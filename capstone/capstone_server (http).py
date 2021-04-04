import socket
import os
import sys
import threading

def comm(clntSock, clntAddr, clntExist):
    
    # while True:

    requestRaw = clntSock.recv(1024)

    if requestRaw == b'': # if connection is closed from client
        print(f"Closed signal from the client: {clntAddr}")

    requestMsg = requestRaw.decode()
    print(f"Request Message: {requestMsg}")

    responseMsg = "Hello world!"
    clntSock.sendall(responseMsg.encode())
    
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
if len(sys.argv) != 2:
    print(f"Usage: {os.path.basename(sys.argv[0])} <Server Port>")
    sys.exit(0)

servPort = int(sys.argv[1])

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