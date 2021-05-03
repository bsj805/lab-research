import sys, os
import socket, threading
import json, hashlib, pymysql
import time, random

SERVER_NAME = "Capstone Design Project"
SERVER_PORT = 10080
SERVER_IP: tuple = None

MAX_PENDING = 10
RCV_SIZE = 1024
OFFSET = 52000

CLNTLIST = dict()
ROOMLIST = dict()

capstone_db = pymysql.connect(
    user='capstone', 
    passwd='capstone0901', #pw입력
    host='101.101.208.192', 
    db='capstone',
    charset='utf8'
)

class CLIENT:
    def __init__(self, sock: socket.socket, addr: tuple):
        self.sock = sock
        self.addr = addr

class MESSAGE:
    def __init__(self, rqst: bytes):
        temp, self.rqstbody = rqst.decode().split('\r\n\r\n')
        self.rqsthead = temp.split('\r\n')
        self.method, _, self.ver = self.rqsthead[0].split(' ')

        self.code = ""
        self.user_num = -1
        try:
            self.rqstjson: dict = json.loads(self.rqstbody)
            self.code: str = self.rqstjson['code']
            self.user_num: int = self.rqstjson['user_num']
        except:
            pass
        

    def rspn(self, status: int, body: str) -> bytes:
        if status == 200:
            temp = "200 OK"
        else:
            temp = "400 Bad Request"
        head = '\r\n'.join([
            f"{self.ver} {temp}",
            f"Server: {SERVER_NAME}",
            f"Content-length:{len(body)}",
            f"Keep-Alive: timeout=5, max=100",
            f"Content-type:text/html"
        ])
        return '\r\n\r\n'.join([head, body]).encode()



def main():
    tempsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tempsock.connect(('google.com', 80))
    SERVER_IP = tempsock.getsockname()[0]
    print(f"Server address is {SERVER_IP}:{SERVER_PORT}")
    tempsock.close()

    servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 포트 강제 재사용을 위한 코드
    servsock.bind(('', SERVER_PORT)) # ''은 시스템에 있는 모든 주소로 소켓에 연결할 수 있음을 의미
    servsock.listen(MAX_PENDING)
    print(f"Now ready to accept clients ...\n")

    while True:
        newsock, newaddr = servsock.accept()
        print(f"OPEN: {newaddr}")
        threading.Thread(target=conn, args=(newsock, newaddr)).start()

def conn(thissock: socket.socket, thisaddr: tuple):

    while True:
        rqst = thissock.recv(RCV_SIZE)
        if rqst == b"":
            break

        msg = MESSAGE(rqst)
        print(msg.rqsthead)
        print(msg.rqstbody)

        if msg.method != "POST":
            print(1)
            thissock.send(msg.rspn(400, "The request message is not POST method"))

        # 통신규약: https://docs.google.com/document/d/125qbejSf1V16Lu_sIbwM8bVvS9V9E5JpAm-uBYYDuJ8/edit

        elif  msg.user_num not in CLNTLIST: # 로그인 하지 않은 사람의 요청 

            if msg.code == "REQUEST_LOGIN": # 로그인을 요청했을 시
                print(2)
                status, rspnbody = REQUEST_LOGIN(msg.rqstjson['user_id'], msg.rqstjson['user_pw'])
                ### Need Semaphore ###
                CLNTLIST[msg.user_num] = CLIENT(thissock, thisaddr) # add CLIENT object to CLNTLIST
                thissock.send(msg.rspn(status, rspnbody))

            if msg.code == "REQUEST_REG": # 가입을 요청했을 시
                print(3)
                status, rspnbody = REQUEST_REG(msg.rqstjson['user_id'], msg.rqstjson['user_pw'], msg.rqstjson['email'])
                thissock.send(msg.rspn(status, rspnbody))
            
            # if msg.code == "REQUEST_DEACTIVATE": # 탈퇴를 요청했을 시
            #     status, rspnbody = REQUEST_DEAVTIVATE(msg.rqstjson['user_id'], msg.rqstjson['user_pw'])
            #     thissock.send(msg.rspn(status, rspnbody))
            
            else:
                print(4)
                thissock.send(msg.rspn(400, "Not logged in"))
        

        else: # 로그인 한 사람의 요청
            print(5)

            # elif msg.code == "REQUEST_LOGOUT": # 안 정해졌음
            # ...
            #     rspnbody: str = REQUEST_LOGOUT(msg.usernum)
            #     del CLNTLIST[msg.user_num] # remove CLIENT object from CLNTLIST
            thissock.send(msg.rspn(400, "Already logged in"))

        del msg
    
    thissock.close()
    print(f"CLOSE: {thisaddr}")

# pymysql 사용 방법: http://pythonstudy.xyz/python/article/203-MySQL-DML

def REQUEST_LOGIN(user_id: str, user_pw: str) -> str:
    try:
        curs = capstone_db.cursor(pymysql.cursors.DictCursor)

        sql_sel = f"SELECT * FROM `user` WHERE `user_id` = '{user_id}' ;"
        curs.execute(sql_sel)
        
        result: dict = curs.fetchall()[0]
        hashed: str = hashlib.sha256(user_pw.encode()).hexdigest()
        if(hashed != result["user_pw"]):
            raise Exception
        else:
            del result["user_pw"] # user_pw는 미리 지워 놓기

    except:
        print("REQUEST_LOGIN EXCEPTION")
        rspnjson: dict = {'code': "FAILED_LOGIN"}
        status = 400

    else:
        print("REQUEST_LOGIN ELSE")
        rspnjson: dict = {**{'code': "SUCCESS_LOGIN"}, **result} # 딕셔너리를 병합하는 방법: c = {**a, **b}
        # rspnjson['room_li'] = [
        #     {"room_name": ROOM.name, "room_num": ROOM.number, "room_member": list(ROOM.clnts.keys())} for ROOM in ROOMLIST.values()
        #     ]
        status = 200
    
    finally:
        rspnbody = str(json.dumps(rspnjson))
        return status, rspnbody


def REQUEST_REG(user_id: str, user_pw: str, email: str):
    try:
        curs = capstone_db.cursor(pymysql.cursors.DictCursor)

        sql_sel = f"SELECT * FROM `user` WHERE `user_id` = '{user_id}' ;"
        curs.execute(sql_sel)
        result: list = curs.fetchall()
        if len(result) > 0:
            raise Exception

        ### Need Semaphore ###
        hashed: str = hashlib.sha256(user_pw.encode()).hexdigest()
        sql_reg = f"INSERT INTO `user` (user_id, user_pw, user_email) VALUES ('{str(user_id)}' , '{hashed}' , '{str(email)}') ;"
        curs.execute(sql_reg)
        capstone_db.commit()

    except:
        print("REQUEST_REG EXCEPTION")
        rspnjson: dict = {'code': "FAILED_REG"}
        status = 400
    
    else:
        print("REQUEST_REG ELSE")
        rspnjson: dict = {'code': "SUCCESS_REG"}
        rspnjson['user_id'], rspnjson['user_pw'], rspnjson['email'] = user_id, user_pw, email
        status = 200
    
    finally:
        rspnbody = str(json.dumps(rspnjson))
        return status, rspnbody
        

if __name__ == "__main__":
    main()