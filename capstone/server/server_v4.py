import socket
import os
import sys
import threading
import json
import hashlib
import time
import random
import pymysql
from collections import OrderedDict
    # https://docs.python.org/ko/3/library/collections.html#collections.OrderedDict

main_db = pymysql.connect(
    user='capstone', 
    passwd='capstone0901', #pw입력
    host='101.101.208.192', 
    db='capstone', 
    charset='utf8'
)
cursor=main_db.cursor(pymysql.cursors.DictCursor)
class sdict(): # dict with semaphore
    
    def __init__(self, iterable=dict()):
        # s는 semaphore
        self.d = iterable
        self.s = threading.BoundedSemaphore(1) # s의 초기값 1, 항상 0 <= s <= 1

    def __setitem__(self, key, val):
        self.s.acquire() # s가 1만큼 감소
        self.d[key] = val
        self.s.release() # s가 1만큼 증가
    
    def __getitem__(self, key):
        return self.d[key]
    
    def __delitem__(self, key):
        del self.d[key]
    
    def __str__(self):
        return str(self.d)

    def __len__(self):
        return len(self.d)
    
    def keys(self):
        return self.d.keys()

    def values(self):
        return self.d.values()

    def items(self):
        return self.d.items()




# Globally shared resources

CLNTLIST = sdict() # {user_num: CLIENT}
ROOMLIST = sdict() # {number: ROOM}
    # CLNTLIST[user_num] 하면 user_num에 해당하는 CLIENT 객체를 리턴
    # ROOMLIST[number] 하면 number 해당하는 ROOM 객체를 리턴



class CLIENT: # client class
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.is_ready = 0 # 레디 상태
        self.number = -1 # 로그인 시 결정
        self.name = "" # 로그인 시 결정
        self.cards = []
        self.score=0
        ############변경
        self.readytime=None # 얼마나 레디안했는지.
        self.waittime=None # 대기실에서 heartbeat얼마나 안보냈는지
        self.roomno = -1 # 몇번방에 속해있는지.
        self.totaltime=None # 아무 메시지도 안보낸채로 30분 이상  (timestamp확인)
        self.totalcnt=None # 총 라운드 수
        self.answer=None # 정답을 맞춘 횟수
        self.similarcnt=None # 다른사람이랑 같은 것을 찍은 경우 
        self.totaltellercnt=None # 텔러가 된 횟수
        self.tellerwin=None # 텔러일때 다른사람이 내것을 맞춘 횟수
        self.nontellerwin=None # 텔러가 아닌데 다른사람이 내 것을 픽한 횟수
        self.curteller=False

class ROOM: # room class
    NUMBER = 0 # 방 번호 
    SEMAPHORE = threading.BoundedSemaphore(1)
        # 방 번호 지정을 위해서 모든 ROOM 객체들이 공유하는 세마포어

    def __init__(self, host, name, maxclnt):
        # 방 생성 시 newroom = ROOM(user_num, room_name, room_user) 로 생성됨
        
        # 방 정보 초기화
        self.host = host # name이 아니라 num임
        self.name = name
        self.maxclnt = maxclnt

        # 방 번호 정해주기, 0번부터 시작
        ROOM.SEMAPHORE.acquire()
        self.number = ROOM.NUMBER; ROOM.NUMBER += 1
        ROOM.SEMAPHORE.release()

        # 방에 있는 사람 목록 만들기
        self.clnts = sdict()
        self.clnts[host] = CLNTLIST[host]
            # room.clnts[user_num]은 user_num에 해당하는 CLIENT 객체를 리턴
        self.curteller=0
        # 기타 정보
        self.curkeyword = "" # 이 방의 현재 키워드
        self.curstage = 0
            # 0:대기실 타이머, 1:텔러가 키워드 선정중, 2: 키워드를 보고서 카드뽑는중, 3: 투표중 4: 게임끝
        self.timestamp = time.time() # 타임 스탬프
        self.visited = [] # 카드 분배 용 리스트
        self.clntorder = [] # 텔러 순서를 정하기 위한 리스트
        self.s = threading.BoundedSemaphore(1) # 각 방마다 존재하는 세마포어
        self.templist=[]
        



# Predefined variables

SERVER_NAME = "Capstone Design Project"
SERVER_PORT = 10080
MAX_PENDING = 10
RCV_SIZE = 1024
SERVER_IP = None # run()에서 결정
SERVER_SOCK = None # run()에서 결정
ALLCARDS = [i for i in range(106)] # 각각이 번호, 총 106개고 0~105번임
WAIT_VALUE=30 #heartbeat안보낸지 30초
READY_WAIT_VALUE=120 #ready신호안보낸지 120초
TOTAL_WAIT_VALUE=60*10 #아무 메시지 안보낸지 10분
KEYWORD_WAIT_VALUE=30 #키워드 선정에 30초
CARD_WAIT_VALUE=30 #카드 선정에 30초
CARD_VOTE_VALUE=30 #카드 투표에 30초
MINIMUM_PLAYER=3 #최소플레이어수 3명

# Server Run

def run():
    # 작업 경로 변경
    base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base)

    # IP define
    tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tempSock.connect(('google.com', 80))
    SERVER_IP = tempSock.getsockname()[0] 
    tempSock.close()
    print(f"Server address is {SERVER_IP}:{SERVER_PORT}")

    # SOCK define
    SERVER_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER_SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 포트 강제 재사용을 위한 코드
    SERVER_SOCK.bind(('', SERVER_PORT)) # ''은 시스템에 있는 모든 주소로 소켓에 연결할 수 있음을 의미
    SERVER_SOCK.listen(MAX_PENDING)
    print(f"Server is now ready to accept clients ...\n")

    while True:
        newsock, newaddr = SERVER_SOCK.accept()
        newclnt = CLIENT(newsock, newaddr)
        # CLNTLIST.append(newclnt)
        print(f"Accepted socket from {newaddr}")
        # print(f"Now existing {len(CLNTLIST)} sockets\n")
        threading.Thread(target=comm, args=(newclnt,)).start()
        

def comm(clnt):

    while True:
        rqst = clnt.sock.recv(RCV_SIZE)
        
        if rqst == b'': # client로부터 빈 request가 들어올 때 (ex. 탭 닫기)
            print(f"Disconnection from {clnt.addr}")
            break
        
        # 수신한 request 보여주기
        rqstMsg = rqst.decode()
        print(f"Request Message is below ...\n{rqstMsg}@End of Message")

        # request 정보 확인
        temp, rqstBody = rqstMsg.split('\r\n\r\n')
        rqstHead = temp.split('\r\n')
        rqstMethod, _, rqstVer = rqstHead[0].split(' ')

        # request가 POST가 아니면 에러 코드 보내기
        if rqstMethod != "POST":
            
            rspnBody = "The request message is not POST method"
            rspnHead = '\r\n'.join([
                f"{rqstVer} 400 Bad Request",
                f"Server: {SERVER_NAME}",
                f"Content-length:{len(rspnBody)}",
                f"Keep-Alive: timeout=5, max=100",
                f"Content-type:text/html"
            ])

        # POST라면 처리 후 응답
        else:
            rqstJson = json.loads(rqstBody)
            if rqstJson['code']!="REQUEST_TIMER":
                if('user_num' in rqstJson.keys()): #user_num을 전달하는애라면
                    usnum=rqstJson['user_num']
                    if (usnum in CLNTLIST.values()):
                        ourcl=CLNTLIST[usnum]
                        ourcl.sock=clnt.sock
                        ourcl.addr=clnt.addr
                        
            
            if rqstJson['code']=="REQUEST_LOGIN":
                usid, uspw= rqstJson['user_id'], rqstJson['user_pw']
                rspnHead, rspnBody = REQUEST_LOGIN(usid, uspw,clnt,rqstVer)

            elif rqstJson['code']=="REQUEST_REGISTER":
                usid,uspw,usem,usnm=rqstJson['user_id'], rqstJson['user_pw'], rqstJson['email'],rqstJson['user_name']
                rspnHead, rspnBody = REQUEST_REG(usid, uspw, usem,usnm,rqstVer)
            
            elif rqstJson['code'] == "REQUEST_ROOM_CREATE":
                user_num, room_name, room_user = rqstJson['user_num'], rqstJson['room_name'], rqstJson['room_user']
                rspnHead, rspnBody = REQUEST_ROOM_CREATE(user_num, room_name, room_user,rqstVer)
            
            elif rqstJson['code'] == "REQUEST_ROOM_INFO":
                rspnHead, rspnBody = REQUEST_ROOM_INFO(rqstJson)

            elif rqstJson['code']=="REQUEST_READY":
                user_num = rqstJson['user_num']
                rspnHead, rspnBody = REQUEST_READY(user_num)
            elif rqstJson['code']=="REQUEST_TIMER":
                rspnHead,rspnBody=REQUEST_TIMER(rqstJson,rqstVer)
            elif rqstJson['code']=="REQUEST_EXIT":
                rspnHead,rspnBody=REQUEST_EXIT(rqstJson,rqstVer):
            elif rqstJson['code']=="REQUEST_ROOM_JOIN":
                rspnHead,rspnBody=REQUEST_ROOM_JOIN(rqstJson,rqstVer)
            elif rqstJson['code']=="REQUEST_TIMER":
                rspnHead,rspnBody=REQUEST_TIMER( rqstJson,rqstVer)
            ##카드 제출, 카드 투표, 게임 종료시 대기실 화면으로 연결시켜주는메시
                    
            else:
                rspnBody = "The JSON code is not available"
                rspnHead = '\r\n'.join([
                    f"{rqstVer} 400 Bad Request",
                    f"Server: {SERVER_NAME}",
                    f"Content-length:{len(rspnBody)}",
                    f"Keep-Alive: timeout=5, max=100",
                    f"Content-type:text/html"
                ])

        rspnMsg = '\r\n\r\n'.join([rspnHead, rspnBody])
        clnt.sock.send(rspnMsg.encode())
    
    
    #del CLNTLIST[clnt.number]
    clnt.sock.close()
    print(f"Now existing {len(CLNTLIST)} sockets\n")








def REQUEST_LOGIN(user_id,user_pw,oneclnt,rqstVer):
    error=False
    retusernum=0
    retid=0
    retscore=0
    retname=""
    try:
        sql_sel="SELECT * FROM `user` WHERE `user_id` = \""+user_id+"\" ; "
        cursor.execute(sql_sel)
        result=cursor.fetchall()
        retusernum=result[0]["usernum"]
        retid=result[0]["user_id"]
        retscore=result[0]["user_score"]
        retpw=result[0]["user_pw"]
        retname=result[0]["user_name"]
        a=str(user_pw)
        ahashed=hashlib.sha256(a.encode())
        ahashedstr=ahashed.hexdigest()
        if(ahashedstr!=retpw):
            error=True
    except Exception as e:
        print("exception:",end="")
        print(e,end="")
        print("@@")
        error=True
    finally:
        group_data=OrderedDict()
        room_li=OrderedDict()
        if error:
            group_data["code"]="FAILED_LOGIN"
        else:
            group_data["code"]="SUCCESS_LOGIN"
        group_data["user_name"]=str(retid)
        group_data["user_num"]=str(retusernum)
        group_data["user_score"]=str(retscore)
        group_data["user_name"]=str(retname)
        temp=[]
        if error:
            room_li["room_name"]="0"
            room_li["room_no"]="0"
            room_li["room_member"]="0"
            temp.append(room_li)
        else:
            oneclnt.number=retusernum
            oneclnt.name=retname
            oneclnt.totaltime=time.time()
            oneclnt.score=retscore
            CLNTLIST[retusernum]=oneclnt
            for room in ROOMLIST.values():
                room_li["room_name"]=room.name
                room_li["room_no"]=str(room.number)
                room_li["room_member"]=str(len(room.clnts))+"/"+str(room.capacity)
                temp.append(room_li)
                room_li=OrderedDict()
        group_data["room_li"]=temp
        msgstr=str(json.dumps(group_data,ensure_ascii=False,indent="\t"))
        rspnHead = '\r\n'.join([
                        f"{rqstVer} 200 OK",
                        f"Server: {SERVER_NAME}",
                        f"Content-length: {len(msgstr)}",
                        f"Keep-Alive: timeout=5, max=100",
                        f"Content-type: text/html"
                        ])
        return rspnHead,msgstr


def REQUEST_REG(user_id,user_pw,user_email,user_name,rqstVer):
    sql_reg="INSERT INTO `user` (user_id,user_pw,user_email,user_name) VALUES (\""+str(user_id)+"\" , \""+str(user_pw)+"\" , \""+str(user_email)+"\" , \""+str(user_name)+"\" );"
    retusernum=0
    retid=0
    retscore=0
    error=False
    try:
        cursor.execute(sql_reg)
        main_db.commit()       
        sql_sel="SELECT * FROM `user` WHERE `user_id` = \""+user_id+"\" ; "
        cursor.execute(sql_sel)
        result=cursor.fetchall()
        retusernum=result[0]["usernum"]
        a=str(retusernum+52000)
        ahashed=hashlib.sha256(a.encode())
        ahashedstr=ahashed.hexdigest()
        if(str(user_pw)==str(user_email)=="0"): #guest_login시에는
            sql_update="UPDATE `user` SET `user_id` = \""+str(retusernum+39000)+"\", `user_pw` = \""+ahashedstr+"\", `user_name` = \""+str(retusernum+39000)+"\" WHERE `usernum`= \""+str(retusernum)+"\""
            cursor.execute(sql_update)
            main_db.commit()
            sql_sel="SELECT * FROM `user` WHERE `usernum` = \""+str(retusernum)+"\" ; "
        else:
            a=user_pw
            ahashed=hashlib.sha256(a.encode())
            ahashedstr=ahashed.hexdigest()
            sql_update="UPDATE `user` SET  `user_pw` = \""+ahashedstr+"\" WHERE `usernum`= \""+str(retusernum)+"\""
            cursor.execute(sql_update)
            main_db.commit()
        cursor.execute(sql_sel) #guestlogin때문에 다시받아오고
        result=cursor.fetchall()    
        retid=result[0]["user_id"]
        retscore=result[0]["user_score"]
    except Exception as e:
        print("exception:",end="")
        print(e,end="")
        print("@@")
        error=True
    finally:
        group_data=OrderedDict()
        room_li=OrderedDict()
        if error:
            group_data["code"]="FAILED_REGISTER"
        else:
            group_data["code"]="SUCCESS_REGISTER"
        group_data["user_name"]=str(retid)
        group_data["user_num"]=str(retusernum)
        group_data["user_score"]=str(retscore)
        temp=[]
        if error:
            room_li["room_name"]="0"
            room_li["room_no"]="0"
            room_li["room_member"]="0"
            temp.append(room_li)
        else:
            for room in ROOMLIST.values():
                room_li["room_name"]=room.name
                room_li["room_no"]=str(room.number)
                room_li["room_member"]=str(len(room.clnts))+"/"+str(room.capacity)
                temp.append(room_li)
                room_li=OrderedDict()
        group_data["room_li"]=temp
        msgstr=str(json.dumps(group_data,ensure_ascii=False,indent="\t"))
        rspnHead = '\r\n'.join([
                        f"{rqstVer} 200 OK",
                        f"Server: {SERVER_NAME}",
                        f"Content-length: {len(msgstr)}",
                        f"Keep-Alive: timeout=5, max=100",
                        f"Content-type: text/html"
                        ])
        return rspnHead,msgstr


def REQUEST_ROOM_CREATE(user_num, room_name, room_user):
    try:
        # ROOM의 생성자는 __init__(self, host, name, maxclnt)
        newroom = ROOM(user_num, room_name, room_user)
        ROOMLIST[newroom.number] = newroom # ROOMLIST 갱신
        CLNTLIST[user_num].roomno = newroom.number # CLIENT 객체 갱신
        ######################################################
        ######################
        """ SUCCESS_ROOM_CREATE response 리턴 """
        return NotImplemented, NotImplemented
    except:
        """ FAILED_ROOM_CREATE response 리턴 """
        return NotImplemented, NotImplemented

def REQUEST_EXIT(rqstJson,rqstVer):
    us=rqstJson['user_num']
    ro=rqstJson['room_no'] #room
    if( ro in ROOMLIST):
        myroom=ROOMLIST[ro]
        del myroom.clnts[us]

        if(len(myroom.clnts)==0):
            del ROOMLIST[ro]
        elif(myroom.host==us):
            for cln in myroom.clnts.values():        #내가 방장이면 방장넘겨야해
                break
            myroom.host=cln.number
            
            
    CLNTLIST[us].roomno=-1
    error=False
    temp=[]
    group_data=OrderedDict()
    room_li=OrderedDict()
    if error:
        group_data["code"]="FAILED_EXIT"
    else:
        group_data["code"]="SUCCESS_EXIT"
    group_data["user_name"]=str(rqstJson['user_name'])
    group_data["user_num"]=str(rqstJson['user_num'])
    group_data["user_score"]=str(rqstJson['user_score'])
    for room in ROOMLIST.values():
                room_li["room_name"]=room.name
                room_li["room_no"]=str(room.number)
                room_li["room_member"]=str(len(room.clnts))+"/"+str(room.capacity)
                temp.append(room_li)
                room_li=OrderedDict()
    group_data["room_li"]=temp
    msgstr=str(json.dumps(group_data,ensure_ascii=False,indent="\t"))
    rspnHead = '\r\n'.join([
                        f"{rqstVer} 200 OK",
                        f"Server: {SERVER_NAME}",
                        f"Content-length: {len(msgstr)}",
                        f"Keep-Alive: timeout=5, max=100",
                        f"Content-type: text/html"
                        ])
    return rspnHead,msgstr
def REQUEST_ROOM_INFO(rqstJson):
    try:
        """ SUCCESS_ROOM_INFO 리턴 """
        return NotImplemented, NotImplemented
    except:
        """ FAILED_ROOM_INFO 리턴 """
        return NotImplemented, NotImplemented

def REQUEST_ROOM_JOIN(rqstJson,rqstVer):
    user_num=rqstJson['user_num']
    thisclnt=CLNTLIST[user_num]
    thisroom_no=rqstJson['room_no']
    error=0
    retroom_name="0"
    retroom_no="0"
    retroom_user="0" #최대명수
    user_li="0"
    retroom_host="0"
    if thisroom_no in ROOMLIST:
        thisroom=ROOMLIST[rqstJson['room_no']]
        retroom_name=thisroom.name
        retroom_no=thisroom_no
        retroom_user=thisroom.maxclnt
        retroom_host=thisroom.host
    else:
        error=1
    if(len(thisroom.clnts)>= thisroom.maxclnt or thisroom.curstage>0):
        error=1
        retroom_name="0"
        retroom_no="0"
        retroom_user="0"
        retroom_host="0"
    else:
        thisclnt.roomno=rqstJson['room_no']
        thisclnt.readytime=time.time()
        thisclnt.waittime=time.time()
        thisclnt.is_ready=0
    group_data=OrderedDict()
    user_li=OrderedDict()
    group_data["user_num"]=user_num
    group_data["room_name"]=retroom_name
    group_data["room_no"]=retroom_no
    group_data["room_user"]=retroom_user
    group_data["room_host"]=retroom_host
    if error==1:
        group_data["code"]="FAILED_ROOM_JOIN"
        group_data["user_li"]="0"
    else:
        temp=[]
        for user in thisroom.clnts.values():
            user_li["user_name"]=user.name
            user_li["user_num"]=user.number
            user_li["user_score"]=user.score
            user_li["is_ready"]=user.is_ready
            temp.append(user_li)
            user_li=OrderedDict()
    group_data["user_li"]=temp
    msgstr=str(json.dumps(group_data,ensure_ascii=False,indent="\t"))
    rspnHead = '\r\n'.join([
                        f"{rqstVer} 200 OK",
                        f"Server: {SERVER_NAME}",
                        f"Content-length: {len(msgstr)}",
                        f"Keep-Alive: timeout=5, max=100",
                        f"Content-type: text/html"
                        ])
    return rspnHead,msgstr
  #이제 response message

def REQUEST_READY(user_num):
    thisclnt = CLNTLIST[user_num]
    thisroom = ROOMLIST[thisclnt.roomno]

    if thisclnt.is_ready == 2: # 게임 중일 때는 무시
        return 

    thisroom.s.acquire()
    if thisroom.host == thisclnt.number: # 요청한 사람이 host일 때
        try:
            if sum([clnt.is_ready for clnt in thisroom.clnts]) == len(thisroom.clnts): # all ready
                
                for clnt in thisroom.clnts:
                    clnt.is_ready = 2
                thisroom.visited = [i for i in range(108)] # 새로 생성 후 섞음
                random.shuffle(thisroom.visited)
                thisroom.clntorder = [user_num for clnt in thisroom.clnts] # teller 선정을 위함
                """ SUCCESS_START 리턴 """ # SUCCESS_READY 아님
                thisroom.s.release()
                ###########################################################################
                ##################self.readytime=time.time() 찍어야한다. ready안한지 2분넘으면 강퇴
                ##################self.waittime=time.time() time찍고 (waittime은 타이머 올때마다 초기화되는애)
                return NotImplemented, NotImplemented
            else:
                """ FAILED_READY 리턴 """
                thisroom.s.release()
                return NotImplemented, NotImplemented
        except:
            """ FAILED_START 리턴 """
            thisroom.s.release()
            return NotImplemented, NotImplemented

    
    else: # 요청한 사람이 host가 아닐 때
        try:
            thisclnt.is_ready = 1 - thisclnt.is_ready # not all ready
            """ SUCCESS_READY 리턴 """
            return NotImplemented, NotImplemented
        except:
            """ FAILED_READY 리턴 """
            return NotImplemented, NotImplemented


def REQUEST_CARD(user_num):
    thisclnt = CLNTLIST[user_num]
    thisroom = ROOMLIST[thisclnt.roomno]
    try:
        # visited에서 각자 앞에서부터 6개씩 뽑아가는 컨셉
        thisroom.s.acquire()
        thisclnt.cards = thisroom.visited[:6]
        thisroom.visited = thisroom.visited[6:]
        thisroom.s.release()
        """ SUCCESS_CARD 리턴""" # thisclnt.cards 정보로 리턴
        return NotImplemented, NotImplemented
    except:
        """ FAILED_CARD 리턴"""
        return NotImplemented, NotImplemented

def REQUEST_WHO_IS_TELLER(room_num):
    thisroom = ROOMLIST[room_num]
    thisroom.curstage = 1
    try:
        teller_num = thisroom.clntorder.pop()
        thisroom.clntorder.insert(0, teller_num)
        """ SUCCESS_WHO_IS_TELLER """
        return NotImplemented, NotImplemented
    except:
        """ FAILED_WHO_IS_TELLER """
        return NotImplemented, NotImplemented
    
    
def REQUEST_TIMER( rqstJson,rqstVer):
    roomfind=rqstJson['room_no']
    usertarget=rqstJson['user_num']
    if(CLNTLIST[usertarget].roomno==-1):#강퇴당했네
        return REQUEST_EXIT(rqstJson,rqstVer)
    cur_room=None
    for i in ROOMLIST.values():
        if(str(i.number)==roomfind):
           cur_room=i
           break
    if(cur_room==None):
        return REQUEST_EXIT(rqstJson,rqstVer)

    
    curtime=time.time() #타임스탬프랑 비교할 현재값
    if(i.curstage==0): ##대기실.
        templi=slist()
        for idx,val in enumerate(i.clnts.values()): #먼저 유저리스트 중 이 방에속하지 않은 사람이 있는지 확인한다
            if( val.roomno==i.number):
                #만약 heartbeat안보낸지 오래되었으면 내보내야.
                if(usertarget==val.number):
                        val.waittime=curtime
                if(len(i.clnts) < MINIMUM_PLAYER):
                    templi.append(val)
                else:                    
                    if( (curtime-val.waittime)<WAIT_VALUE):
                        templi.append(val)
                    else:
                        #만약 방장이면 내보내면안돼
                        if(i.host!=val.number):
                            val.roomno=-1 #방에 존재하지 않는상태
                        else:
                            templi.append(val)
            #else: 다른방에 이미 들어간상태 우리의 리스트에포함안시킨다.
        i.clnts=templi
        group_data=OrderedDict()
        group_data["code"]="SUCCESS_TIMER"
        group_data["stage_name"]=str(i.curstage)
        group_data["stage_time"]=str(time.time()-CLNTLIST[usertarget].readytime) # 준비
        group_data["room_no"]=str(roomfind)
        group_data["time"]=str(READY_WAIT_VALUE) #준비신호 120초안에보내야
        msgstr=str(json.dumps(group_data,ensure_ascii=False,indent="\t"))
        rspnHead = '\r\n'.join([
                        f"{rqstVer} 200 OK",
                        f"Server: {SERVER_NAME}",
                        f"Content-length: {len(msgstr)}",
                        f"Keep-Alive: timeout=5, max=100",
                        f"Content-type: text/html"
                        ])
        return rspnHead,msgstr
    elif (i.curstage ==1):# 만약 curstage==1이면
            #아직 키워드 선정안했네
        if(time.time()-i.timestamp >KEYWORD_WAIT_VALUE+5): #5초정도 유예시간
            return REQUEST_EXIT(rqstJson,rqstVer)            
        group_data=OrderedDict()
        group_data["code"]="SUCCESS_TIMER"
        group_data["stage_name"]=str(i.curstage)
        group_data["stage_time"]=str(time.time()-i.timestamp) # 텔러가 보내는시간
        group_data["room_no"]=str(roomfind)
        group_data["time"]=str(KEYWORD_WAIT_VALUE) # 텔러가 키워드 30초안에보내야
        msgstr=str(json.dumps(group_data,ensure_ascii=False,indent="\t"))
        rspnHead = '\r\n'.join([
                        f"{rqstVer} 200 OK",
                        f"Server: {SERVER_NAME}",
                        f"Content-length: {len(msgstr)}",
                        f"Keep-Alive: timeout=5, max=100",
                        f"Content-type: text/html"
                        ])
        return rspnHead,msgstr
        #else: #키워드 선정된경우 ---삭제--- 그냥 다른함수에서 체크하도록.
    elif (i.curstage==2): #만약 텔러가 키어드 선정하고 남은 카드 뽑을 수 있는 시간이라면
        if(time.time()-i.timestamp > CARD_WAIT_VALUE+5):
            return REQUEST_EXIT(rqstJson,rqstVer)
        group_data=OrderedDict()
        group_data["code"]="SUCCESS_TIMER"
        group_data["stage_name"]=str(i.curstage)
        group_data["stage_time"]=str(time.time()-i.timestamp) # 텔러가 보내는시간
        group_data["room_no"]=str(roomfind)
        group_data["time"]=str(CARD_WAIT_VALUE) # 카드 30초안에 보내야해
        msgstr=str(json.dumps(group_data,ensure_ascii=False,indent="\t"))
        rspnHead = '\r\n'.join([
                        f"{rqstVer} 200 OK",
                        f"Server: {SERVER_NAME}",
                        f"Content-length: {len(msgstr)}",
                        f"Keep-Alive: timeout=5, max=100",
                        f"Content-type: text/html"
                        ])
        return rspnHead,msgstr
    elif(i.curstage==3): #카드 투표하는시간
        if(time.time()-i.timestamp > CARD_VOTE_VALUE+5):
            return REQUEST_EXIT(rqstJson,rqstVer)
        group_data=OrderedDict()
        group_data["code"]="SUCCESS_TIMER"
        group_data["stage_name"]=str(i.curstage)
        group_data["stage_time"]=str(time.time()-i.timestamp) # 텔러가 보내는시간
        group_data["room_no"]=str(roomfind)
        group_data["time"]=str(CARD_VOTE_VALUE) # 어떤 카드에 투표할지 30초안에 보내야해
        msgstr=str(json.dumps(group_data,ensure_ascii=False,indent="\t"))
        rspnHead = '\r\n'.join([
                        f"{rqstVer} 200 OK",
                        f"Server: {SERVER_NAME}",
                        f"Content-length: {len(msgstr)}",
                        f"Keep-Alive: timeout=5, max=100",
                        f"Content-type: text/html"
                        ])
        return rspnHead,msgstr
    else: #게임종료를 알림
        group_data=OrderedDict()
        group_data["code"]="SUCCESS_TIMER"
        group_data["stage_name"]=str(i.curstage)
        group_data["stage_time"]=str(time.time()-i.timestamp) # 텔러가 보내는시간
        group_data["room_no"]=str(roomfind)
        group_data["time"]=str(10) # ?? 게임종료하면 그냥 뭐 별거없지뭐..
        msgstr=str(json.dumps(group_data,ensure_ascii=False,indent="\t"))
        rspnHead = '\r\n'.join([
                        f"{rqstVer} 200 OK",
                        f"Server: {SERVER_NAME}",
                        f"Content-length: {len(msgstr)}",
                        f"Keep-Alive: timeout=5, max=100",
                        f"Content-type: text/html"
                        ])
        return rspnHead,msgstr



if __name__ == "__main__":
    run()
