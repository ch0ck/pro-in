#!/usr/bin/env python
# encoding:utf-8
import os,re,collections
import requests,json,urlparse
from libmproxy import controller, proxy
from libmproxy.proxy.server import ProxyServer


class StickyMaster(controller.Master):
    def __init__(self, server):
			controller.Master.__init__(self, server)
			self.stickyhosts = {}
			self.pickurl = []

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, flow):
		hid = (flow.request.host, flow.request.port)
		if flow.request.headers["cookie"]:
			self.stickyhosts[hid] = flow.request.headers["cookie"]
		elif hid in self.stickyhosts:
			flow.request.headers["cookie"] = self.stickyhosts[hid]
		flow.reply()
		self.post_url(flow)

    def post_url(self,flow):
		lastUrl,headers,okurl='',{},flow.request.url
		headers['referer'] = flow.request.headers['referer'][0] if flow.request.headers['referer'] else ''
		headers['cookie']  = flow.request.headers['cookie'][0] if flow.request.headers['cookie'] else ''
	
		#过滤静态文件的链接
		preg = r'\.(jpg|png|gif|css|js|ttf|doc|jpeg|ico|mp4|flv|bmp)'
		htmlPreg = r'\.(html|htm|shtml)$'
		if (not re.findall(preg,okurl,re.I)) and (not re.findall(htmlPreg,okurl,re.I)):
			lastUrl = okurl if okurl else ''

		cuturl ,query,bcomeUrl= urlparse.urlparse(lastUrl),[],''
		if cuturl.query and lastUrl:   #GET 类型链接去重（目前先采用这种蛋疼的做法）
			for i in cuturl.query.split('&'):
				tmp=re.findall(r'\W([^\s]+)',i)
				if tmp and (tmp[0].isdigit() or len(tmp[0])>12):
					i=re.sub(r'\W([^\s]+)','=1',i)
					query.append(i) 
					lastquery= '&'.join(query)
					ParseUrl = collections.namedtuple('ParseUrl','scheme netloc path params query fragment')
					tmpUrl = ParseUrl(scheme=cuturl.scheme,netloc=cuturl.netloc,path=cuturl.path,params=cuturl.params,query=lastquery,fragment=cuturl.fragment)
					bcomeUrl = urlparse.urlunparse(tmpUrl)
		else:							#POST类型链接不做处理
				bcomeUrl=lastUrl

		if bcomeUrl not in self.pickurl:#判断检测过的列表里有无这个链接
			self.pickurl.append(bcomeUrl)#加入检测列表名单
			if lastUrl:
				print '%s %s'%(lastUrl,flow.request.content)
				requests.post("http://192.168.76.224:8082/compare",data=json.dumps({'url':lastUrl,'data':flow.request.content,'header':headers,'method':flow.request.method}),headers={'Content-Type':'application/json'})

    def handle_response(self, flow):
		hid = (flow.request.host, flow.request.port)
		if flow.response.headers["set-cookie"]:
			self.stickyhosts[hid] = flow.response.headers["set-cookie"]
		flow.reply()


config = proxy.ProxyConfig(port=8017)
server = ProxyServer(config)
m = StickyMaster(server)
m.run()
