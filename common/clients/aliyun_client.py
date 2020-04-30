# -*- coding: utf-8 -*-
import time, datetime, json, sys, os, zipfile, base64
import fc2

from config.config import REGION, ALI_USER_ID, ALI_ACCESSKEY_ID, ALI_ACCESSKEY_KEY, ALI_NORMAL_SERVICE, ALI_VPC_SERVICE, ALI_ENDPOINT_MODEL, BASCI_LOGGING_CODE, INVOKE_HANDLER,ALI_NAME

from config.code import CODE

from common.utils import getLogger, getCodeZip

class AliClient:
    def __init__(self):
        self.name = ALI_NAME
        self.region = REGION
        self.servicename = ALI_NORMAL_SERVICE
        self.logger = getLogger()
        self.logger.info("Init ALIYUN Client...\n")
        self.logger.info("The region is: %s\n" % self.region)
        self.logger.info("The user id is: %s\n" % ALI_USER_ID)
        self.logger.info("The secert info:")
        self.logger.info("AccessKey ID: %s" % (ALI_ACCESSKEY_ID[0:5] + "******"))
        self.logger.info("Access Key Secret: %s\n" % (ALI_ACCESSKEY_KEY[0:5] + "******"))
        endpoint = ALI_ENDPOINT_MODEL % (ALI_USER_ID, self.region)
        self.logger.info("The request endpoint is: %s\n" % endpoint)
        self.client = fc2.Client(
            endpoint = endpoint,
            accessKeyID = ALI_ACCESSKEY_ID,
            accessKeySecret = ALI_ACCESSKEY_KEY)

        self.logger.info("ALIYUN client init success!\n")

        self.logger.info("Start to get FC Service info...")
        self.logger.info("VPC-SERVICE name is: %s" % ALI_VPC_SERVICE)
        self.logger.info("NORMAL-SERVICE name is: %s\n" % ALI_NORMAL_SERVICE)


    def invokeFunction(self, functionname, servicename=None):
        if servicename is None:
            servicename = self.servicename
        ret = self.client.invoke_function(servicename, functionname)
        return ret

    def createFunction(self, functionname, invokeType, isVpc=False):

        zipname = getCodeZip(invokeType)
        if isVpc:
            self.logger.info("create vpc [%s] function\n" % invokeType)
            ret = self.client.create_function(ALI_VPC_SERVICE, functionname, 'python2.7', INVOKE_HANDLER, codeZipFile=zipname)
            self.servicename = ALI_VPC_SERVICE
        else:
            self.logger.info("create [%s] function\n" % invokeType)
            ret = self.client.create_function(ALI_NORMAL_SERVICE, functionname, 'python2.7', INVOKE_HANDLER, codeZipFile=zipname)
            self.servicename = ALI_NORMAL_SERVICE

        return ret

    def deleteFunction(self, functionname, servicename=None):
        if not servicename:
            servicename = self.servicename
        ret = self.client.delete_function(servicename, functionname)
        return ret

    def deleteFunctionAll(self, servicename=None):
        if not servicename:
            servicename = self.servicename
        # ret = self.client.delete_function(servicename, functionname)
        ret = self.client.list_functions(servicename, limit=20)
        for function in ret.data["functions"]:
            self.logger.info("delete function:%s->%s\n" % (servicename, function["functionName"]))
            ret = self.client.delete_function(servicename, function["functionName"])
        return ret

    def invokeFunctionGetDuration(self, functionname, servicename=None):
        if not servicename:
            servicename = self.servicename
        ret = self.client.invoke_function(servicename, functionname)
        return ret, ret.headers['x-fc-invocation-duration'], ret.headers['X-Fc-Max-Memory-Usage']


if __name__ == '__main__':
    functionName = "test" + str(int(time.time()))
    client = AliClient()
    # client.deleteFunctionAll(ALI_NORMAL_SERVICE)
    client.logger.info("开始创建函数...")
    client.createFunction(functionName, BASCI_LOGGING_CODE)
    client.logger.info("开始调用函数...")
    resp, duration, mem_usage = client.invokeFunctionGetDuration(functionName)
    client.logger.info("调用返回：%s" % resp.data)
    client.logger.info("调用时长：%s" % duration)
    client.logger.info("运行时内存：%s\n" % mem_usage)

    client.logger.info("开始删除函数...")
    resp = client.deleteFunction(functionName)
    client.logger.info("删除成功！")
