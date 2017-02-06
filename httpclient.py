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

    def __str__(self):
        return "%s\n%s" % (self.code, self.body)

class Request(object):
    def __init__(self, method, path, host):
        self.headers = {"Host" : host, "Accept" : "*/*", "Connection" : "close"}
        self.method = method
        self.path = path
        self.body = ""
        self.end = "\r\n"

    def set_body(self, body):
        self.body = body
        self.headers["Content-Length"] = len(bytearray(body))
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"

    def build(self):
        status =  "%s %s HTTP/1.1" % (self.method, self.path)
        headers = self.end.join(["%s: %s" % (k, v) for k, v in self.headers.iteritems()])

        return "%s\r\n%s\r\n\r\n%s" % (status, headers, self.body)

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

    def GET(self, url, args={}):
        host, path, port = self.parse_url(url)
        self.connect(host, port)
        path += urllib.urlencode(args)
        path = urllib.url2pathname(path)
        request = Request("GET", path, host)
        self.socket.sendall(request.build())
        raw_response = self.recvall(self.socket)
        code = self.get_code(raw_response)
        body = self.get_body(raw_response)
        self.reset_socket()
        response = HTTPResponse(code, body)
        if (code == "301" or code == "302"):
            return self.redirect(raw_response, response)
        return response

    def redirect(self, response, three_o_response):
        new_url = self.parse_redirect(response)
        if new_url.startswith("https"):
            return three_o_response
        return self.GET(new_url)

    def parse_redirect(self, response):
        headers = response.split("\r\n\r\n")[0]
        location = filter(lambda x: x.startswith("Location: "), headers.split("\r\n"))[0]
        new_url = location.split()[1]
        return new_url

    def POST(self, url, args={}):
        host, path, port = self.parse_url(url)
        self.connect(host, port)
        request = Request("POST", path, host)
        request.set_body(self.build_body(args))
        self.socket.sendall(request.build())
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.reset_socket()
        return HTTPResponse(code, body)

    def build_body(self, args):
        return urllib.urlencode(args)

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

    def command(self, url, command="GET", args={}):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

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
