#!/usr/bin/env python3
# -*- coding:utf8 -*-

__author__ = 'thomas.sterber@meraki.net'


info = '''

This script will
- receive syslog messages on port 20514
- log the incoming syslog message
- create out of them json messages and
- send them per Webhook to a Cloud Webhook Receiver

This is for Demo usage only

For a public free Webhook-Receiver goto http://webhook.site

'''

# ------------------------------------------------------
# imports
# ------------------------------------------------------
import os
import logging
import socketserver as SocketServer
import requests, json



# ------------------------------------------------------
# settings
# ------------------------------------------------------
LOG_FILE = 'youlogfile.log'
HOST, PORT = "0.0.0.0", 20514

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')




# ------------------------------------------------------
# functions
# ------------------------------------------------------
'''
sender:
192.168.10.6 :   #!! == str(self.client_address[0])
message:
<134>1 1674475214.739659485 CW9164I flows allow src=192.168.21.100 dst=23.89.83.113 mac=A4:50:46:D5:53:55 protocol=udp sport=37865 dport=5004
'''
def create_json(message):
    dic = {}
    dic['senders ip'] = message[0]
    dic['time_stamp'] = message[2]
    dic['sender hw']  = message[3]
    dic['type']       = message[4]
    dic['policy']     = message[5]
    source = message[6].replace('src=', '')
    dic['src']        = source
    destination = message[7].replace('dst=', '')
    dic['dst']        = destination
    mac_address = message[8].replace('mac=', '')
    dic['mac']        = mac_address
    protocol = message[9].replace('protocol=', '')
    dic['protocol']   = protocol
    source_port = message[10].replace('sport=', '')
    dic['source port']   = source_port
    destination_port = message[11].replace('dport=', '')
    dic['destination port']   = destination_port
    #
    json_data = dic
    print('json_data :\n',json_data)
    return(json_data)



def send_webhook(senddata):
    print('sending data per Webhook')
    url = webhook_receiver_url
    senddata = json.dumps(senddata)
    #
    header = {'Content-Type': 'application/json'}
    response = requests.post(url, data=senddata, headers=header)
    #
    print('Status Code : ' , response.status_code)
    print('Content : ' , response.text)
    #
    return()


class SyslogUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        data = str(self.client_address[0]) + ' ' + str(data)
        print (data)
        logging.info(data)
        # filter only firewall messages
        filter = 'flows'                         # firewall messages
        data = data.replace(':','')        # remove :
        data = data.split(' ')             # generate list
        print(data)
        if (data[4] == filter):
            senddata = create_json(data)
            send_webhook(senddata)
        


# --------------------------------------------------------
# Main
# --------------------------------------------------------
if __name__ == "__main__":
    os.system('clear')
    webhook_receiver_url = input('Webhook Receiver URL :')
    print(48*'-')
    print('starting receiver')
    print('\nto stop press CTRL+C')
    print(48*'-')
    #
    try:
        server = SocketServer.UDPServer((HOST,PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print ("Crtl+C Pressed. Shutting down.")
