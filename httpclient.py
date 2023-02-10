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
    def __init__(self, code=200, body="", headers=None):
        self.code = code
        self.body = body
        self.headers = headers

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        for lines in data:
            if lines.startswith("HTTP/1.1"):
                return int(lines.split(" ")[1])
        return None

    def get_headers(self,data):
        headers = {}
        for lines in data:
            if lines.startswith("<!doctype"):
                continue
            else:
                divided_line = lines.split(":")
                if len(divided_line) < 2:
                    continue
                header_name = divided_line[0]
                header_content = divided_line[1]
                headers[header_name] = header_content
        return headers
                
    def get_body(self, data):
        for lines in data:
            if lines.startswith("<!doctype"):
                return lines
    
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
        try:
            self.connect( url, 80 )
        except:
            return HTTPResponse(404, "404 Not Found")
        
        request = "GET / HTTP/1.1\r\nHost:"+url+"\r\n\r\n"
        self.sendall(request)
        self.socket.shutdown(socket.SHUT_WR)
        message = self.recvall(self.socket)
        code = 500
        list_of_lines = message.split("\r\n")                
        code = self.get_code(list_of_lines)
        headers = self.get_headers(list_of_lines)
        body = self.get_body(list_of_lines)          
        return HTTPResponse(code, headers, body)

    def POST(self, url, args=None):
        try:
            split_url = url.split("?")
            path = split_url[0]
            args = split_url[1]
        except:
            return HTTPResponse(422, "Unprocessable Entity")
            
        try:
            self.connect( path, 80 )
        except:
            return HTTPResponse(404, "404 Not Found")
        
        request = "POST / HTTP/1.1\r\nHost:"+url+"Content-Type: application/x-www-form-urlencoded\r\nContent-Length: "+str(len(args))+"\r\n\r\n"+args+"\r\n\r\n"
        self.sendall(request)
        self.socket.shutdown(socket.SHUT_WR)
        message = self.recvall(self.socket)
        code = 500
        list_of_lines = message.split("\r\n")    
        print(list_of_lines)            
        code = self.get_code(list_of_lines)
        headers = self.get_headers(list_of_lines)
        body = self.get_body(list_of_lines)          
        return HTTPResponse(code, headers, body)

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
