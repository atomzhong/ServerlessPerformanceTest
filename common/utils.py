# -*- coding: utf-8 -*-

import logging, time, os, base64, datetime
from StringIO import StringIO
from zipfile import ZipFile
from config.config import LOG_PATH, CODEZIP_PATH, INDEX_FLIE, LOG_LEVEL, HOT_INVOKE, COLD_INVOKE, SCENES_INVOKE, VPC_COLD_INVOKE, BASCI_LOGGING_CODE, BASIC_PRINT_CODE, NET_CODE, FILE_IO_CODE, FILE_RANDOM_IO_CODE, COMPUTE_CODE, RESULT_PNG_PATH
from config.code import CODE

# import matplotlib.pyplot as plt


def getLogger():

    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    if not logger.handlers:
        _time = time.strftime("%Y-%m-%d", time.localtime())
        fileHandler = logging.FileHandler(LOG_PATH % _time, mode='a')
        fileHandler.setLevel(logging.DEBUG)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s %(pathname)s %(funcName)s %(lineno)s %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
        fileHandler.setFormatter(formatter)
        consoleHandler.setFormatter(formatter)

        logger.addHandler(fileHandler)
        logger.addHandler(consoleHandler)

    return logger

# 打包后返回文件路径，用于aliyun
def getCodeZip(invokeType):
    filename = CODEZIP_PATH % INDEX_FLIE
    zipname = CODEZIP_PATH % invokeType + '.zip'

    logger = getLogger()
    # 若未创建有对应zip包
    logger.info("开始创建代码zip包...\n")
    if not os.path.exists(zipname):
        logger.info("无对应场景函数代码包，开始创建...\n")
        if os.path.exists(filename):
            logger.info("移除重名index文件...\n")
            os.remove(filename)

        ali_temp_file = open(filename, 'w')
        ali_temp_file.write(CODE[invokeType])
        ali_temp_file.close()
        zip = ZipFile(zipname, 'a')
        os.chdir(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))) + os.path.sep + "code_zip" + os.path.sep)
        zip.write(INDEX_FLIE)
        zip.close()
        logger.info("创建成功！\n")
    else:
        logger.info("对应场景函数代码包已存在。\n")
    logger.info("ZIP：%s\n" % zipname)
    return zipname

# 打包后返回字节流，用于aws
def getCodeBuf(invokeType):
    filename = CODEZIP_PATH % INDEX_FLIE
    zipname = CODEZIP_PATH % invokeType + '.zip'

    logger = getLogger()

    if os.path.exists(filename):
        logger.info("移除重名index文件...\n")
        os.remove(filename)

    aws_temp_file = open(filename, 'w')
    aws_temp_file.write(CODE[invokeType])
    aws_temp_file.close()

    buf = StringIO()
    with ZipFile(buf, 'w') as z:
        os.chdir(os.path.abspath(os.path.dirname(
            os.path.abspath(os.path.dirname(os.path.abspath(__file__))))) + os.path.sep + "code_zip" + os.path.sep)
        z.write(INDEX_FLIE)
    buf.seek(0)
    return buf.read()

# 打包后返回base64编码，用于腾讯云
def getCodeBase64(invokeType):
    filename = CODEZIP_PATH % INDEX_FLIE
    zipname = CODEZIP_PATH % invokeType + '.zip'

    logger = getLogger()
    # 若未创建有对应zip包
    logger.info("开始创建代码zip包...\n")
    if not os.path.exists(zipname):
        logger.info("无对应场景函数代码包，开始创建...\n")
        if os.path.exists(filename):
            logger.info("移除重名index文件...\n")
            os.remove(filename)

        ali_temp_file = open(filename, 'w')
        ali_temp_file.write(CODE[invokeType])
        ali_temp_file.close()
        zip = ZipFile(zipname, 'a')
        os.chdir(os.path.abspath(os.path.dirname(
            os.path.abspath(os.path.dirname(os.path.abspath(__file__))))) + os.path.sep + "code_zip" + os.path.sep)
        zip.write(INDEX_FLIE)
        zip.close()
        logger.info("创建成功！\n")
    else:
        logger.info("对应场景函数代码包已存在。\n")

    with open(zipname, 'rb') as fp:
        return base64.b64encode(fp.read())

# 获取函数执行时间
def getResAndTimeInterval(func, *args, **kwargs):
    begin = datetime.datetime.now()
    res = func(*args, **kwargs)
    end = datetime.datetime.now()
    cost = end - begin
    interval = float(cost.total_seconds()) * 1000

    return res, interval

# 将测试数据写入文件
def setResultDataToFile(file, func, *args, **kwargs):
    if func.__name__ == "durationInvoke":
        data, data_average, mem_data, mem_data_average = func(*args, **kwargs)
        file.write(data)
        file.write('\n\n')
        file.write(data_average)
        file.write('\n\n')
        file.write(mem_data)
        file.write('\n\n')
        file.write(mem_data_average)
        file.write('\n\n')
        return data, data_average, mem_data, mem_data_average
    else:
        data, data_average = func(*args, **kwargs)
        file.write(data)
        file.write('\n\n')
        file.write(data_average)
        file.write('\n\n')
        return data, data_average

# 绘制单张折线图
def getResultJPG(title, ali_data,aws_data,qcc_data, ali_data_ave,aws_data_ave,qcc_data_ave, filename):

    x = range(1, 101)

    plt.plot(x, ali_data, color="r", linestyle="-", linewidth=1, label="aliyun,average=%s" % ali_data_ave)
    plt.plot(x, aws_data, color="g", linestyle="-", linewidth=1, label="aws,average=%s" % aws_data_ave)
    plt.plot(x, qcc_data, color="b", linestyle="-", linewidth=1, label="tencent,average=%s" % qcc_data_ave)

    plt.legend(loc='upper left', bbox_to_anchor=(0.2, 0.95))
    plt.xlabel("number_of_invokes")
    plt.ylabel("invoke_duration(ms)")
    plt.title(title)
    plt.grid(color="k", linestyle=":", axis="y")
    plt.savefig(filename, dpi=100)

# 绘制两张折线子图拼接
def getDoubleResultJPG(title,
                       ali_data, aws_data, qcc_data, ali_data_ave, aws_data_ave, qcc_data_ave,
                       ali_data2, aws_data2, qcc_data2, ali_data_ave2, aws_data_ave2, qcc_data_ave2,
                       filename):
    x = range(1, 101)

    plt.figure(1)
    plt.subplot(1, 2, 1)
    plt.plot(x, ali_data, color="r", linestyle="-", linewidth=1, label="aliyun,average=%s" % ali_data_ave)
    plt.plot(x, aws_data, color="g", linestyle="-", linewidth=1, label="aws,average=%s" % aws_data_ave)
    plt.plot(x, qcc_data, color="b", linestyle="-", linewidth=1, label="tencent,average=%s" % qcc_data_ave)

    plt.legend(loc='upper left', bbox_to_anchor=(0.2, 0.95))
    plt.xlabel("number_of_invokes")
    plt.ylabel("duration(ms)")
    plt.title(title)
    plt.grid(color="k", linestyle=":", axis="y")

    plt.figure(1)
    plt.subplot(1, 2, 2)
    plt.plot(x, ali_data2, color="r", linestyle="-", linewidth=1, label="aliyun,average=%s" % ali_data_ave2)
    plt.plot(x, aws_data2, color="g", linestyle="-", linewidth=1, label="aws,average=%s" % aws_data_ave2)
    plt.plot(x, qcc_data2, color="b", linestyle="-", linewidth=1, label="tencent,average=%s" % qcc_data_ave2)

    plt.legend(loc='upper left', bbox_to_anchor=(0.2, 0.95))
    plt.xlabel("number_of_invokes")
    plt.ylabel("memory_used(mb)")
    plt.title(title)
    plt.grid(color="k", linestyle=":", axis="y")

    plt.savefig(filename, dpi=100)



if __name__ == '__main__':
    from result.data import *

    pngname = (RESULT_PNG_PATH % (HOT_INVOKE, _time))
    getResultJPG(SCENES_INVOKE, aliyun_hot, aws_hot, qcloud_hot, aliyun_hot_average, aws_hot_average,
                 qcloud_hot_average, pngname)

    pngname = (RESULT_PNG_PATH % (COLD_INVOKE, _time))
    getResultJPG(SCENES_INVOKE, aliyun_cold, aws_cold, qcloud_cold, aliyun_cold_average, aws_cold_average,
                 qcloud_cold_average, pngname)

    pngname = (RESULT_PNG_PATH % ((SCENES_INVOKE + BASCI_LOGGING_CODE), _time))
    getDoubleResultJPG((SCENES_INVOKE + BASCI_LOGGING_CODE),
                       aliyun_BASCI_LOGGING_CODE_duration, aws_BASCI_LOGGING_CODE_duration,
                       qcloud_BASCI_LOGGING_CODE_duration, aliyun_BASCI_LOGGING_CODE_duration_average,
                       aws_BASCI_LOGGING_CODE_duration_average, qcloud_BASCI_LOGGING_CODE_duration_average,

                       aliyun_BASCI_LOGGING_CODE_memused, aws_BASCI_LOGGING_CODE_memused,
                       qcloud_BASCI_LOGGING_CODE_memused, aliyun_BASCI_LOGGING_CODE_memused_average,
                       aws_BASCI_LOGGING_CODE_memused_average, qcloud_BASCI_LOGGING_CODE_memused_average,
                       pngname)

    pngname = (RESULT_PNG_PATH % ((SCENES_INVOKE + BASIC_PRINT_CODE), _time))
    getDoubleResultJPG((SCENES_INVOKE + BASIC_PRINT_CODE),
                       aliyun_BASIC_PRINT_CODE_duration, aws_BASIC_PRINT_CODE_duration,
                       qcloud_BASIC_PRINT_CODE_duration, aliyun_BASIC_PRINT_CODE_duration_average,
                       aws_BASIC_PRINT_CODE_duration_average, qcloud_BASIC_PRINT_CODE_duration_average,

                       aliyun_BASIC_PRINT_CODE_memused, aws_BASIC_PRINT_CODE_memused,
                       qcloud_BASIC_PRINT_CODE_memused, aliyun_BASIC_PRINT_CODE_memused_average,
                       aws_BASIC_PRINT_CODE_memused_average, qcloud_BASIC_PRINT_CODE_memused_average,
                       pngname)

    getDoubleResultJPG((SCENES_INVOKE + NET_CODE),
                       aliyun_NET_CODE_duration, aws_NET_CODE_duration,
                       qcloud_NET_CODE_duration, aliyun_NET_CODE_duration_average,
                       aws_NET_CODE_duration_average, qcloud_NET_CODE_duration_average,

                       aliyun_NET_CODE_memused, aws_NET_CODE_memused,
                       qcloud_NET_CODE_memused, aliyun_NET_CODE_memused_average,
                       aws_NET_CODE_memused_average, qcloud_NET_CODE_memused_average,
                       pngname)

    getDoubleResultJPG((SCENES_INVOKE + FILE_IO_CODE),
                       aliyun_FILE_IO_CODE_duration, aws_FILE_IO_CODE_duration,
                       qcloud_FILE_IO_CODE_duration, aliyun_FILE_IO_CODE_duration_average,
                       aws_FILE_IO_CODE_duration_average, qcloud_FILE_IO_CODE_duration_average,

                       aliyun_FILE_IO_CODE_memused, aws_FILE_IO_CODE_memused,
                       qcloud_FILE_IO_CODE_memused, aliyun_FILE_IO_CODE_memused_average,
                       aws_FILE_IO_CODE_memused_average, qcloud_FILE_IO_CODE_memused_average,
                       pngname)

    getDoubleResultJPG((SCENES_INVOKE + FILE_RANDOM_IO_CODE),
                       aliyun_FILE_RANDOM_IO_CODE_duration, aws_FILE_RANDOM_IO_CODE_duration,
                       qcloud_FILE_RANDOM_IO_CODE_duration, aliyun_FILE_RANDOM_IO_CODE_duration_average,
                       aws_FILE_RANDOM_IO_CODE_duration_average, qcloud_FILE_RANDOM_IO_CODE_duration_average,

                       aliyun_FILE_RANDOM_IO_CODE_memused, aws_FILE_RANDOM_IO_CODE_memused,
                       qcloud_FILE_RANDOM_IO_CODE_memused, aliyun_FILE_RANDOM_IO_CODE_memused_average,
                       aws_FILE_RANDOM_IO_CODE_memused_average, qcloud_FILE_RANDOM_IO_CODE_memused_average,
                       pngname)

    getDoubleResultJPG((SCENES_INVOKE + COMPUTE_CODE),
                       aliyun_COMPUTE_CODE_duration, aws_COMPUTE_CODE_duration,
                       qcloud_COMPUTE_CODE_duration, aliyun_COMPUTE_CODE_duration_average,
                       aws_COMPUTE_CODE_duration_average, qcloud_COMPUTE_CODE_duration_average,

                       aliyun_COMPUTE_CODE_memused, aws_COMPUTE_CODE_memused,
                       qcloud_COMPUTE_CODE_memused, aliyun_COMPUTE_CODE_memused_average,
                       aws_COMPUTE_CODE_memused_average, qcloud_COMPUTE_CODE_memused_average,
                       pngname)