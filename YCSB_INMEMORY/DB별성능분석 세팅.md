YCSB설치 
(black쪽)
git clone https://github.com/brianfrankcooper/YCSB.git
mvn clean package




- #!/usr/bin/env python
+ #!/usr/bin/env python2
으로 YCSB 디렉토리의 bin/ycsb 파일 수정


docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' [컨테이너 이름]

출처: https://msyu1207.tistory.com/entry/Docker-docker-DB-사용해보기-mongodb-설치-외부에서-db-접속 [Lotts Blog]


<몽고DB시작>

docker run -d --name mongo-db -v /data:/data/db -p 27017:27017 mongo:4.2
이러고 container에서 mongo를 킨다.

몽고디비의 설정파일은
/etc/mongod.conf

여기서 bindIP: 를 고치면 모든 IP에서 접속가능
bindIP: ::,0.0.0.0
이런식으로 해두면 ipv6,ipv4 접속가능.



white 쪽에서
mongo 192.168.0.2:27017
로 접근가능

출처: https://msyu1207.tistory.com/entry/Docker-docker-DB-사용해보기-mongodb-설치-외부에서-db-접속 [Lotts Blog]
<https://msyu1207.tistory.com/entry/Docker-docker-DB-%EC%82%AC%EC%9A%A9%ED%95%B4%EB%B3%B4%EA%B8%B0-mongodb-%EC%84%A4%EC%B9%98-%EC%99%B8%EB%B6%80%EC%97%90%EC%84%9C-db-%EC%A0%91%EC%86%8D>

sudo ./bin/ycsb load mongodb-async -s -P workloads/workloada > outputLoad.txt
//이게 workload " a" 번째의 데이터를 넣어두는것.

mongo에서는
show dbs
use ycsb
show collections;
db.usertable.remove()
db.stats();

 ./bin/ycsb load mongodb-async -s -P workloads/workloada -p mongodb.url=mongodb://localhost:27017/ycsb?w=0
 이거하면된다. workloada를 담는거.
 어차피 docker를 포트포워딩해서 로컬에보내도 저기로간다.
 ./bin/ycsb run mongodb-async -s -P workloads/workloada -p mongodb.url=mongodb://localhost:27017/ycsb?w=0 > outputRun.txt
load했으니 run하자.
![image](https://user-images.githubusercontent.com/47310668/116787627-06e50280-aae0-11eb-8cf0-ce1885d3c6fd.png)

./bin/ycsb load mongodb -s -P workloads/workloadc -p recordcount=1000 -threads 2 -p mongodb.url="mongodb://cw-mongo-router:27017/ycsb"
./bin/ycsb load mongodb -s -P workloads/workloadc -p recordcount=1000 -threads 2 -p mongodb.url="mongodb://172.17.0.3:27017/ycsb"

이렇게 서버에다 미리 넣어두는것.
mongodb://172.17.0.3:27017/ycsb
하면 ycsb라는 이름의 db를만든다. 
<https://eyeballs.tistory.com/174>



####카산드라 cassandra

설정파일은


docker run --name cassandb -p 9042:9042 -d cassandra:3 

vim /etc/systemd/system/cassandra.service 이게 초기환경
vim /etc/cassandra/conf/cassandra.yaml 이게 그 뒤에 환경설정
vim /etc/cassandra/cassandra.yaml
rpc_address: 0.0.0.0 으로 설정,
broadcast_rpc_address의 주석해제
sudo systemctl daemon-reload
sudo systemctl start cassandra.service
sudo systemctl enable cassandra
systemctl status cassandra.service 명령어로 active가 되어 있는지 확인하고 nodetool status로 현재 Cassandra의 상태를 확인할 수 있습니다.
cqlsh -u cassandra -p cassandra 로 처음 접속 
./bin/ycsb load cassandra-cql -p hosts="127.0.0.1" -s -P workloads/workloada
./bin/ycsb run cassandra-cql -p hosts="127.0.0.1" -s -P workloads/workloada
https://log-laboratory.tistory.com/243
외부접속하려면 start_rpc:true ->이게 서버를여는것이야


1. 수정 항목 

rpc_address: 0.0.0.0
broadcast_rpc_address: 자기주소
listen_address: 자기주소
seeds : 자기주소
 

2. 추가 항목 

start_rpc: true

이후 kill pid 하고 bin.cassandra하면 재시작.

Workload A: Update heavy workload: 50/50% Mix of Reads/Writes
Workload B: Read mostly workload: 95/5% Mix of Reads/Writes
Workload C: Read-only: 100% reads.

출처: https://nowonbun.tistory.com/381 [명월 일지]



