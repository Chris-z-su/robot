import json
import os
import random
import socket

ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ListenSocket.bind(('127.0.0.1', 5710))
ListenSocket.listen(100)

HttpResponseHeader = '''HTTP/1.1 200 OK
Content-Type: text/html
'''

#定位有效信息
def request_to_json(msg):
	for i in range(len(msg)):
		if msg[i]=="{" and msg[-1]=="}":
			return json.loads(msg[i:])
	return None

#需要循环执行，返回值为json格式
def rev_msg():# json or None
	print(123)
	conn, Address = ListenSocket.accept()
	Request = conn.recv(1024).decode(encoding='utf-8')
	#print(Request)
	rev_json=request_to_json(Request)
	#print(rev_json)
	conn.sendall((HttpResponseHeader).encode(encoding='utf-8'))
	conn.close()
	return rev_json


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#从客户端发送给服务端
def client_to_conn():
	label = get_message_type()
	number = get_number()
	msg = get_raw_message()
	if flag == 0:
		msg = txt_msg(get_raw_message())
	if label == 'group':
		payload = "GET /send_group_msg?group_id=" + str(number) + "&message=" + msg + " HTTP/1.1\r\nHost: 127.0.0.1:5700\r\nConnection: close\r\n\r\n"
	elif label == 'private':
		payload = "GET /send_private_msg?user_id=" + str(number) + "&message=××××" + " HTTP/1.1\r\nHost: 127.0.0.1:5700\r\nConnection: close\r\n\r\n"
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('127.0.0.1',5700))
	client.send(payload.encode("utf-8"))
	client.close()


#获取信息类型 群聊/私聊 group/private
def get_message_type():
	return all_message['message_type']

#获取群号/私聊qq号
def get_number():
	if get_message_type() == 'group':
		return all_message['group_id']
	elif get_message_type() == 'private':
		return all_message['user_id']
	else:
		print('出错啦！找不到群号/QQ号')
		exit()
# 获取信息发送者的QQ号
def get_user_id():
	return all_message['user_id']

#获取发送的信息
def get_raw_message():
	return all_message['raw_message']

#查找txt文本数据库
def txt_msg(msg):
	fp = open("/机器人/txt.txt", "r",encoding='utf-8')
	while 1:
		s = fp.readline()
		if not s:
			fp.close()
			if flag == 2:
				return
			return error()
		s = s.strip('\n')
		s1 = s.split(' ')[0]
		s2 = s.split(' ')[1]
		if '[CQ:at,qq=×××××] ' + s1 == msg:
			fp.close()
			return s2


#帮助界面
def help_interface():
	number = get_number()
	payload = "GET /send_group_msg?group_id=" + str(number) + "&message=学习方式：%0a私聊rabbit酱，发送学习信息。%0a学习格式：%27学习%27%20%2b%20发送信息%20%2b%20回复信息，以空格分开%0a例：学习%20我爱你%20我也爱你" + " HTTP/1.1\r\nHost: 127.0.0.1:5700\r\nConnection: close\r\n\r\n"
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('127.0.0.1',5700))
	client.send(payload.encode("utf-8"))
	client.close()

#错误
def error():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('127.0.0.1',5700))
	rand = random.randint(1,4)
	number = get_number()
	if rand == 1:
		msg = "我听不懂你在说什么哦"
	elif rand == 2:
		msg = "我好笨，听不懂呜呜呜"
	elif rand == 3:
		msg = "啊？发生了什么"
	elif rand == 4:
		msg = "干啥呢干啥呢"
	payload = "GET /send_group_msg?group_id=" + str(number) + "&message=" + msg + " HTTP/1.1\r\nHost: 127.0.0.1:5700\r\nConnection: close\r\n\r\n"
	client.send(payload.encode("utf-8"))
	client.close()

#发送猫猫图，图片保存在本地
def send_cat_pic():
	global flag
	flag = 1
	cat_list = os.listdir("/data/catpic")
	all_message['raw_message'] = "[CQ:image,file=file:///data/catpic/"+ random.choice(cat_list)+"]"
	client_to_conn()

#发送setu，图片从API内获取
def send_setu_pic():
	apikey = '×××××××××××××××'
	req_url="https://api.lolicon.app/setu/"
	params = {"apikey":apikey}
	res=requests.get(req_url,params=params)
	setu_url=res.json()['data'][0]['url']
	all_message['raw_message'] ="[CQ:image,file="+setu_url+"]"
	client_to_conn()

#调教机器人
#这块代码也有点bug，需要后期调整。
def training_message():
	s = get_raw_message()
	if s.split(' ')[0] != '学习':
		return
	s2 = s.split(' ')[1]
	s3 = s.split(' ')[2]
	s = s2 + ' ' + s3
	fp = open("/机器人/txt.txt", "a",encoding='utf-8')
	fp.write('\n')
	fp.write(s)
	fp.close()
	client_to_conn()


#首次判断信息内容
def first_judgement():
	if get_message_type() == 'private':
		training_message()
	if get_raw_message() == '[CQ:at,qq=×××××××××] help':
		help_interface()
		return
	if get_raw_message() == '[CQ:at,qq=×××××××××] setu':
		send_setu()
		return
	elif get_raw_message() == '[CQ:at,qq=×××××××××] 猫猫图':
		send_cat_pic()
		return
	elif len(get_raw_message()) < 20:  #即使不@，也有15%概率回复信息
		rand = random.randint(1,20)
		if rand <= 3:
			global flag
			flag = 2
			all_message['raw_message'] = '[CQ:at,qq=×××××××××] ' + all_message['raw_message']
			client_to_conn()
		else:
			return
	elif get_raw_message()[0:20] != '[CQ:at,qq=×××××××××]':
		return
	client_to_conn()

#flag为全局变量
#flag = 0 正常
#flag = 1 数据不通过数据库
#flag = 2 退出
#使用try、except语句保证程序不会因部分错误退出。
while 1:
	global flag
	flag = 0
	all_message = rev_msg()
	print(all_message)
	try:
		first_judgement()
	except:
		continue
