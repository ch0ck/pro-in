# encoding:utf-8

import os, subprocess,requests,time,json,sqlite3,random
from multiprocessing import Process, Queue
from bottle import route, run, template, request,static_file
from AutoSqli import AutoSqli
queue_waiting = Queue()
queue_scaning = Queue(10)

@route('/html/images/:filename#.*.png#')
def send_image(filename):
	return static_file(filename,root='/root/proxy-sqli/html/images/',mimetype='image/png')

@route('/html/js/:filename')
def send_static(filename):
	return static_file(filename,root='/root/proxy-sqli/html/js/')

@route('/html/css/:filename')
def send_css(filename):
	return static_file(filename,root='/root/proxy-sqli/html/css/')
@route('/html/fonts/:filename')
def send_font(filename):
	return static_file(filename,root='/root/proxy-sqli/html/fonts/')
		
@route('/compare', method='POST')
def compare_scaner():    
    urls = request.body.readlines()
    postdata = eval(urls[0])
    queue_waiting.put(postdata)
    Process(target=queue_get,args=(queue_waiting,queue_scaning)).start()


@route('/index', method='GET')
def index():
	conn = sqlite3.connect('sqli.db')
	cs = conn.cursor()
	cs.execute('select * from injection')
	result = cs.fetchall()
	conn.commit()
	conn.close()
	return template('html/index.html',result=result,color='success',scaning=queue_scaning.qsize(),waiting=queue_waiting.qsize())

def queue_get(queue_waiting, queue_scaning):
    while not queue_scaning.full():
	while queue_waiting.qsize()>0 :
	        postdata = queue_waiting.get()
		data = postdata['data'] if postdata['data'] else ''
        	queue_scaning.put(1)
		wow = AutoSqli('http://127.0.0.1:8775',postdata['url'],data,postdata['header']['referer'],postdata['header']['cookie'])
		wow.run()
		queue_scaning.get()	


        
if __name__ == '__main__':

    run(host='192.168.76.224', port=8082)
