# -*- coding: utf-8 -*-
import time,os
from common.invoke_model import Invoker
from common.utils import getLogger, setResultDataToFile
from config.config import RESULT_DATA_PATH, NUMBER_OF_INVOKES, NUMBER_HOT_WARM_UP_INVOKES, BASCI_LOGGING_CODE, BASIC_PRINT_CODE, NET_CODE, FILE_IO_CODE, FILE_RANDOM_IO_CODE, COMPUTE_CODE

from common.clients.qcloud_client import QcloudClient
from common.clients.aliyun_client import AliClient
from common.clients.aws_client import AwsClient


if __name__ == '__main__':
    logger = getLogger()
    _time = str(int(time.time()))
    if os.path.exists(RESULT_DATA_PATH):
        logger.info("备份数据文件...\n")

        filename = (RESULT_DATA_PATH + ".bak." + _time)
        os.rename(RESULT_DATA_PATH, filename)


    logger.info('Result data file in: %s' % RESULT_DATA_PATH)
    dataFile = open(RESULT_DATA_PATH, 'w')

    for client in [
        AliClient(),
        AwsClient(),
        QcloudClient()
    ]:
        invoker = Invoker(invokeClient=client, count=NUMBER_OF_INVOKES)
        # 普通函数
        setResultDataToFile(dataFile, invoker.hotInvoke, isVpc=False, warmUpCount=NUMBER_HOT_WARM_UP_INVOKES)
        setResultDataToFile(dataFile, invoker.coldInvoke, isVpc=False)
        # vpc函数场景
        # VPC函数热启动和普通函数热启动无区别，这里仅收录冷启动数据
        setResultDataToFile(dataFile, invoker.coldInvoke, isVpc=True)

        # 场景执行测试，区分为计算型、IO内存型、网络型、基础型
        for it in [
            BASCI_LOGGING_CODE,
            BASIC_PRINT_CODE,
            NET_CODE,
            FILE_IO_CODE,
            FILE_RANDOM_IO_CODE,
            COMPUTE_CODE
        ]:
            setResultDataToFile(dataFile, invoker.scenesInvoke, scenesType=it)

