### 도커 설치
https://subicura.com/2017/01/19/docker-guide-for-beginners-2.html

______
도커는 리눅스 기반이라, 리눅스상에 설치해야한다. 설치해보자.
먼저 xshell을 통해 내 서버에 들어간다.

 tmux -new 를 통해 새 tmux를 열고

 ctrl a 내 tmux prefix key를 입력 후 , v를 통해 화면을 분할한다
 alt R로 편하게 볼 수 있게 바꿔놓은뒤, 

curl -fsSL https://get.docker.com/ | sudo sh

설치!

docker -v 로 확인해보면 docker가 깔려있음을 알 수 있다.

docker은 기본적으로 root 권한이 필요하다. 

<sudo 없이 사용하기

docker는 기본적으로 root권한이 필요합니다. root가 아닌 사용자가 sudo없이 사용하려면 해당 사용자를 docker그룹에 추가합니다.

`sudo usermod -aG docker $USER # 현재 접속중인 사용자에게 권한주기
sudo usermod -aG docker your-user # your-user 사용자에게 권한주기`
사용자가 로그인 중이라면 다시 로그인 후 권한이 적용됩니다.>

