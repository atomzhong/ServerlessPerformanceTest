# -*- coding: utf-8 -*-
import time, datetime, json, sys, os, zipfile, base64
import boto3

from config.config import AWS_REGION, AWS_PRODUCT_NAME, AWS_ACCESSKEY_ID, AWS_ACCESSKEY_KEY, AWS_LAMBDA_ROLE, BASCI_LOGGING_CODE, INVOKE_HANDLER,AWS_NAME, AWS_VPC_CONF

from config.code import CODE

from common.utils import getLogger, getCodeBuf


class AwsClient:
    def __init__(self):
        self.name = AWS_NAME
        self.region = AWS_REGION
        self.logger = getLogger()
        self.logger.info("Init AWS Client...\n")
        self.logger.info("The region is: %s\n" % self.region)
        self.logger.info("The secert info:")
        self.logger.info("AccessKey ID: %s" % (AWS_ACCESSKEY_ID[0:5] + "******"))
        self.logger.info("Access Key Secret: %s\n" % (AWS_ACCESSKEY_KEY[0:5] + "******"))
        self.client = boto3.client(AWS_PRODUCT_NAME,
                                   region_name = self.region,
                                   aws_access_key_id = AWS_ACCESSKEY_ID,
                                   aws_secret_access_key = AWS_ACCESSKEY_KEY)

        self.logger.info("AWS client init success!\n")

    def invokeFunction(self, functionname):
        ret = self.client.invoke(FunctionName=functionname)
        return ret

    def createFunction(self, functionname, invokeType, isVpc=False):
        code_zip_buf = getCodeBuf(invokeType)

        if isVpc:
            self.logger.info("create vpc [%s] function\n" % invokeType)
            response = self.client.create_function(FunctionName=functionname, Runtime='python2.7', Role=AWS_LAMBDA_ROLE, MemorySize=256, Handler="index.handler", Timeout=10, TracingConfig={"Mode": "PassThrough"}, Code={"ZipFile": code_zip_buf}, VpcConfig=aws_vpc_config)
        else:
            self.logger.info("create [%s] function\n" % invokeType)
            response = self.client.create_function(FunctionName=functionname, Runtime='python2.7', Role=AWS_LAMBDA_ROLE, MemorySize=256, Handler="index.handler", Timeout=10, TracingConfig={"Mode": "PassThrough"}, Code={"ZipFile": code_zip_buf})

        start_time = time.time()
        while time.time() - start_time < 3000:
            resp = self.client.get_function(FunctionName=functionname)

            if resp['Configuration']['State'] == "Active":
                self.logger.info("恭喜!函数处于可用状态[%s]\n" % str(resp['Configuration']['State']))
                return resp
            elif "ing" in resp['Configuration']['State']:
                self.logger.info("函数处于不可用状态[%s]，再次查询状态...\n" % str(resp['Configuration']['State']))
                time.sleep(2)
            elif "Failed" in resp['Configuration']['State']:
                self.logger.info("函数操作失败[%s]\n" % str(resp['Configuration']['State']))
                raise RuntimeError('Create Function Error!')
            else:
                self.logger.info("函数处于未知状态[%s]\n" % str(resp['Configuration']['State']))
                raise RuntimeError('Create Function Error!')

        return response

    def deleteFunction(self, functionname):
        ret = self.client.delete_function(FunctionName=functionname)
        return ret

    def invokeFunctionGetDuration(self, functionname):
        response = self.client.invoke(FunctionName=functionname, InvocationType='RequestResponse', LogType='Tail')
        self.logger.info(str(base64.b64decode(response["LogResult"])))
        start = str(base64.b64decode(response["LogResult"])).find('Used')
        end = str(base64.b64decode(response["LogResult"])).find('MB', start)
        memUsed = str(base64.b64decode(response["LogResult"]))[start + 6:end]

        start = str(base64.b64decode(response["LogResult"])).find('Duration')
        end = str(base64.b64decode(response["LogResult"])).find('ms', start)
        duration = str(base64.b64decode(response["LogResult"]))[start + 10:end]
        return response, duration, memUsed


if __name__ == '__main__':
    functionName = "test" + str(int(time.time()))
    client = AwsClient()
    client.logger.info("开始创建函数...")
    client.createFunction(functionName, BASCI_LOGGING_CODE)
    client.logger.info("开始调用函数...")
    resp, duration, mem_usage = client.invokeFunctionGetDuration(functionName)
    client.logger.info("调用返回：%s" % resp)
    client.logger.info("调用时长：%s" % duration)
    client.logger.info("运行时内存：%s\n" % mem_usage)

    client.logger.info("开始删除函数...")
    resp = client.deleteFunction(functionName)
    client.logger.info("删除成功！")