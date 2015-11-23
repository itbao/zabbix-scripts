#!/bin/env python
#coding:utf-8
import sys
import argparse
import json
import time
import datetime
import stomp
import logging
import os
reload(sys)
sys.setdefaultencoding("utf-8")

amq_ip='172.17.0.9'
amq_port=61613
amq_user='admin'
amq_pass='admin'
destination='/queue/zabbix'

def setLogger():  
    logger = logging.getLogger('mylogger')  
    logger.setLevel(logging.DEBUG)  
      
    fh = logging.FileHandler(os.path.join('/tmp/', 'send_activemq.log'))  
    fh.setLevel(logging.DEBUG)  
      
    ch = logging.StreamHandler()  
    ch.setLevel(logging.DEBUG)  
      
    formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter)  
      
    logger.addHandler(fh)  
    logger.addHandler(ch)  
      
    logger.info('hello world, i\'m log helper in python, may i help you')  
    return logger  

logger=setLogger()

if len(sys.argv) < 2:
    print "No arguments!!!"
    exit()

zbx_severity_map= {
    'Disaster':       '5',
    'High':           '4',
    'Average':        '3',
    'Warning':        '2',
    'Information':    '1',
    'Not classified': '0',
}

zbx_status_map={
    'PROBLEM':	'OPEN',
    'OK':	'CLOSED'
}

data=[]

try: 
    parser = argparse.ArgumentParser()
    parser.add_argument('activemq',nargs='*')
    args = parser.parse_args()

    log=open('/tmp/send_activemq2.log','a+')
    log.write(str(args.activemq[2]))
    log.close()
    
    for line in args.activemq[2].split(';'):
        if '=' not in line:
        	continue
        k,v=line.strip('\r\n').split('=')
        if k == "modifyTime" or k == "arrivalTime" or k == "tally":
        	type="long"
        else:
            type="string" 
        if k == "modifyTime" or k == "arrivalTime":
            d=datetime.datetime.strptime(v,"%Y.%m.%d %H:%M:%S")
            v=time.mktime(d.timetuple())
        if k == 'severity' or k == 'original_severity':
            v=zbx_severity_map[v]
        if k == 'status':
            v=zbx_status_map[v]
    
        data.append({"name":k,"val":v,"type":type})
        trgger_data=json.dumps([data],indent=4)
except:
    logger.exception("Exception Logged") 

class MyListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print('received an error "%s"' % message)
    def on_message(self, headers, message):
        print('received a message "%s"' % message)

#conn = stomp.Connection()
conn = stomp.Connection10([(amq_ip,amq_port)])
conn.set_listener('', MyListener())
conn.start()
conn.connect(amq_user, amq_pass, wait=True)

#send 发送信息
conn.send(body=trgger_data, destination=destination)

time.sleep(1)
conn.disconnect()
