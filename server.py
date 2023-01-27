#  coding: utf-8 
import socketserver
import urllib.request
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def setup(self):
        self.paths = []
        self.directories = []
        # create a list of all paths in www directory
        for root, dirs, files in os.walk("www"):
            for file in files:
                self.paths.append(os.path.join(root, file)) # all paths in www directory
        for i in range(len(self.paths)): # remove www from all paths
            self.paths[i] = self.paths[i][3:]

        # create a list of all directories in www directory
        for root, dirs, files in os.walk("www"):
            for dir in dirs:
                self.directories.append(os.path.join(root, dir))
        for i in range(len(self.directories)): # remove www from all paths
            self.directories[i] = self.directories[i][3:]
    
    def handle(self): # GET
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        request_tokenized = (str(self.data)).split()
        if request_tokenized[0] != "b'GET": # if not GET respond with 405
            response = b'HTTP/1.1 405 Method Not Allowed\r\n'
            b'Connection: close\r\n'
        
        else:  # handle get request
            path = request_tokenized[1]
            # if path ends with /, change to /index.html
            if path[-1] == "/":
                path += "index.html"
            if path not in self.paths: 
                if path not in self.directories:  # if path not in www respond with 404
                    response = b'HTTP/1.1 404 Not Found\r\n'
                    b'Connection: close\r\n'
                else:  # if path is directory respond with 301 and redirect
                    response = b'HTTP/1.1 301 Moved Permanently\r\n'
                    response += b'Location: http://localhost:8080' + bytes(path, 'utf-8') + b'/\r\n'
                    response += b'Connection: close\r\n'
            else:  # if path in www
                extension = path.split(".")[-1]
                if extension == "css":
                    response = b'HTTP/1.1 200 OK\r\n'
                    # response += b'Content-Encoding: gzip\r\n'
                    response += b'Content-Type: text/css; charset=utf-8\r\n'
                    # response += b'Transfer-Encoding: gzip\r\n'
                    # response += b'Connection: close\r\n'
                    response += b'\r\n'
                elif extension == "html":
                    response = b'HTTP/1.1 200 OK\r\n'
                    # response += b'Content-Encoding: gzip\r\n'
                    response += b'Content-Type: text/html; charset=utf-8\r\n'
                    # response += b'Transfer-Encoding: gzip\r\n'
                    # response += b'Connection: close\r\n'
                    response += b'\r\n'
                else:
                    response = b'HTTP/1.1 200 OK\r\n'
                    b'Content-Encoding: gzip\r\n'
                    b'Content-Type: application/octet-stream; charset=utf-8\r\n'
                    b'Transfer-Encoding: gzip\r\n\r\n\r\n'
                    b'Connection: close\r\n'
                    b'\r\n'
                with open("www"+path, 'rb') as f:
                    response += f.read()
        print(response)
        self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)


    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
