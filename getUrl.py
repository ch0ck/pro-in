#-*- encoding:utf8- *-
import requests,sys,json,re
urllist=[]
def getdata(url):
	data = requests.get(url)
	result= data.content.split('\r\n')
	return result
	
			
def pickUrl(result):
	global urllist
	for i in result[:-1]:
		a=eval(i)
		a['header']={}
		preg = r'\.(jpg|png|gif|css|ttf|doc|jpeg|ico|mp4|flv|swf|bmp)'
		htmlpreg = r'\.(html|htm|shtml|js)$'
		if (not re.findall(preg,a['url'],re.I)) and (not re.findall(htmlpreg,a['url'],re.I)):
			if a['type']=='GET':
				urlpreg = r'(\w+/+$)|(cn$|jsp$|#$)|(html#)'
				if not re.findall(urlpreg,a['url']):
					urllist.append(a)
					a['header']['cookie']=a['cookie']
					a['header']['referer']=a['url']
					#print a['url']
					postFood(a)
			elif a['type']=='POST':
				urllist.append(a)
				a['header']['cookie']=a['cookie']
				a['header']['referer']=a['url']
				postFood(a)
				print a['url']
			#urllist.append(a)
			#print '======================='
			#print 'url : %s'%a['url']
			#print 'cookie : %s'%a['cookie']
			#print 'type : %s'%a['type']
				if a['body']: print 'body : %s'%a['body']

def postFood(food):
	requests.post("http://192.168.76.224:8082/compare",data=json.dumps({'url':food['url'],'data':food['body'],'header':food['header'],'method':food['type']}),headers={'Content-Type':'application/json'})
	print 'I had send %s+%s'%(food['type'],food['url'])

if __name__=='__main__':
	url = 'http://192.168.21.32/data/txt.txt'#raw_input('url:')
	result=getdata(url)
	pickUrl(result)
	#print urllist
