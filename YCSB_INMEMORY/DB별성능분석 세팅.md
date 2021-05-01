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

 

./bin/ycsb load mongodb -s -P workloads/workloadc -p recordcount=1000 -threads 2 -p mongodb.url="mongodb://cw-mongo-router:27017/ycsb"
./bin/ycsb load mongodb -s -P workloads/workloadc -p recordcount=1000 -threads 2 -p mongodb.url="mongodb://172.17.0.3:27017/ycsb"

이렇게 서버에다 미리 넣어두는것.
mongodb://172.17.0.3:27017/ycsb
하면 ycsb라는 이름의 db를만든다. 
<https://eyeballs.tistory.com/174>


