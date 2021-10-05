#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        result = urllib.parse.urlparse(url)
        path = result.path
        host = result.netloc.split(':')[0]
        port = 80
        if len(result.netloc.split(':')) > 1:
            port = int(result.netloc.split(':')[1])
        #else:
            #host = socket.gethostbyname(host)

        body = f"GET {url} HTTP/1.1\r\nHost: {host}\r\n\r\n"
        self.connect(host, port)
        self.sendall(body)
        self.socket.shutdown(socket.SHUT_WR)
        recieved = self.recvall(self.socket)
        print("###############################")
        print(recieved)

        content = ''
        start = False
        match = [
            "\AHTTP\/(.*?) (\d*?) (.*)\Z",
            "\A(.+?): (.*)\Z",
            "\A(.+?): (\S*, \d{2} \S{3} \d{4} \d\d:\d\d:\d\d \S*)\Z"
        ]
        lines = recieved.splitlines()
        attributes = {}
        code = 0
        for i in range(len(lines)):
            if lines[i] == '':
                start = True
                continue

            if start:
                content+=lines[i]+'\r\n'
                continue

            reg = re.match(match[0], lines[i])
            if reg:
                code = int(reg.groups()[1])
                continue
            reg = re.match(match[2], lines[i])
            if reg:
                attributes[reg.groups()[0]] = reg.groups()[1]
                continue
            reg = re.match(match[1], lines[i])
            if reg:
                attributes[reg.groups()[0]] = reg.groups()[1]
                continue

        print(attributes)
        print(code)
        print("-------------------------------")
        self.socket.close()
        return HTTPResponse(code, content)

    def POST(self, url, args=None):
        code = 500
        #match = "\A&(\S*?)=(.*)\Z"
        #match.group[0] = attributes
        #match.group[1] = value
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
