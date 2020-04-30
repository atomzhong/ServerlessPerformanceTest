# -*- coding: utf-8 -*-
import time, datetime, json, sys, os, zipfile, base64
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.scf.v20180416 import scf_client, models
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

from config.config import REGION, QC_API_ID, QC_API_KEY, QC_VPC, QC_SUBNET, QC_ENDPOINT_MODEL, BASCI_LOGGING_CODE, INVOKE_HANDLER, QC_NAME
from common.utils import getLogger, getCodeBase64

class QcloudClient:
    def __init__(self):
        self.name = QC_NAME
        self.region = REGION
        self.logger = getLogger()
        self.logger.info("Init Qcloud SCF Client...\n")
        self.logger.info("The region is: %s\n" % self.region)
        cred = credential.Credential(QC_API_ID, QC_API_KEY)
        self.logger.info("The secert info:")
        self.logger.info("Secret Id: %s" % (QC_API_ID[0:5]+"******"))
        self.logger.info("Secret Key: %s\n" % (QC_API_KEY[0:5]+"******"))
        httpProfile = HttpProfile()
        httpProfile.reqMethod = "GET"
        httpProfile.reqTimeout = 30
        httpProfile.endpoint = QC_ENDPOINT_MODEL % self.region
        self.logger.info("The request endpoint is: %s\n" % httpProfile.endpoint)
        httpProfile.keepAlive = True

        clientProfile = ClientProfile()

        clientProfile.signMethod = "HmacSHA256"
        clientProfile.httpProfile = httpProfile

        self.client = scf_client.ScfClient(cred, 'ap-' + self.region, clientProfile)

        self.logger.info("SCF client init success!\n")

        self.logger.info("Start to get VPC info...")
        self.logger.info("VPC id is: %s"% QC_VPC)
        self.logger.info("VPC-Subnet id is: %s\n" % QC_SUBNET)

    def invokeFunction(self, functionname, namespace=None):
        params = '''{"FunctionName": "%s"}''' % functionname
        if namespace:
            params = '''{"Namespace":"%s","FunctionName":"%s"}''' % (namespace, functionname)
        invo = models.InvokeRequest()
        invo.from_json_string(params)
        resp = self.client.Invoke(invo)
        return resp

    def createFunction(self, functionname, invokeType, isVpc=False):

        zip64 = getCodeBase64(invokeType)

        if isVpc:
            self.logger.info("create vpc [%s] function\n" % invokeType)
            params = '''{"FunctionName":"%s","Code":{"ZipFile": %s},"Timeout":60,"Handler":"%s","Runtime":"Python2.7","VpcConfig":{"VpcId":"%s","SubnetId":"%s"},"Namespace":"dialtest"}''' % (
            functionname, zip64, INVOKE_HANDLER,self.vpcId, self.subnetId)
        else:
            self.logger.info("create [%s] function\n" % invokeType)
            params = '''{"FunctionName":"%s","Code":{"ZipFile":"%s"},"Timeout":60,"Handler":"%s","Runtime":"Python2.7","Namespace":"dialtest"}''' % (functionname, zip64, INVOKE_HANDLER)

        crea = models.CreateFunctionRequest()
        crea.from_json_string(params)
        resp = self.client.CreateFunction(crea)
        self.logger.info("创建函数返回: %s\n" % resp)

        start_time = time.time()
        while time.time() - start_time < 3000:
            params = '''{"FunctionName":"%s"}''' % functionname
            getf = models.GetFunctionRequest()
            getf.from_json_string(params)
            resp = self.client.GetFunction(getf)

            self.logger.info(resp)
            if resp.Status == "Active":
                self.logger.info("恭喜!函数处于可用状态[%s]\n" % str(resp.Status))
                return resp
            elif "ing" in resp.Status:
                self.logger.info("函数处于不可用状态[%s]，再次查询状态...\n" % str(resp.Status))
                time.sleep(2)
            elif "Failed" in resp.Status:
                self.logger.info("函数操作失败[%s]\n" % str(resp.Status))
                raise RuntimeError('Create Function Error!')
            else:
                self.logger.info("函数处于未知状态[%s]\n" % str(resp.Status))
                raise RuntimeError('Create Function Error!')
        return resp


    def deleteFunction(self, functionname):
        params = '''{"FunctionName": "%s"}''' % functionname
        dele = models.DeleteFunctionRequest()
        dele.from_json_string(params)
        resp = self.client.DeleteFunction(dele)
        return resp

    def invokeFunctionGetDuration(self, functionname):
        params = '''{"FunctionName": "%s"}''' % functionname
        invo = models.InvokeRequest()
        invo.from_json_string(params)
        resp = self.client.Invoke(invo)
        return resp, resp.Result.Duration, float(resp.Result.MemUsage / 1024.00 / 1024.00)


if __name__ == '__main__':
    functionName = "atomtest" + str(int(time.time()))
    client = QcloudClient()
    client.logger.info("开始创建函数...")
    client.createFunction(functionName, BASCI_LOGGING_CODE)

    client.logger.info("开始调用函数...")
    resp, duration, mem_usage = client.invokeFunctionGetDuration(functionName)
    client.logger.info("调用返回：%s" % resp)
    client.logger.info("调用时长：%s" % duration)
    client.logger.info("运行时内存：%s\n" % mem_usage)

    client.logger.info("开始删除函数...")
    resp = client.deleteFunction(functionName)
    client.logger.info("删除函数返回: %s\n" % resp)






