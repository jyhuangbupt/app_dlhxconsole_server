# -*- coding: utf-8 -*-
'''项目自动化部署脚本

执行步骤


'''

import sys, os, datetime
import commands

def yieldcommand(cmd):
    '''执行一个shell命令，并打印输出到标准输出'''
    r = os.popen(cmd)
    l = r.readline()
    while l:
        l = l[0:-1]
        print '>>>%s' % l
        yield l
        l = r.readline()

def run(dev=True, service=None):
    branch = 'develop' if dev else 'master'
    configfile = 'config.dev.yaml' if dev else 'config.pro.yaml'

    print '-------------> checkout to %s' % branch
    for l in yieldcommand('git checkout %s' % branch):
        pass

    # print '-------------> start stash workspace '
    # for l in yieldcommand('git stash'):
    #     pass

    print '-------------> pull the lastest verson from %s' % branch
    for l in yieldcommand('git pull origin %s' % branch):
        pass


    print '-------------> copy %s to config.yaml' % configfile
    for l in yieldcommand('cp %s config.yaml' % configfile):
        pass

    # print '-------------> init server'
    # for l in yieldcommand('python server.py init'):
    #     pass

    print '-------------> restart service %s' % service
    for l in yieldcommand('supervisorctl restart %s' % service):
        pass

    print '-------------> finish '


if __name__ == '__main__':
    usage = '''
    命令错误，请按照下面命令输入：
    python deploy.py dev <service>
    python deploy.py pro <service>

    比如，家族办公室测试环境部署：
    python deploy.py bbs

    '''
    argv = sys.argv
    if len(argv) != 3:
        print usage
    else:
        dev = (argv[1].lower() == 'dev')
        service = argv[2]
        print dev
        print service
        run(dev=dev, service=service)



