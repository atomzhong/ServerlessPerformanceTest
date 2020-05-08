# -*- coding: utf-8 -*-
# 默认语言：python27

from config import BASCI_LOGGING_CODE, BASIC_PRINT_CODE, NET_CODE, FILE_IO_CODE, FILE_RANDOM_IO_CODE, COMPUTE_CODE

CODE = {
    BASCI_LOGGING_CODE : \
'''
# -*- coding: utf-8 -*-
import logging

def handler(event, context):
    logger = logging.getLogger()
    logger.info('hello world')
    return 'hello world'
''',

    COMPUTE_CODE : \
'''# -*- coding: utf-8 -*-
import random
def handler(event, context):
    result = 1
    for _ in range(10000):
        result += random.random()
    return result
''',

    FILE_IO_CODE : \
'''# -*- coding: utf-8 -*-

def handler(event, context):
    filename = '/tmp/test.txt'  
    file = open(filename, 'w')  
    file.write("A"*419430400)  
    file.close()  
    file = open(filename, 'r')  
    return file.readline() 
''',

    FILE_RANDOM_IO_CODE : \
'''# -*- coding: utf-8 -*-
import random

def handler(event, context):
    l = range(100000)
    #预写入文件
    filename = '/tmp/test.txt'
    file = open(filename, 'w')  
    file.write("A"*100000)  
    file.close()
    #随机写
    file = open(filename, 'w')
    random.shuffle(l)
    for i in l:
        file.seek(i,0)
        file.write("B")
    file.close()
    #随机读
    random.shuffle(l)
    file = open(filename, 'r')
    for i in l:
        file.seek(i,0)
        file.read(1)
''',

    NET_CODE : \
'''# -*- coding: utf-8 -*-
import commands
def handler(event, context):
    cmd = 'curl -v http://www.baidu.com/'  
    status,output = commands.getstatusoutput(cmd)  
    print output  
    return output
''',

    BASIC_PRINT_CODE : \
'''# -*- coding: utf-8 -*-

def handler(event, context):
    for i in range(10000):  
        print i
'''
}