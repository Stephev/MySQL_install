#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Time    : 2018/11/1 0001 
# @Author  : Stephev
# @Site    : 
# @File    : MY_install.py
# @Software:

import os
import ConfigParser
import commands
import string

ins = ConfigParser.ConfigParser()
ins.read('install.conf')
install_path = ins.get("INSTALL","INSTALL_PATH")
rpm_name = ins.get("INSTALL","RPM")
datadir_path = ins.get("INSTALL","DATADIR")
new_pass = ins.get("INSTALL","PASSWD")


def check_user():           #判断mysql用户是否存在,存在直接用，不存在创建
    print "[INFO] 正在检查系统的用户..."
    cc=os.popen('cat /etc/passwd').readlines()
    ccc=''
    for i in cc:
        user_name = i.split(':')
        ccc = cmp(user_name[0],'mysql')
    if ccc == 0:
        if os.path.exists('/home/mysql'):
            print ("[INFO] 用户mysql存在且拥有家目录，直接使用它")
        else:
            exit("[FATAL]:已存在用户mysql，但该用户没有家目录。请手动删除此用户或者为其创建家目录")
    else:
        if os.path.exists('/home/mysql'):
            exit("[FATAL]:没有msyql用户但是存在mysql家目录，请删除它或改名")
        else:
            os.system("useradd -U mysql")
            print("[INFO] 成功创建mysql用户...ok")
    return


def rpm_install():   # 解压RPM包安装
    print "[INFO] 正在解压RPM包..."
    cmd_tar = "tar -xzf"+rpm_name+" -C "+install_path+" >/dev/null"
    int_tar = os.system(cmd_tar)
    if int_tar == 0:
        print "[INFO] 解压成功...ok"
    else:
        print "[Error]:解压失败"
        exit('[FATAL]:退出安装程序...')
    print "[INFO] 正在创建软连接..."
    cmd_ln = "ln -s "+install_path+"/mysql-5.7.22-linux-glibc2.12-x86_64 " +install_path+"/mysql"
    ln_int = os.system(cmd_ln)
    if ln_int == 0:
        print "[INFO] 创建成功...ok"
    else:
        print "[Error]:创建失败"
        exit('[FATAL]:退出安装程序...')
    print "[INFO] 正在给安装包赋权..."
    cmd_chown_ln = "chown -R mysql:mysql "+install_path+"/mysql-5.7.22-linux-glibc2.12-x86_64"
    cmd_chown_pg = "chown -R mysql:mysql "+install_path+"/mysql"
    os.system(cmd_chown_ln)
    os.system(cmd_chown_pg)
    print "[INFO] 赋权成功...ok"
    return


def set_data():  #检查提供的数据目录
    print "[INFO] 正在检查处理数据目录..."
    if os.path.exists(datadir_path):
        cmd_lsdir = 'ls '+datadir_path+'| wc -l'
        data_string = commands.getoutput(cmd_lsdir)
        data_int = string.atoi(data_string)
        if data_int>0:
            print "Error:指定为数据目录的文件夹不为空，请清空后重试"
            exit('[FATAL]:退出安装程序...')
        else:
            cmd_chown_data = 'chown -R mysql:mysql '+datadir_path
            int_chown = os.system(cmd_chown_data)
            if int_chown == 0:
                print "[INFO] 为数据目录赋权成功...ok"
            else:
                exit('[FATAL]:为数据目录赋权失败，数据目录的权限必须是mysql用户')
        print "[INFO] 数据目录检查完成...ok"
    else:
        print "[Error]:必须先准备好数据目录.(最好是插盘挂载，保证空间充足)"
        exit('[FATAL]:退出安装程序...')
    return


def set_path():     # 配置好环境变量
    print "[INFO] 正在配置环境变量..."
    path_profile = open("/root/.bash_profile","a")
    path_profile.write("export PATH=$PATH:/usr/local/mysql/bin")
    path_profile.close()
    cmd_source = "source /root/.bash_profile"
    sou_int = os.system(cmd_source)
    if sou_int == 0:
        print "[INFO] 配置成功...ok"
    else:
        exit('[FATAL]:配置mysql的环境变量失败')
    return


def myconf():     #检查my.cnf的配置信息
    print "[INFO] 正在配置my.cnf文件..."
    if os.path.exists('/home/mysql'):
        print "[INFO] 已经存在my.cnf文件，我们将它备份好..ok"
        os.system('cp /etc/my.cnf /etc/my.cnf_bak')
    print "[INFO] 配置我们提供的默认信息..."
    my = ConfigParser.ConfigParser()
    my.read('/etc/my.cnf')
    if my.has_section('mysqld'):
        my.set('mysqld', 'datadir' ,datadir_path)
        my.set('mysqld','socket',datadir_path+'/mysql.sock')
        my.set('mysqld','user','mysql')
        my.set('mysqld','enforce_gtid_consistency','on')
        my.set('mysqld','binlog_format','row')
        my.set('mysqld', 'symbolic-links', '0')
        my.set('mysqld', 'port', '3306')
        my.set('mysqld', 'enforce_gtid_consistency', 'on')
    else:
        my.add_section('mysqld')
        my.set('mysqld', 'datadir' ,datadir_path)
        my.set('mysqld','socket',datadir_path+'/mysql.sock')
        my.set('mysqld','user','mysql')
        my.set('mysqld','enforce_gtid_consistency','on')
        my.set('mysqld','binlog_format','row')
        my.set('mysqld', 'symbolic-links', '0')
        my.set('mysqld', 'port', '3306')
        my.set('mysqld', 'enforce_gtid_consistency', 'on')
    if my.has_section('mysqld_safe'):
        my.set('mysqld_safe','log-error',datadir_path+'/mysqld.log')
        my.set('mysqld_safe', 'pid-file', datadir_path+'/mysqld.pid')
    else:
        my.add_section('mysqld_safe')
        my.set('mysqld_safe','log-error',datadir_path+'/mysqld.log')
        my.set('mysqld_safe','pid-file',datadir_path+'/mysqld.pid')
    my.write(open('/etc/my.cnf', 'w'))
    print "[INFO] 配置文件准备成功..ok"
    return


def initialize():
    print "[INFO] 正在初始化数据库..."
    init_com = 'mysqld --user=mysql --basedir='+install_path+'/mysql --datadir='+datadir_path+' --initialize >/dev/null'
    int_init = os.system(init_com)
    if int_init == 0:
        print "[INFO] 初始化数据库成功...ok"
    else:
        exit("[Error] 初始化数据库失败")
    print "[INFO] 正在启动数据库..."
    mysqld_safe = 'mysqld_safe --skip-grant-tables &'
    int_start = os.system(mysqld_safe)
    if int_start == 0:
        print "[INFO] 启动数据库成功...ok"
    else:
        exit("[FATAL] 启动数据库失败")
    print "[INFO] 启动数据库成功...ok"
    return


def passwd():
    print "[INFO] 正在修改数据库密码..."
    flu = "mysql -uroot -h127.0.0.1 -e \'flush privileges;\'  -e'set password for root@localhost = password('"+new_pass+"');'"
    os.system(flu)
    #setpasswd = "mysql -uroot -h127.0.0.1 -e'set password for root@localhost = password('"+new_pass+"');'"
    #os.system(setpasswd)
    print "[INFO] 修改成功....ok"
    return


def main():
    check_user()
    rpm_install()
    set_data()
    set_path()
    myconf()
    initialize()
    #passwd()
    print "[INFO] MySQL数据库安装完成...ok"
    return

if __name__ == '__main__':
    main()
