### C++ 도커 작업하기.<https://www.slideshare.net/iFunFactory/docker-linux-linux-66590915>

``` DOCKERFILE
  1 FROM ubuntu:20.04                                                                                                                                                                                             
  2 RUN apt-get -qq update \                                                                                                                                                                                      
  3  && apt-get -qq install -y g++ cmake \
     && apt-get install vim \
  4  && apt-get clean                                                                                                                                                                                             
  5                                                                                                                                                                                                               
  6 EXPOSE 8000                                                                                                                                                                                                   
  7 VOLUME ["/workspace"]        // 위의 apt-get install 할때 설치하게 되는곳 컨테이너안에 디렉토리가 생김                                                                                                                                                                                 
  8 ENTRYPOINT ["/bin/bash"]     // 컨테이너 시작시점에 ENTRYPOINT를 실행시킴                                                                                                                                                                                 
  9                                                                                                                                                                                                               
~                                
``` 
``` bash
docker build --rm -t cpp-builder .
```
이러면 8000포트를 연거야.
```bash
docker run -it --rm -v ~/work/helloworld:/workspace cpp-builder
```
이러면 helloworld라는 이름의 프로젝트를 빌드하는 거야.

이제 docker 컨테이너 안에서
``` bash
apt-get update
apt install build-essential 
cd /workspace
mkdir build; 
cd build;

```
<https://psychoria.tistory.com/613>
도커파일수정.

```Dockerfile
  1 FROM ubuntu:20.04                                                                                                                                        
  2 RUN apt-get -qq update \                                                                                                                                 
  3  && apt-get -qq install -y g++ cmake \                                                                                                                   
  4  && apt-get -y install vim \                                                                                                                             
  5  && apt install build-essential -y \                                                                                                                     
  6  && apt-get clean                                                                                                                                        
  7                                                                                                                                                          
  8 #set the working directory to /app  ( we copied all things into /app                                                                                     
  9 WORKDIR /app                                                                                                                                             
 10                                                                                                                                                          
 11 #copy current directory contents into the container at /app                                                                                              
 12 ADD . /app                                                                                                                                               
 13                                                                                                                                                          
 14 EXPOSE 8000                                                                                                                                              
 15                                                                                                                                                          
 16 #define environment variable                                                                                                                             
 17 ENV NAME Wrold                                                                                                                                           
 18                                                                                                                                                          
 19 #Run hello when container launches                                                                                                                       
 20                                                                                                                                                          
 21 CMD ["./hello"]     
 ```
 
<https://amytabb.com/ts/2018_07_28/> 여기를 참고하면 뭔가 알수 있을거같다.

```Dockerfile
  1 FROM ubuntu:20.04                                                                                                                                        
  2 RUN apt-get -qq update \                                                                                                                                 
  3  && apt-get -qq install -y g++ cmake \                                                                                                                   
  4  && apt-get -y install vim \                                                                                                                             
  5  && apt install build-essential -y \                                                                                                                     
  6  && apt-get clean                                                                                                                                        
  7                                                                                                                                                          
  8 #set the working directory to /app  ( we copied all things into /app                                                                                     
  9 WORKDIR /app/                                                                                                                                            
 10                                                                                                                                                          
 11 #copy current directory contents into the container at /app                                                                                              
 12 ADD . /app                                                                                                                                               
 13                                                                                                                                                          
 14 EXPOSE 8000                                                                                                                                              
 15                                                                                                                                                          
 16 #define environment variable                                                                                                                             
 17 ENV NAME World                                                                                                                                           
 18                                                                                                                                                          
 19 #Run hello when container launches                                                                                                                       
 20                                                                                                                                                          
 21 CMD ["./hello"]       
 ```
 
 이걸로 내 . 디렉토리에 있는 (현재 디렉토리) 파일을 copy해주고, 
 현재의 경로로 설정해준다음, 커맨드라인에서 ./hello를 침으로써 어플을 실행시키는데 성공한다.
 
 ADD 대신 COPY를 써도 된다.
 
 ```dockerfile
 FROM amytabb/docker_ubuntu16_essentials
ENV NAME VAR1
ENV NAME VAR2
ENV NAME VAR3
COPY run_hello1.sh /run_hello1.sh
COPY HelloWorld /HelloWorld
WORKDIR /HelloWorld/
RUN g++ -o HelloWorld1 helloworld1.cpp
WORKDIR /
CMD ["/bin/sh", "/run_hello1.sh"]
 ```
 환경변수 VAR1, 2, 3을 만들어 놓고 run_hello1.sh를 
 ``` bash
 #!/bin/sh
./HelloWorld/HelloWorld1 $VAR1 $VAR2 $VAR3
```
 로 만들어놓는거.
 
 
 
 ![image](https://user-images.githubusercontent.com/47310668/89859309-a9202b80-dbdb-11ea-91b3-59ca0bcb15bf.png)

이런식으로 실행시킬 수 있다. -e
 
dockerfile을 
 
 ```Dockerfile
 1 FROM ubuntu:20.04                                                                                                                                                                                                                          
  2 RUN apt-get -qq update \                                                                                                                                                                                                                 
  3  && apt-get -qq install -y g++ cmake \                                                                                                                                                                                                   
  4  && apt-get -y install vim \                                                                                                                                                                                                             
  1 FROM ubuntu:20.04                                                                                                                                                                                                                        
  2 RUN apt-get -qq update \                                                                                                                                                                                                                 
  3  && apt-get -qq install -y g++ cmake \                                                                                                                                                                                                   
  4  && apt-get -y install vim \                                                                                                                                                                                                             
  5  && apt install build-essential -y \                                                                                                                                                                                                     
  6  && apt-get clean                                                                                                                                                                                                                        
  7                                                                                                                                                                                                                                          
  8 #set the working directory to /app  ( we copied all things into /app                                                                                                                                                                     
  9 WORKDIR /                                                                                                                                                                                                                                
 10 ENV NAME VAR1                                                                                                                                                                                                                            
 11 ENV NAME VAR2                                                                                                                                                                                                                            
 12 ENV NAME VAR3                                                                                                                                                                                                                            
 13 RUN mkdir /write_directory                                                                                                                                                                                                               
 14 ARG DIRECTORY=/write_directory                                                                                                                                                                                                           
 15 ENV VAR_DIR=$DIRECTORY                                                                                                                                                                                                                   
 16                                                                                                                                                                                                                                          
 17 COPY run_hello2.sh /run_hello2.sh                                                                                                                                                                                                        
 18 COPY HelloWorld /HelloWorld                                                                                                                                                                                                              
 19                                                                                                                                                                                                                                          
 20 #copy current directory contents into the container at /app                                                                                                                                                                              
 21 #ADD . /app                                                                                                                                                                                                                              
 22                                                                                                                                                                                                                                          
 23 EXPOSE 8000                                                                                                                                                                                                                              
 24                                                                                                                                                                                                                                          
 25 #define environment variable                                                                                                                                                                                                             
 26 ENV NAME World                                                                                                                                                                                                                           
 27                                                                                                                                                                                                                                          
 28 #workdir바꾸고 compile                                                                                                                                                                                                                   
 29 WORKDIR /HelloWorld                                                                                                                                                                                                                      
 30                                                                                                                                                                                                                                          
 31 #Run hello when container launches                                                                                                                                                                                                       
 32                                                                                                                                                                                                                                          
 33 RUN g++ -o HelloWorld2 helloworld2.cpp                                                                                                                                                                                                   
 34                                                                                                                                                                                                                                          
 35 WORKDIR /                                                                                                                                                                                                                                
 36                                                                                                                                                                                                                                          
 37 CMD ["/bin/sh", "/run_hello2.sh"]    
 ```
 로 구성한뒤, 
 
 
 ![image](https://user-images.githubusercontent.com/47310668/89860676-ff429e00-dbde-11ea-9575-4b1dc264aebe.png)
 와 같이 실행시키면, write_directory는 
 
 docker run -it -v /home/byeon/docker/HelloWorldMount:/write_directory -e VAR1=15 bruzn/hello2
이 mount옵션에 따라서, write_directory에 쓰여진 파일이 저기에 저장되는 것이다. 
 
 https://stackoverflow.com/questions/59093384/how-to-pass-arguments-to-docker-container-in-kubernetes-or-openshift-through-com
 
 e 옵션은 environment variable을 넘기는건데, 이렇게 할수있대
 
The right answer is from @Jonas but you can also use environment variables in your yaml file as stated below:

As an alternative to providing strings directly, you can define arguments by using environment variables
```bash
env:
- name: ARGUMENT
  value: {{ argument_1 }}
args: ["$(ARGUMENT)"]
Where {{ argument_1 }} is an environment variable.

기존 index.php를 시간차이를 내도록해서
bruzn/overloadphp-apache . 로 
```
 docker build --tag bruzn/overloadphp-apache . 
 ```
 이미지를 빌드했다.
 ![image](https://user-images.githubusercontent.com/47310668/89866828-2acb8580-dbeb-11ea-91b7-897ff0e5de08.png)

와 같이 응답시간이 현격하게 떨어진 것을 볼 수 있다..
한 pod의 최대값이 500m이므로(limit) 그 이상으로늘어나지 못한다는 걸 알 수 있다.
또 바로 
![image](https://user-images.githubusercontent.com/47310668/89866972-69f9d680-dbeb-11ea-9152-28c55392871f.png)
원래대로 돌아오는 것도 볼 수 있다.

흠.. cpu를 초과해서 사용하려고 하면 오히려 thrashing 같이 전체적인 속도저하가 발생한다.
Thrashing이란, 프로세스가 실행을 위해 몇개의 페이지 프레임을 할당 받는데, (메모리에서의
이야기. 메모리는 limit보다 현저히 적게사용) degree of multiprogramming이 올라가다보면
시스템의 프레임 개수가 프로세스가 한 단위시간에 필요한 프레임 수보다 적을수도 있다. 
이때엔 프로세스가 수행되는 시간보다 page fault에 처리하는 시간이 길어져서 cpu utilization이 저하되는
문제가 발생한다. 

내가 세운 가설은 이러하니 그렇다면 단순히 하나의 부하만 있을 때에 cpu utilization을
잡아먹는지 볼까?
음 일단 이상태로도 500을 다 잡아먹는건 맞는거같다.
<https://hellomuzi.tistory.com/33>
throttling 에 관한 이야기였다. 
cpu limit 상태가 되면, cpu는 compressible 리소스가 된다. app이 cpu limit을 치면 kubernetes는 
app container를 throttling하기 시작한다. cpu가 인위적으로 제한되고, 
앱이 잠재적으로 더 나쁜 퍼포먼스를 낼 수 있다. 
하지만 죽이지는 않음. 퍼포먼스에 영향받지 않으려면 liveness health check를 써라.

라고 한다. 

오호 아예 unlimited ( cpu:0 ) 하니까 response time이 더 빨라졌어.
뭔가 단계는 있나보다..
1000m에 머물러있는다.
그래서 하나를 더하니 1996으로 올라갔다.
response time은 거의 그대로.

2026m을 쓰는 hulkbuster가 25퍼니까..
하나씩 클라이언트를 늘릴때마다 cpu사용량이 1000m씩늘어나고 
이걸로 부하를 걸어보자.
 
5개째에 5000m. 62퍼

6개 6000m이나 7000m 이제 response time이 늘어나기시작.
7개 7000m, cpu 87%, 0. 초만에 response가 나오는게 이제 없어짐.

8개 php-apache가 7954m cpu쓰고 21 Mi 메모리 쓰고, 할때
node는 7987m 99%에 해당하는 cpu 사용중.
아직 php의 response time이 길어지거나 하진 않았음.
7991.

여기에 small task를 하나 더 넣고 얘에 대한 hpa를 발동시켜보자.
8000이 cpu 100%

http://10.97.176.44:80
즉 small-apache로 접속하게 했더니

기존 7900정도를 차지하던 기존 php-apache가 1000m을 내주면서
small-apache에게 1000m을 부여해줬다. 
 
 hpa는 프로그램을 시작시키기 전에 켜야된다고 한다. 
 그리고 limit을 정해주어야 작동한다고 한다 deployment에 대해.
 while true; do wget -q -O- http://10.97.176.44:80; done
 load를 기존거에 더 가해주니까 100m정도를 가져가는 것 같음
 그랬다가 다시 small 쪽 로드를 늘려주니 또 small쪽에서 cpu를 더 가져감. 500정도
 small에 로드 하나 더 해주니 500 더 가져감. 
 근데 6000 : 2000 인 상황에서 small을 더해주니 (small4) 5번째 스몰 . 5500 : 2500
 지금 원래거는 10개 였음.
 그리고 양쪽의 레스폰스타임이 현격하게 느려짐. 서로 비슷한정도
 로드를 기존거에 더해주니 5700:2500 이 유지된다. 그러다 다시 5500:2500 가량..
 small 에 추가해주니
 처음엔 5300 2700 후엔 5100 2900
 그러다 쓰로틀링인지
 5094: 2626: 확줄어들었다가
 5197: 2647
 5134: 2842
 5431: 2703
 5148: 2592
 5326 : 2490
 5085 : 2928
 
 오리지날 2개를 줄였어.
 
 4761 : 3032
 
 이제 6:6인데
 4324: 3687 먼저 시작한 것이 우선권을 가지고 있나?
 4207:3637
 4171:3707
 4220:3654
 
 이제 로드를 각 3개씩으로 줄였더니
 
 2998:2998 cpu util 75%
 
