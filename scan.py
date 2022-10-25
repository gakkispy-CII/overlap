import time
import queue
import argparse
import requests
import threading

class Dirscan(object):

	def __init__(self, scanSite, scanDict, scanOutput,threadNum):
		print('Dirscan is running!')
		# 三运运算符   https://www.oldboyedu.com/ 
		self.scanSite = 'http://%s' % scanSite if scanSite.find('://') == -1 else scanSite
		print('Scan target:',self.scanSite,"<=====>")
		
		# 把dict/dict.txt赋值给scanDict
		self.scanDict = scanDict
		# 创建数据文件 https://www.oldboyedu.com => www.oldboyedu.com + ".txt"
		self.scanOutput = scanSite.rstrip('/').replace('https://', '').replace('http://', '')+'.txt' if scanOutput == 0 else scanOutput
		# 指定并发线程的数量
		self.threadNum = threadNum # 60
		# 创建线程锁 (防止数据错乱,保证数据安全,所以需要线程锁)
		self.lock = threading.Lock()
		# 伪造请求头 (假装不是爬虫,是正常的浏览器访问)
		self._loadHeaders()
		# 把dict文件夹中dict文件读取出来
		self._loadDict(self.scanDict)
		# 判断键盘是不是使用ctrl+c进行键盘终止
		self.STOP_ME = False
		
	def _loadHeaders(self):
		self.headers = {
			'Accept': '*/*',  # 接受所有种类的数据类型
			'Referer': 'http://www.baidu.com',  # 请求该网站的源头网址 
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36', # 标注浏览器内核(伪造是浏览器请求的不是爬虫)
			'Cache-Control': 'no-cache',    # 不使用缓存
		}

	def _loadDict(self, dict_list):
		# 创建队列
		self.q = queue.Queue()
		# 把dict.txt里面的所有路径拿出来  dict_list = dict/dict.txt
		with open(dict_list ,mode="r", encoding="utf-8") as fp:
			for line in fp:
				# 如果不是注释
				if line[0] != '#':
					# 把数据添加到线程的队列里
					self.q.put(line.strip())

		# q.qsize是队列长度
		if self.q.qsize() > 0:
			print('Total Dictionary:',self.q.qsize())
		# 如果队列里面的数据已经没有了,证明线程已经处理完所有要扫描的路径;
		else:
			print('Dict is Null ???')
			# 退出
			quit()

	def _writeOutput(self, result):
		# 上锁
		self.lock.acquire()
		with open(self.scanOutput, mode = 'a+',encoding="utf-8") as f:
			f.write(result + '\n')
		# 解锁
		self.lock.release()

	def _scan(self, url):
		html_result = None
		try:
			# allow_redirects=False 参数,禁用重定向处理 timeout = 60 限定最大超时时间为60秒
			html_result = requests.get(url, headers=self.headers, allow_redirects=False, timeout=60)
		# 如果发生链接失败的报错
		except requests.exceptions.ConnectionError:
			print('Request Timeout:%s' % url)
		finally:
			if html_result.status_code == 200 and html_result is not None:
				# 状态码 , html_result.url
				# [200]https://www.oldboyedu.com//about_21.shtml.bak
				print('[%d]%s' % (html_result.status_code, html_result.url))
				self._writeOutput('[%d]%s' % (html_result.status_code, html_result.url))
				
	def run(self):
		# q.empty()判断是否为空
		while not self.q.empty() and self.STOP_ME == False:
			# https://www.oldboyedu.com/ + /index.html =>  https://www.oldboyedu.com//index.html
			url = self.scanSite + self.q.get()
			self._scan(url)

if __name__ == '__main__':
	# ### part1 封装参数
	parser = argparse.ArgumentParser()
	# 必要参数  要浏览的网站
	parser.add_argument('scanSite', help="The website to be scanned", type=str)
	# 可选参数  要匹配的目录原文件
	parser.add_argument('-d', '--dict'  , dest="scanDict"  , help="要浏览的目录", type=str,   default="dict/dict.txt")
	# 可选参数  要保存的文件
	parser.add_argument('-o', '--output', dest="scanOutput", help="保存的文件"    , type=str, default=0)
	# 设置线程的数量 
	parser.add_argument('-t', '--thread', dest="threadNum" , help="设置线程的数量", type=int, default=60)
	# 返回参数对象
	args = parser.parse_args()
	
	
	# ### part2 实例化对象 (自动触发init构造方法) 
	# scanSite = https://www.oldboyedu.com/   scanDict = dict/dict.txt   scanOutput = 0  threadNum = 60
	scan = Dirscan(args.scanSite, args.scanDict, args.scanOutput, args.threadNum)	

	# ### part3 创建60个子线程,执行run这个任务
	for i in range(args.threadNum):
		t = threading.Thread(target=scan.run)
		t.start()

	# ### part4 判断是否存在键盘终止的异常.
	# threading.activeCount() 统计当前活跃线程的数量是多少
	while True:
		if threading.activeCount() <= 1 :
			break
		else:
			try:
				# 爬的太快容易封ip,适当速度减慢
				time.sleep(0.1)
			# KeyboardInterrupt 在ctrl +c 的时候触发报的错误是KeyboardInterrupt
			except KeyboardInterrupt:
				print('\n[WARNING] 请等待所有的子线程执行结束 当前线程数为%d' % threading.activeCount())
				scan.STOP_ME = True
	
	print('Scan end!!!')
	
