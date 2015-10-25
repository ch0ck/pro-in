# encoding:utf-8
import os,json,time,requests,sqlite3

class AutoSqli(object):
	def __init__(self,server='',target='',data='',referer='',cookie=''):
		super(AutoSqli,self).__init__()
		self.server = server
		if self.server[-1] != '/':
			self.server = self.server+'/'
		self.target = target
		self.taskid = ''
		self.engineid = ''
		self.status = ''
		self.data = data
		self.referer = referer
		self.cookie = cookie
		self.ua = 'Googlebot/2.1 (+http://www.googlebot.com/bot.html)'
		self.payload = {'url':self.target}
		self.start_time = time.time()

	def task_new(self):
		self.taskid = json.loads(requests.get(self.server+'task/new').text)['taskid']
		print 'Created new task: '+self.taskid
		if len(self.taskid)>0:
			return True
		return False

	def task_delete(self):
		if json.loads(requests.get(self.server + 'task/'+self.taskid+'/delete').text)['success']:
			print '[%s] Delete task'%(self.taskid)
			return True
		return False

	def scan_start(self):
		headers = {'Content-Type':'application/json'}
		if self.data:
			self.payload['data'] = self.data
		if self.cookie:
			self.payload['cookie'] = self.cookie
		if self.referer:
			self.payload['referer'] = self.referer
		if self.ua:
			self.payload['User-Agent'] = self.ua

		url = self.server + 'scan/'+self.taskid + '/start'
		t = json.loads(requests.post(url,data=json.dumps(self.payload),headers=headers).text)
		self.engineid = t['engineid']
		if len(str(self.engineid))>0 and t['success']:
			print 'Start scan'
			print self.payload
			return True
		return False

	def scan_status(self):
		self.status = json.loads(requests.get(self.server+'scan/'+self.taskid+'/status').text)['status']
		if self.status == 'running':
			return 'running'
		elif self.status == 'terminated':
			return 'terminated'
		else:
			return 'error'

	def scan_data(self):
		self.data = json.loads(requests.get(self.server+'scan/'+self.taskid+'/data').text)['data']
		if len(self.data)==0:
			print "\33[31mnot injection\33[0m"
		else:
			self.data2db()
			#print self.payload
			#print '\33[31minjection:%s\33[0m\t'%self.target
	
	def option_set(self):
		headers = {'Content-Type':'application/json'}
		option = {'option':{"smart":True}}
		url = self.server+'option/'+self.taskid+'/set'
		t = json.loads(requests.post(url,data=json.dumps(option),headers=headers).text)
		print t

	def scan_stop(self):
		json.loads(requests.get(self.server+'scan/'+self.taskid+'/stop').text)['success']
		
	def scan_kill(self):
		json.loads(requests.get(self.server+'scan/'+self.taskid+'/kill').text)['success']
	def data2db(self):
		data = self.data[0]
		target = self.target
		conn = sqlite3.connect("sqli.db")
		csor = conn.cursor()
		csor.execute("insert into injection values (null,?,?,?,?)",(target,'%s'%self.payload,"%s"%data,time.time())) 
		conn.commit()
		conn.close()

	def run(self):
		if not self.task_new():
			return False
		self.option_set()
		if not self.scan_start():
			return False
		while True:
			if self.scan_status() == 'running':
				time.sleep(10)
			elif self.scan_status() == 'terminated':
				break
			else:
				break

			if time.time() -self.start_time > 300:
				error= True
				self.scan_stop()
				self.scan_kill()
				break
		self.scan_data()
		self.task_delete()
		print 'it used only '+str(time.time() - self.start_time)+'s'
