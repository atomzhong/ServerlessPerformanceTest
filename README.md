# ServerlessPerformanceTest

Serverless performance testing framework.

任意带外网机器执行以下命令安装依赖库：

pip install tencentcloud-sdk-python

pip install boto3

pip install aliyun-fc2

export PYTHONPATH=/your_dir

cd ServerlessPerFormanceTest

需要添加python环境变量
export PYTHONPATH=/root/ServerlessPerformanceTest/

配置文件中需要填写所有以\*号隐去的字段

目录说明：

code_zip # 用于保存创建函数时生成的代码zip包

log # 执行日志存放目录

result # 执行结果数据文件存放目录

运行方式：
python main.py

