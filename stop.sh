#!/bin/sh
kill -s 9 `ps -ef |grep web.py |awk '{print $2}'`
kill -s 9 `ps -ef |grep sqlmapapi.py|awk '{print $2}'`
kill -s 9 `ps -ef |grep proxy.py|awk '{print $2}'`
