import socket
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import json

def comm(clntSock, clntAddr, clntExist):
    
    # while True:

    requestRaw = clntSock.recv(1024) #1024byte를 받는다.최대값은 65535 

    
    if requestRaw == b'': # if connection is closed from client
        print(f"Closed signal from the client: {clntAddr}")

    requestMsg = requestRaw.decode()
    print(f"Request Message:@@ {requestMsg}@@")
    request_arr=requestMsg.split()
    request_method=request_arr[0]#"GET" or "POST"
    request_version=request_arr[2]#"1.1? 2? 등등
    contlen=0
    sumnow=0
    if(request_method=="POST"):
        '''
        for idx,val in enumerate(request_arr):
            #print(idx,val)
            if(val=="Content-Length:"):
                #print("idx:"+str(idx))
                contlen=request_arr[idx+1]
        '''
        header_fin_string="\r\n\r\n"
        header_fin_idx=requestMsg.find(header_fin_string)
        #print(requestMsg.find(header_fin_string))
        bodystr=requestMsg[header_fin_idx+4:]#이게 post로 넘어온 json
        print("body@@"+bodystr+"@@")
        #json array인 경우
        '''
        jsonobj=json.loads(bodystr)
        jsonarray=jsonobj.get("room_li")
        for val in jsonarray:
            print(val)
        '''
        #일반 json의 경우
        #bodystr=={'outer': { 'inner': 'value'}} 인상황
        jsonobj=json.loads(bodystr)
        print("딕셔너리@@"+str(jsonobj)+"@@") #딕셔너리형태로 출력
        print("outer의 value는 @@"+str(jsonobj.get("outer"))+"@@")
        print("inner의 value는 @@"+str(jsonobj.get("inner"))+"@@") #이렇게하면 none출력
        print("inner의 value는 @@"+str(jsonobj.get("outer").get("inner"))+"@@")#이렇게해야 inner의 value출력 
    #if(request_method=="POST"):

    #postcontent=clntSock.recv(int(contlen))
    #print("postcont:@@"+str(postcontent)+"@@")
    #print(request_version) # HTTP/1.1

    if request_method == "GET":
        responseMsg = '{\"code\":\"HI\"}'
        contlen=len(responseMsg)
        response_header = "{0} 200 OK\r\nServer: {1}\r\nContent-length:{2}\r\nKeep-Alive: timeout=5, max=100\r\nContent-type:text/html\r\n\r\n".format(request_version, SERVER_NAME,contlen)
        response_header+=responseMsg    
    elif request_method=="POST":        
        responseMsg = '{\"code\":\"HI\"}'
        contlen=len(responseMsg)
        response_header = "{0} 200 OK\r\nServer: {1}\r\nContent-length:{2}\r\nKeep-Alive: timeout=5, max=100\r\nContent-type:text/html\r\n\r\n".format(request_version, SERVER_NAME,contlen)
        response_header+=responseMsg  
    else:
        response_header = "{0} 405 Method Not Allowed\r\nServer: {1}\r\nContent-length:{2}\r\nKeep-Alive: timeout=5, max=100\r\nContent-type:text/html\r\n\r\n".format(request_version, SERVER_NAME,contlen)
    
    clntSock.send(response_header.encode())
    clntSock.close()
def comm_th(clntSock, clntAddr, clntExist):
    thread = threading.Thread(target=comm, args=(clntSock, clntAddr, clntExist))
    thread.start()
    thread.join()

# Global variables
SERVER_NAME = "Capstone Design Project"
MAX_PENDING = 10

# Change the current working directory
base = os.path.dirname(os.path.abspath(__file__))
os.chdir(base)

# Open a temporary socket to get IP address of this server
tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tempSock.connect(('google.com', 80))
servIP = tempSock.getsockname()[0]
tempSock.close()

# Check if arguments are valid
'''
if len(sys.argv) != 2:
    print(f"Usage: {os.path.basename(sys.argv[0])} <Server Port>")
    sys.exit(0)
'''
servPort = int(10080)

# Create server socket
servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # To reuse the previous server port, even if the serversocket is closed abnormally.
servSock.bind(('', servPort)) # '' means that the socket can be connected to any address on the system
servSock.listen(MAX_PENDING)

print(f"Server address = {servIP}:{servPort}")
print("Server is ready to receive ...\n")

clntExist = [] # To trace all of the accepted sockets
while True:
    clntSock, clntAddr = servSock.accept()
    clntExist.append(clntAddr)
    print(f"Accepted socket = {clntAddr[0]}:{clntAddr[1]}") # Accepted address changes for each clients.
    print(f"Existing Sockets = {clntExist}")
    comm_th(clntSock, clntAddr, clntExist)
