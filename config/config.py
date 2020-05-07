# -*- coding: utf-8 -*-
import os,logging

# 测试过程中创建的函数名
FUNCTION_NAME = "ServerLessTest"

# 结果数据存放目录
RESULT_DATA_PATH = os.path.join((os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))) + os.path.sep + "result" + os.path.sep), "data.py")
RESULT_PNG_PATH = os.path.join((os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))) + os.path.sep + "result" + os.path.sep), "%s_%s.png")


# 日志目录
LOG_PATH = os.path.join((os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))) + os.path.sep + "log" + os.path.sep), "ServerlessPerformance_%s.log")

# 日志等级
LOG_LEVEL = logging.INFO

# 代码zip包目录
CODEZIP_PATH = os.path.join((os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))) + os.path.sep + "code_zip" + os.path.sep), "%s")

# 地域信息
REGION = "hongkong"
AWS_REGION = "ap-east-1" # 香港

# 函数场景
# 基础logging场景
BASCI_LOGGING_CODE = "BASCI_LOGGING_CODE"
# 基础循环print场景
BASIC_PRINT_CODE = "BASIC_PRINT_CODE"
# 外网访问场景
NET_CODE = "NET_CODE"
# 文件顺序读写场景
FILE_IO_CODE = "FILE_IO_CODE"
# 文件随机读写场景
FILE_RANDOM_IO_CODE = "FILE_RANDOM_IO_CODE"
# 浮点数计算场景
COMPUTE_CODE = "COMPUTE_CODE"

# 函数handler
INDEX_FLIE = "index.py"
INVOKE_HANDLER = "index.handler"

# 调用次数设定
# 调用总次数
# 如果为热调用，则调用总次数为100+50=150次，但仅记录后100次调用数据
NUMBER_OF_INVOKES = 100
# 热调用预热调用次数
NUMBER_HOT_WARM_UP_INVOKES = 50

# 调用类型
HOT_INVOKE = "HOT_INVOKE"
COLD_INVOKE = "COLD_INVOKE"
VPC_COLD_INVOKE = "VPC_COLD_INVOKE"
SCENES_INVOKE = "SCENES_INVOKE"

# ======================================================

# 腾讯云账号api id
QC_NAME = "qcloud"
QC_API_ID = "**************"
# 腾讯云账号api key
QC_API_KEY = "*************"

# 腾讯云 vpc信息，需要和地域信息对应
QC_VPC = "vpc-*******"
QC_SUBNET = "subnet-*******"

# 腾讯云请求api地址模板
# e.g. QC_ENDPOINT_MODEL % REGION
QC_ENDPOINT_MODEL = "scf.ap-%s.tencentcloudapi.com"

# 腾讯云函数命名空间，默认default
QC_NAMESPACE = "default"

# ======================================================
ALI_NAME = "aliyun"
# 阿里云用户id
ALI_USER_ID = "************"

# 阿里云请求api地址模板
# e.g. ALI_ENDPOINT_MODEL % (ALI_USER_ID, REGION)
ALI_ENDPOINT_MODEL = "https://%s.cn-%s.fc.aliyuncs.com"

# 阿里云账号 AccessKey ID
ALI_ACCESSKEY_ID = "**************"
# 阿里云账号 Access Key Secret
ALI_ACCESSKEY_KEY = "****************"

# 阿里云Service信息
ALI_VPC_SERVICE = "*****"
ALI_NORMAL_SERVICE = "*****"

# ======================================================
AWS_NAME = "aws"
# 亚马逊云产品名
AWS_PRODUCT_NAME = 'lambda'
# 亚马逊云账号 AccessKey ID
AWS_ACCESSKEY_ID = "**************"
# 亚马逊云账号 Access Key Secret
AWS_ACCESSKEY_KEY = "*****************"

# 亚马逊云产品角色
AWS_LAMBDA_ROLE = "*****************"

AWS_VPC_CONF = {'SubnetIds': ["subnet-*****","subnet-*****"],'SecurityGroupIds':["sg-*****"]}


