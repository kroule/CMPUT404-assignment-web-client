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
    STATUS_CODE = 'HTTP/1\.([0,1]) (.*?) (.*?)\Z'
    HEADERS     = '\A(.+?): (.*?)\Z'

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        linebyline = data.splitlines()

        # "In the interest of robustness, servers SHOULD ignore any empty line(s) received where a Request-Line is expected. 
        # In other words, if the server is reading the protocol stream at the beginning of a message and receives a CRLF first, it should ignore the CRLF.""
        for line in linebyline:
            if line == '':
                continue

            result = re.match(self.STATUS_CODE, line)
            if result and result.group(2).isnumeric():
                return int(result.group(2))
            else:
                return None

        return None

    def get_headers(self, data):
        linebyline = data.splitlines()
        past_status_code = False
        headers = {}

        for line in linebyline:
            if line == '':
                if past_status_code:
                    break
                continue

            if not past_status_code:
                r_result = re.match(self.STATUS_CODE, line)
                if r_result:
                    past_status_code = True
                continue

            result = re.match(self.HEADERS, line)
            # Incorrect header format? Just skip and go to next?
            if not result:
                continue

            # Matched attribute with no value? Ignore
            if len(result.groups()) < 2:
                continue

            # headers = { {date : "2021 something something"}, ... }
            headers[result.group(1)] = result.group(2)

        return headers

    def get_body(self, data):
        linebyline = data.splitlines()
        body = ''
        past_status_code, past_headers = False, False

        for line in linebyline:
            if past_status_code and past_headers:
                body += line + '\r\n'
                continue

            if line == '':
                past_headers = past_status_code
                continue

            if not past_status_code:
                result = re.match(self.STATUS_CODE, line)
                if result:
                    past_status_code = True
                    continue
                else:
                    # First non-empty line was garb
                    return
                
                past_headers = True

        return body
    
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

    def parse_url(self, url):
        result = urllib.parse.urlparse(url)
        host = result.netloc
        port = 80

        if ':' in host:
            host, port = host.split(':')
            if port.isnumeric():
                port = int(port)

        return host, port



    def GET(self, url, args=None):
        host, port = self.parse_url(url)

        header = f"GET {url} HTTP/1.1\r\nHost: {host}\r\n"
        header += "Connection: close\r\n"

        if args:
            for arg, val in args.items():
                header += arg + ': ' + val + '\r\n'

        header += '\r\n'

        self.connect(host, port)
        self.sendall(header)
        self.socket.shutdown(socket.SHUT_WR)

        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)
        #headers = self.get_headers(response)

        self.socket.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port = self.parse_url(url)

        header = f'POST {url} HTTP/1.1\r\nHost: {host}\r\n'
        header+= 'Connection: close\r\n'
        header+= 'Content-Type: application/x-www-form-urlencoded\r\n'
        header+= 'Content-Length: '
        body = ''

        if args:
            for arg, val in args.items():
                formatted = urllib.parse.quote(val, safe=' ')
                formatted = '+'.join(formatted.split())
                body += arg + '=' + formatted + '&'

            body=body[:-1]
            header+=str(len(body))+'\r\n'
        else:
            header+= '0\r\n'

        header+='\r\n'

        self.connect(host, port)
        self.sendall(header+body)
        self.socket.shutdown(socket.SHUT_WR)
        
        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)
        #headers = self.get_headers(response)

        self.socket.close()

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
