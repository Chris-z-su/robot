import getMsg

#flag为全局变量
#flag = 0 正常
#flag = 1 数据不通过数据库
#flag = 2 退出
#使用try、except语句保证程序不会因部分错误退出。
if __name__ == '__main__':
    while 1:
        global flag
        flag = 0
        all_message = getMsg.rev_msg()
        print(all_message)
        try:
            getMsg.first_judgement()
        except:
            continue



