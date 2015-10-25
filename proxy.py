#!/usr/bin/env python
"""
This example builds on mitmproxy's base proxying infrastructure to
implement functionality similar to the "sticky cookies" option.

Heads Up: In the majority of cases, you want to use inline scripts.
"""
import os,re
import requests,json
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
	lastUrl=''
	headers={}
	okurl = flow.request.url
	preg = r'\.(jpg|png|gif|css|js|ttf|doc|jpeg|ico|mp4|flv|bmp)'
	htmlPreg = r'\.(html|htm|shtml)$'
	if not re.findall(preg,okurl,re.I):
		if not re.findall(htmlPreg,okurl,re.I):
			lastUrl = okurl if okurl else ''	
			#if lastUrl : print lastUrl
	headers['referer'] = flow.request.headers['referer'][0] if flow.request.headers['referer'] else ''
	headers['cookie']  = flow.request.headers['cookie'][0] if flow.request.headers['cookie'] else ''
        
	hid = (flow.request.host, flow.request.port)
        if flow.request.headers["cookie"]:
            self.stickyhosts[hid] = flow.request.headers["cookie"]
        elif hid in self.stickyhosts:
            flow.request.headers["cookie"] = self.stickyhosts[hid]
        flow.reply()
	if lastUrl not in self.pickurl:
		self.pickurl.append(lastUrl)
		print lastUrl
#	if lastUrl:
#		requests.post("http://192.168.76.224:8082/compare",data=json.dumps({'url':lastUrl,'data':flow.request.content,'header':headers,'method':flow.request.method}),headers={'Content-Type':'application/json'})	

    def handle_response(self, flow):
        hid = (flow.request.host, flow.request.port)
        if flow.response.headers["set-cookie"]:
            self.stickyhosts[hid] = flow.response.headers["set-cookie"]
        flow.reply()


config = proxy.ProxyConfig(port=8004)
server = ProxyServer(config)
m = StickyMaster(server)
m.run()
