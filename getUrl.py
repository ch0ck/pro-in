#-*- encoding:utf8- *-
import requests,sys,json,re

class getUrl(object):
	def __init__(self,url=''):
			super(getUrl,self).__init__()
			self.url = url
			self.urllist=[]
	
	def getdata(self):
		data = requests.get(self.url)
		result= data.content.split('\r\n')
		return result
	
			
	def pickUrl(self,result):
			a=eval(result)
			a['header']={}
			preg = r'\.(jpg|png|gif|css|ttf|doc|jpeg|ico|mp4|flv|swf|bmp)'
			htmlpreg = r'\.(html|htm|shtml|js)$'
			if (not re.findall(preg,a['url'],re.I)) and (not re.findall(htmlpreg,a['url'],re.I)):
				if a['type']=='GET':
					urlpreg = r'(\w+/+$)|(cn$|jsp$|#$)|(html#)'
					if not re.findall(urlpreg,a['url']):
						self.urllist.append(a)
						a['header']['cookie']=a['cookie']
						a['header']['referer']=a['url']
						#self.postFood(a)
						print a['url']
				elif a['type']=='POST':
					self.urllist.append(a)
					a['header']['cookie']=a['cookie']
					a['header']['referer']=a['url']
					#self.postFood(a)

	def postFood(self,food):
		requests.post("http://192.168.76.224:8082/compare",data=json.dumps({'url':food['url'],'data':food['body'],'header':food['header'],'method':food['type']}),headers={'Content-Type':'application/json'})
		#print 'I had send %s+%s'%(food['type'],food['url'])

	def run(self):
		result=self.getdata()
		#self.pickUrl(result)
		for i in result[:-1]:
			self.pickUrl(i)
