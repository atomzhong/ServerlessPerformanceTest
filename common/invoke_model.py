# -*- coding: utf-8 -*-
import time, datetime, sys
from common.utils import getLogger, getResAndTimeInterval
from common.clients.qcloud_client import QcloudClient
from common.clients.aliyun_client import AliClient
from common.clients.aws_client import AwsClient
from config.config import BASCI_LOGGING_CODE, FUNCTION_NAME

# 热调用，仅创建一次函数，间隔1s连续调用150次，前50次调用为预热阶段，取后100次调用数据
def hotInvoke(client, isVpc=False, count=150, warmUpCount=50):
    data = []
    timeSum = 0

    logger = getLogger()
    logger.info('start create function')
    functionName = FUNCTION_NAME + str(int(time.time()))
    logger.info('create resp:%s' % client.createFunction(functionName, BASCI_LOGGING_CODE))

    logger.info('start hot invoke')
    for i in xrange(count):
        res, interval = getResAndTimeInterval(client.invokeFunction, functionName)
        logger.info("invoke time is: %s" % interval)
        logger.info("invoke res is: %s" % res)
        if i >= warmUpCount:
            data.append(interval)
            timeSum += interval
        time.sleep(1)

    logger.info('all data:%s' % data)
    logger.info('average time:%s' % str(timeSum / (count-warmUpCount)))

    logger.info('start delete function')
    response = client.deleteFunction(functionName)
    logger.info("delete res is: %s" % response)

    if isVpc:
        data = "%s_vpc_hot = %s" % (client.name, data)
        data_average = "%s_vpc_hot_average = %s" % (client.name, str(timeSum / (count-warmUpCount)))
    else:
        data = "%s_hot = %s" % (client.name, data)
        data_average = "%s_hot_average = %s" % (client.name, str(timeSum / (count-warmUpCount)))

    return data, data_average

# 冷调用，每次调用都会重新创建函数，间隔1s连续调用100次，无预热阶段
def coldInvoke(client, isVpc=False, count=100):
    data = []
    timeSum = 0
    first_functionName = ""
    logger = getLogger()
    logger.info('start cold invoke')
    for i in xrange(count):
        logger.info('start create function')
        functionName = FUNCTION_NAME + str(int(time.time()))
        logger.info('create resp:%s' % client.createFunction(functionName, BASCI_LOGGING_CODE))

        # 模拟用户行为，创建完后不会立刻调用
        time.sleep(5)

        res, interval = getResAndTimeInterval(client.invokeFunction, functionName)
        logger.info("invoke time is: %s" % interval)
        logger.info("invoke res is: %s" % res)
        data.append(interval)
        timeSum += interval

        if isVpc and client.name == "qcloud" and i == 0:
            logger.info("Do not delete the first qcloud vpc function.")
            first_functionName = functionName
            time.sleep(30)
            continue

        logger.info('start delete function')
        response = client.deleteFunction(functionName)
        logger.info("delete res is: %s" % response)

        time.sleep(1)

    if isVpc and client.name == "qcloud":
        logger.info('start delete qcloud first vpc function')
        response = client.deleteFunction(first_functionName)
        logger.info("delete res is: %s" % response)

    logger.info('all data:%s' % data)
    logger.info('average time:%s' % str(timeSum / count))

    if isVpc:
        data = "%s_vpc_cold = %s" % (client.name, data)
        data_average = "%s_vpc_cold_average = %s" % (client.name, str(timeSum / count))
    else:
        data = "%s_cold = %s" % (client.name, data)
        data_average = "%s_cold_average = %s" % (client.name, str(timeSum / count))

    return data, data_average

# 热调用，但统计函数执行回包中的执行时间和运行时内存，用于函数场景类型调用
def durationInvoke(client, invokeType, count=100):
    data = []
    memData = []

    timeSum = 0
    memSum = 0
    logger = getLogger()
    logger.info('start create function')
    functionName = FUNCTION_NAME + str(int(time.time()))
    logger.info('create resp:%s' % client.createFunction(functionName, invokeType))
    time.sleep(10)

    logger.info('start duration invoke')
    for i in xrange(count):
        res, duration, memUsed = client.invokeFunctionGetDuration(functionName)
        logger.info("duration time is: %s" % duration)
        logger.info("memory used is: %s" % memUsed)

        data.append(float(duration))
        memData.append(float(memUsed))

        timeSum += float(duration)
        memSum += float(memUsed)
        time.sleep(1)

    logger.info('all data:%s' % data)
    logger.info('all memory data:%s' % memData)
    logger.info('average time:%s' % str(timeSum / count))
    logger.info('average mem:%s' % str(memSum / count))

    logger.info('start delete function')
    response = client.deleteFunction(functionName)
    logger.info("delete res is: %s" % response)

    logger.info('start write data file')
    data = "%s_%s_duration = %s" % (client.name, invokeType, data)
    data_average = "%s_%s_duration_average = %s" % (client.name, invokeType, str(timeSum / count))

    mem_data = "%s_%s_memUsed = %s" % (client.name, invokeType, memData)
    mem_data_average = "%s_%s_memUsed_average = %s" % (client.name, invokeType, str(memSum / count))

    return data, data_average, mem_data, mem_data_average


if __name__ == '__main__':
    # client = QcloudClient()
    # client = AliClient()
    client = AwsClient()

    data, data_average = hotInvoke(client, isVpc=False, count=10, warmUpCount=3)
    client.logger.info("热调用全量数据：%s\n" % data)
    client.logger.info("热调用均值数据：%s\n" % data_average)

    data, data_average = coldInvoke(client, isVpc=False, count=10)
    client.logger.info("冷调用全量数据：%s\n" % data)
    client.logger.info("冷调用均值数据：%s\n" % data_average)

    data, data_average = coldInvoke(client, isVpc=True, count=10)
    client.logger.info("VPC冷调用全量数据：%s\n" % data)
    client.logger.info("VPC冷调用均值数据：%s\n" % data_average)

    data, data_average, mem_data, mem_data_average = durationInvoke(client, BASCI_LOGGING_CODE, count=10)
    client.logger.info("场景调用时间全量数据：%s\n" % data)
    client.logger.info("场景调用时间均值数据：%s\n" % data_average)
    client.logger.info("场景调用运行时内存全量数据：%s\n" % mem_data)
    client.logger.info("场景调用运行时均值数据：%s\n" % mem_data_average)