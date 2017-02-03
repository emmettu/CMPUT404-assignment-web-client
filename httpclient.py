#!/usr/bin/env python
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
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = int(code)
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def __init__(self):
        self.open_socket()

    def connect(self, host, port=80):
        self.socket.connect((host, port))

    def get_code(self, data):
        # print data
        return data.split("\n")[0].split(" ")[1]

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

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
        return str(buffer)

    def GET(self, args):
        host, path, port = self.parse_url(args)
        self.connect(host, port)
        self.socket.sendall(
"""
GET %s HTTP/1.1\r
Host: %s\r
\r
""" % (path, host)
        )
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.reset_socket()
        return HTTPResponse(code, body)

    def POST(self, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def parse_url(self, args):
        url = args.strip("http://")
        path = "/"
        host = url
        port = 80
        if "/" in url:
            host, sub_path = url.split("/", 1)
            path += sub_path
        if ":" in host:
            host, port = host.split(":")
        return host, path, int(port)

    def reset_socket(self):
        self.socket.close()
        self.open_socket()

    def open_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(args)
        else:
            return self.GET(url)

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )
