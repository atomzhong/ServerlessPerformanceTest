# -*- coding: utf-8 -*-

import logging, time, os, base64, datetime
from StringIO import StringIO
from zipfile import ZipFile
from config.config import LOG_PATH, CODEZIP_PATH, INDEX_FLIE, LOG_LEVEL
from config.code import CODE


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
        file.write(mem_data)
        file.write('\n\n')
        file.write(mem_data_average)
        file.write('\n\n')
    else:
        data, data_average = func(*args, **kwargs)
    file.write(data)
    file.write('\n\n')
    file.write(data_average)
    file.write('\n\n')