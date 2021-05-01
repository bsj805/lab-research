YCSB설치 
(black쪽)
git clone https://github.com/brianfrankcooper/YCSB.git
mvn clean package



<몽고DB시작>

docker run -d --name mongo-db -v /data:/data/db -p 27017:27017 mongo:4.2
이러고 container에서 mongo를 킨다.

출처: https://msyu1207.tistory.com/entry/Docker-docker-DB-사용해보기-mongodb-설치-외부에서-db-접속 [Lotts Blog]
<https://msyu1207.tistory.com/entry/Docker-docker-DB-%EC%82%AC%EC%9A%A9%ED%95%B4%EB%B3%B4%EA%B8%B0-mongodb-%EC%84%A4%EC%B9%98-%EC%99%B8%EB%B6%80%EC%97%90%EC%84%9C-db-%EC%A0%91%EC%86%8D>





white 쪽에서
mongo 192.168.0.2:27017
로 접근가능
