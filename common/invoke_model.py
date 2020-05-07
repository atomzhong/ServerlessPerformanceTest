# -*- coding: utf-8 -*-
import time, datetime, sys
from common.utils import getLogger, getResAndTimeInterval
from common.clients.qcloud_client import QcloudClient
from common.clients.aliyun_client import AliClient
from common.clients.aws_client import AwsClient
from config.config import BASCI_LOGGING_CODE, FUNCTION_NAME, QC_NAME, AWS_NAME

class Invoker:
    def __init__(self, invokeClient, count):

        self.invokeClient = invokeClient
        self.count = count

        self.logger = getLogger()

    # 热调用，仅创建一次函数，间隔1s连续调用150次，前50次调用为预热阶段，取后100次调用数据
    def hotInvoke(self, warmUpCount=None, isVpc=None):
        data = []
        timeSum = 0

        self.logger.info('start create function')
        functionName = FUNCTION_NAME + str(int(time.time()))
        self.logger.info('create resp:%s' % self.invokeClient.createFunction(functionName, BASCI_LOGGING_CODE, isVpc=isVpc))

        self.logger.info('start hot invoke')
        for i in xrange((self.count + warmUpCount)):
            res, interval = getResAndTimeInterval(self.invokeClient.invokeFunction, functionName)
            self.logger.info("当前调用次数：[%s]" % i)
            self.logger.info("invoke time is: %s" % interval)
            self.logger.info("invoke res is: %s" % res)
            if i >= warmUpCount:
                data.append(interval)
                timeSum += interval
            time.sleep(1)

        self.logger.info('all data:%s' % data)
        self.logger.info('average time:%s' % str(timeSum / self.count))

        self.logger.info('start delete function')
        response = self.invokeClient.deleteFunction(functionName)
        self.logger.info("delete res is: %s" % response)

        if isVpc:
            data = "%s_vpc_hot = %s" % (self.invokeClient.name, data)
            data_average = "%s_vpc_hot_average = %s" % (self.invokeClient.name, str(timeSum / self.count))
        else:
            data = "%s_hot = %s" % (self.invokeClient.name, data)
            data_average = "%s_hot_average = %s" % (self.invokeClient.name, str(timeSum / self.count))

        return data, data_average

    # 冷调用，每次调用都会重新创建函数，间隔1s连续调用100次，无预热阶段
    def coldInvoke(self, isVpc=None):
        data = []
        timeSum = 0
        first_functionName = ""

        self.logger.info('start cold invoke')
        for i in xrange(self.count):
            self.logger.info('start create function')
            functionName = FUNCTION_NAME + str(int(time.time()))
            self.logger.info('create resp:%s' % self.invokeClient.createFunction(functionName, BASCI_LOGGING_CODE, isVpc=isVpc))

            # 模拟用户行为，创建完后不会立刻调用
            time.sleep(5)

            res, interval = getResAndTimeInterval(self.invokeClient.invokeFunction, functionName)
            self.logger.info("当前调用次数：[%s]" % i)
            self.logger.info("invoke time is: %s" % interval)
            self.logger.info("invoke res is: %s" % res)
            data.append(interval)
            timeSum += interval

            if isVpc and self.invokeClient.name in [QC_NAME,AWS_NAME] and i == 0:
                self.logger.info("Do not delete the first qcloud/aws vpc function.")
                first_functionName = functionName
                time.sleep(30)
                continue

            self.logger.info('start delete function')
            response = self.invokeClient.deleteFunction(functionName)
            self.logger.info("delete res is: %s" % response)

            time.sleep(1)

        if isVpc and self.invokeClient.name == QC_NAME:
            self.logger.info('start delete qcloud/aws first vpc function')
            response = self.invokeClient.deleteFunction(first_functionName)
            self.logger.info("delete res is: %s" % response)

        self.logger.info('all data:%s' % data)
        self.logger.info('average time:%s' % str(timeSum / self.count))

        if isVpc:
            data = "%s_vpc_cold = %s" % (self.invokeClient.name, data)
            data_average = "%s_vpc_cold_average = %s" % (self.invokeClient.name, str(timeSum / self.count))
        else:
            data = "%s_cold = %s" % (self.invokeClient.name, data)
            data_average = "%s_cold_average = %s" % (self.invokeClient.name, str(timeSum / self.count))

        return data, data_average

    # 各类函数场景的热调用，但统计函数执行回包中的执行时间和运行时内存，不进行预热
    def scenesInvoke(self, scenesType=None):
        data = []
        memData = []

        timeSum = 0
        memSum = 0

        self.logger.info('start create function')
        functionName = FUNCTION_NAME + str(int(time.time()))
        self.logger.info('create resp:%s' % self.invokeClient.createFunction(functionName, scenesType))
        time.sleep(10)

        self.logger.info('start scenes invoke')
        for i in xrange(self.count):
            res, duration, memUsed = self.invokeClient.invokeFunctionGetDuration(functionName)
            self.logger.info("当前调用次数：[%s]" % i)
            self.logger.info("duration time is: %s" % duration)
            self.logger.info("memory used is: %s" % memUsed)

            data.append(float(duration))
            memData.append(float(memUsed))

            timeSum += float(duration)
            memSum += float(memUsed)
            time.sleep(1)

        self.logger.info('all data:%s' % data)
        self.logger.info('all memory data:%s' % memData)
        self.logger.info('average time:%s' % str(timeSum / self.count))
        self.logger.info('average mem:%s' % str(memSum / self.count))

        self.logger.info('start delete function')
        response = self.invokeClient.deleteFunction(functionName)
        self.logger.info("delete res is: %s" % response)

        self.logger.info('start write data file')
        data = "%s_%s_duration = %s" % (self.invokeClient.name, scenesType, data)
        data_average = "%s_%s_duration_average = %s" % (self.invokeClient.name, scenesType, str(timeSum / self.count))

        mem_data = "%s_%s_memused = %s" % (self.invokeClient.name, scenesType, memData)
        mem_data_average = "%s_%s_memused_average = %s" % (self.invokeClient.name, scenesType, str(memSum / self.count))

        return data, data_average, mem_data, mem_data_average


if __name__ == '__main__':
    client = QcloudClient()
    # client = AliClient()
    # client = AwsClient()

    invoker = Invoker(client, 10)

    data, data_average = invoker.hotInvoke(isVpc=False, warmUpCount=3)
    invoker.logger.info("热调用全量数据：%s\n" % data)
    invoker.logger.info("热调用均值数据：%s\n" % data_average)

    data, data_average = invoker.coldInvoke(isVpc=False)
    invoker.logger.info("冷调用全量数据：%s\n" % data)
    invoker.logger.info("冷调用均值数据：%s\n" % data_average)

    data, data_average = invoker.coldInvoke(isVpc=True)
    invoker.logger.info("VPC冷调用全量数据：%s\n" % data)
    invoker.logger.info("VPC冷调用均值数据：%s\n" % data_average)

    data, data_average, mem_data, mem_data_average = invoker.scenesInvoke(BASCI_LOGGING_CODE)
    invoker.logger.info("场景调用时间全量数据：%s\n" % data)
    invoker.logger.info("场景调用时间均值数据：%s\n" % data_average)
    invoker.logger.info("场景调用运行时内存全量数据：%s\n" % mem_data)
    invoker.logger.info("场景调用运行时均值数据：%s\n" % mem_data_average)