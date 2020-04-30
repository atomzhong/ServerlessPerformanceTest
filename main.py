# -*- coding: utf-8 -*-
import time
from common.invoke_model import hotInvoke, coldInvoke, durationInvoke
from common.utils import getLogger, setResultDataToFile
from config.config import RESULT_DATA_PATH

from common.clients.qcloud_client import QcloudClient
from common.clients.aliyun_client import AliClient
from common.clients.aws_client import AwsClient


if __name__ == '__main__':
    _time = str(int(time.time()))
    filename = (RESULT_DATA_PATH % _time)
    logger = getLogger()
    logger.info('Result data file in: %s' % filename)
    dataFile = open(RESULT_DATA_PATH, 'w')

    for client in [
        AliClient(),
        AwsClient(),
        QcloudClient()
    ]:
        # 普通函数
        setResultDataToFile(dataFile, hotInvoke, client, isVpc=False)
        setResultDataToFile(dataFile, coldInvoke, client, isVpc=False)
        # vpc函数场景
        # VPC函数热启动和普通函数热启动无区别，这里仅收录冷启动数据
        setResultDataToFile(dataFile, coldInvoke, client, isVpc=True)

        # 场景执行测试，区分为计算型、IO内存型、网络型、基础型
        for it in [BASCI_LOGGING_CODE, BASIC_PRINT_CODE, NET_CODE, FILE_IO_CODE, FILE_RANDOM_IO_CODE, COMPUTE_CODE]:
            setResultDataToFile(dataFile, duration_invoke, client, invokeType=it)
