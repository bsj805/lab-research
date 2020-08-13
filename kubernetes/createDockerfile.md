### C++ 도커 작업하기.
<https://www.slideshare.net/iFunFactory/docker-linux-linux-66590915>

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
```
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
 ```
 while true; do wget -q -O- http://10.97.176.44:80; done
 ```
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
 
흠. 이걸로 알아낸 것은, 스스로 cpu usage를 조정하는 무언가가 있다.

### CPU Management Policies.
<https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/>
Default값으로, kubelet은 CFS quota (completely fair scheduler) 를 이용해 pod CPU limit을 지키게 한다. 노드가 CPU-bound pods 를 많이 run 할수록, workload는 
pod가 throttling이 되는지나 scheduling 될 때 어떤 CPU core가 available 한지 에 따라 다른 CPU core로 움직일 수도 있다. 많은 workloads 들은 이런 migration에 그렇게 sensitive하지 않으며, 
어떤 intervention 없이도 works fine

2 supported policy
1. none: default
2. static: allows pods with certain resource characteristics to be granted 
  increased CPU affinity and exclusivity on the node. 혼자 돌아도 되도록 설정하는게 
  (얘 하나만 돌아가게 할 수 있나본데?)
CPU manager은 CRI를 통해서 periodically write resource updates.

reconcile frequency는 --cpu-manager-reconcile-period. ==default는 --node-status-update-frequency

static policy가 containers in guaranteed pods들을 exclusive acess to CPU하게 만드는거.
이 exclusivity는 cpuset cgroup controller를 통해서 이뤄짐. 
exclusively allocatable CPU는 total num of CPUs in the node - any CPU reservations by the kubelet --kube-reserved or --system-reserved options. kubelet에 --reserved-cpus option을 달면 돼.

음 cpu가 배정되는 과정이 cpus are removed from the shared pool and placed in the cpu set for the container if guaranteed pods.  
즉 shared pool에 있는 CPU만 가지고 CFS가 cpu usage를 관리하는거지. 

내 상황도 
<https://kubernetes.io/docs/tasks/configure-pod-container/assign-cpu-resource/>
와 같이 설명가능

node에 cpu resource limit이 있는데, 그것보다 cpu를 많이 쓰려고 하니 cpu use가 being
throttled된다. 

```bash
kubectl get nodes --no-headers | awk '{print $1}' | xargs -I {} sh -c 'echo {}; kubectl describe node {} | grep Allocated -A 5 | grep -ve Event -ve Allocated -ve percent -ve -- ; echo
```
https://dzone.com/articles/kubernetes-resource-usage-how-do-you-manage-and-mo 

________________
우리가 만든게 overcommitted 한 상태인데, 
https://github.com/kubernetes/community/blob/master/contributors/design-proposals/scheduling/pod-priority-api.md
의 priority에 따라 결정된다. 

사실 내가만든 상태는 쿠버네티스에서꽤흔한일이다 
보통 workload는 high priority critical tasks, non-urgent tasks의 mix이다. 
non-urgent면 기다릴 수 있는 거지.
Cluster management는 그런 workloads를 구분하고, 어떤게 acquire the resource 해야 하고 어떤게 기다릴 수 있는지 구분해야한다.
클러스터에 제공할 key metric 중 하나이다. priority가. 

lower priority pods 는 higher priority pods 에게 preempted 될 가능성이 높다.
cluster가 threshold에 닿았을 때. 이럴 때엔, scheduler은 higher priority pending pods
를 위해 lower priority pods 를 preempt 하고자 한다.
물론 다른 여러 parameter가 있다. affinity나 anti-affinity. lower priority pods 가 preempted 되도 high priority pod가 schedule 되지 못한다고 스케줄러가 판단하면, preempt하지 않는다. scheduler는 다른 restrictions도 있다. 만약 pod disruption budger이 violate된다면 pod를 preempt하지 않을 것이다. PodSpec 이라는 struct에 priority값을 가진다. PriorityClassName (specified by user), Priority ( populated by Kubernetes). User specified is a string and all valid priority classes are mapped their string with interger values. PriorityClassName이 empty 면 default priority. 
물론 system priority class들을 위한 system priority class names도 있어.
any priority above 1 billion is reserved for system use. 
``` bash
system  2147483647 (int_max)
tier1   4000
tier2   2000
tier3   1000
```
tier1이 가장높은 priority. 

### resource QOS(Quality Of Service) in Kubernetes
https://github.com/kubernetes/community/blob/master/contributors/design-proposals/node/resource-qos.md#qos-classes

pods 들의 request에 따라서 different level of QOS. 
request == limit 이면 resources are guaranteed. 
request < limit : pod is guaranteed the request but can opportunistically scavenge the difference between request and limit if they are not being used by other containers. This allows kubernetes to oversubscribe nodes. (utilization을 늘리게 허용한다 limit까지) 

#### requests and limits

for each resource, containers can specify a resource request and limit,
0 <= request <= Node Allocatable & request <= limit <= Infinity

kube-reserved 와 system-reserved 자원 양은 
/etc/origin/node/node-config.yaml 파일에 있다.
```
[Allocatable] = [Node Capacity] - [kube-reserved] - [system-reserved]
```
이니까
<https://github.com/kubernetes/community/blob/master/contributors/design-proposals/scheduling/resources.md>
kubernetes schedulers들은 sum of the resources allocated to its pods never exceeds the usable capacity of the node. ( pod가 node에 fit 할지 테스트 하는 feasibility checking) 

우리가 yaml파일에서 말하는 spec은 desired state를 뜻한다. 
우리가 yaml파일에서 말하는 status 는 current state이다. 
```
Excess CPU resources will be distributed based on the amount of CPU requested. For example, suppose container A requests for 600 milli CPUs, and container B requests for 300 milli CPUs. Suppose that both containers are trying to use as much CPU as they can. Then the extra 100 milli CPUs will be distributed to A and B in a 2:1 ratio (implementation discussed in later sections).
Pods will be throttled if they exceed their limit. If limit is unspecified, then the pods can use excess CPU when available.
```
pod는 kubelet이 들여오고 scheduler 가 schedule 한다. based on the sum of requests of its containers. Scheduler와 kubelet이 ensure that
sum of requests of all containers is within the node's allocatable capacity.
##### QoS classes
<https://github.com/kubernetes/community/blob/master/contributors/design-proposals/node/resource-qos.md#qos-classes>
overcommitted system( sum of limits > machine capacity) 에서
containers might eventually have to be killed. 
그럼 덜 중요한 컨테이너를 kill 해야겠지. 
각 리소스별로, container들을 3가지 QoS class로 분류한다.
1. Guaranteed,2 Burstable, and 3 Best-Effort.

Requests and Limits와 QoS class 사이의 관계는 미묘하다. (적다.)
이론적으로는, policy of classifying pods into QoS classes is orthogonal to the requests and limits specified for the container. 
서로 상반된다는 말인가보다.
Hypothetically, users could use an API to specify whether a pod is guaranteed or best-effort. ( 나중에는)
어찌되었던, 지금은, pod를 QoS class로 분류하는 것은 tied to "Requests and Limits" . QoS는 memory guarantee를 위해 만들어지긴 했다.

______________

Pod는 3개의 다른 class 중 하나가 될 수 있다.
limits 와 requests (얘는 있어도 되고 없어도 되고)  가 set for all resources across all containers and they are qeual, pod is classified as **Guaranteed.** (보장..)
- 파드 내 모든 컨테이너가 CPU 상한과 CPU 요청을 가지고 동일할 때.


Requests 와 limits(얘는 있어도 되고 없어도 되고) 가 set for one or more resources and they are not equal, pod is **burstable**.(원하면 CPU를 더 가져간다!) 
limit이 specified 되지 않으면 node capacity만큼이다. 
- 파드 내에 request가 정해진  pod가 있는 경우.

request와 limit이 not set이면 **best-effort** 로 분류돼.( 새거가 들어오면 기꺼이 내주지 & CPU guarantee가 맞지 않으면 pods가 killed 되는거.)


lowest priority to highest priority ( guaranteed가 가장 높은거)

best effort pod: 가 lowest priority 그래도 노드에 있는 만큼의 resource사용가능

Burstable pods: minimal resource guarantee( requests만있어) 가지고 있어,
can use more resources when available. 이런 container은 best effort pod가 없을  때 killed 되는 victim이 된다. 



guaranteed pods: top-priority and guaranteed to not be killed until they exceed their limits. 자기보다 lower priority만 먼저 죽이도록 되어있다.




Out Of Memory score 이 있네 높을수록 kill

Swap off 하는 이유가 이 QOS때문이라고. 
swap space 때문에 memory가 threshold에 부딪혔을 때 다른 현상이 발생가능


그래서 guaranteed 로 해주려고 small-test.yaml의 cpu limit을 1000m으로
걸고 request 는 0으로 둔채 small-test를 deploy 해보았다.

결과: QoS class: Burstable로 뜬다!

limit과 request 설정안하면 best-effort

```
kubectl run --generator=run-pod/v1 -it --rm lo2 --image=busybox /bin/sh

while true; do wget -q -O- http://small-apache.default.svc.cluster.local; done

while true; do wget -q -O- http://php-apache.default.svc.cluster.local; done
```

역시 1000m을 잡아먹고 더 늘어나지않는다.
바로 load generator 하나 추가하니까 throttling 발생.
둘다 레스폰스타임이 늘어나버림.

1001m은 반올림되어서 그런가보다.

autoscaler는 cpu request와 limit가 정해져야지만 쓸 수 있대.

일단 8개를 실행시켜서 7953 m 의 cpu를 사용하게 해놓았어.
response time은 많이 늘어났고, cpu 100%사용중.
이상태에서 small-apache에 load를 가해주면 small-apache는
best effort인 php-apache보다 priority가 높기 때문에
1000m을 가져올 수 있을 것.
처음에는 2, 1 초가 계속해서걸리다가, 줄어들것으로 예상했는데
아니다. 그냥 다른 php-apache 서버처럼 얘에도 부하가 걸리는지
cpu 사양이 안좋아진것인지, 1초나 2초가 걸린다.
1000m을 갖게 되긴 했다.


<https://www.replex.io/blog/everything-you-need-to-know-about-kubernetes-quality-of-service-qos-classes>
______________________
guaranteed pods 가 Exclusive CPU core을 얻을 수 있는 이유?
shared CPU pool은 노드의 모든 CPU resource MINUS --kube-reserved 와 --system-reserved.

Guaranteed는 static CPU management policy를 통해 exclusive use of CPU를 할 수 있다.

best effort pods는 kubernetes scheduler가 어떻게 관리할까?
얘네들은 사용가능한 resource를 다 쓰고 싶어하기 때문에, this can at times lead to resource contention with other pods, where BestEffort pods hog( 자신만을 위해서 다 쓰는) resources and do not leave enough resource headroom(여유분) for other pods to consume resources within resource limits.

Bustable QoS class를 가지는 pods들 ( 2번째 priority) 과 같이, BESTEFFORT pods also run in the shared resources pool on a node and cannot be granted exclusive CPU resource usage.

이걸 evict 하는 것은 kubelet이야. pod의생성과 제거를 담당하는 kubelet.


DevOps(development and operation 하는사람들) can specify thresholds for resources which when breached(break through(into)) trigger pod evictions by the Kubelet.
그니까 개발쪽에서 언제 eviction trigger 할지 한계선을 정할 수 있다는 거네.
QoS class of a pod does affect the order in which it is chosen for eviction 
\
 QOS class 는 eviction될때 순서에 영향을 미친다. kubelet은 BestEffort 와 Burstable pods using resources above requests 인 애들을 먼저 evict 한다. 각 pod 에 주어진 priority와 amount of resources being consumed above request. 
 
 ```
 이쯤에서 원론으로 돌아가서, 생각해보면,
 best-effort service 두개가 있다고 할 때 cpu를 건네주는 방식의 차이는 결국 
 CFS quota 인 것이다. 결국 scheduling을 어떻게 하느냐에 달려있는 문제가 된 것이다
 HPA쪽이 아니라. 
 ```
 아 어쨌던, oom_killer는 memory 넘칠때 killer인데, memory usage별로 oom_score을 매겨서
 qos class 더 좋은게 있더라도 kill될수도 있다. 
 
 Resource manage에는 Cgroup이 관여한다.
 Pod A, Pod B, Pod C 와 같이 pod 단위의 Cgroup이 존재하고, cgroup 아래에는
 각각 pod 에 속한 App container의 Cgroup과 Pause Container의 Cgroup이 존재한다.
 
 Cgroup의 CPU Quota
 ```
 (cfs_quota_us / cfs_period_us) * 1000 = Limit milicpu
(150000 / 100000) * 1000 = 1500 milicpu

[공식 1] CPU Quota 계산 01
(milicpu / 1000) * cfs_period_us = cfs_quota_us
0.5 * 100000 = 50000

[공식 2] CPU Quota 계산 02

 CPU Limit 값은 Linux에서 Process의 CPU Bandwidth를 제한하는데 이용되는 Cgroup의 CPU Quota를 설정하는데 이용된다. CPU Quota는 cfs_period_us와 cfs_quota_us라는 두개의 값으로 조작된다. cfs_period_us은 Quota 주기를 의미하고 Default 값은 100000이다. cfs_quota_us은 Quota 주기동간 최대 얼마만큼 CPU를 이용할지 설정하는 값이다. cfs_quota_us값을 150000으로 설정하면 [공식 1]에 의해서 Container는 최대 1500milicpu만 이용 할 수 있다.

설정할 수 있는 최대 CPU Limit 값은 Container가 동작하는 (v)CPU의 개수에 의해 제한된다. Container가 동작하는 Node에 4 (v)CPU만 있다면 Container에게는 최대 4000milicpu까지만 할당할 수 있다. [공식 1]을 이용하여 [공식 2]를 만들 수 있다. [공식 2]는 Kubernetes에서 CPU limit에 따라서 cfs_quota_us 값을 계산하는 방법을 나타낸다. cfs_period_us 값은 무조건 Default 값인 100000을 이용한다. 만약 CPU limit를 500milicpu를 설정하였다면 [공식 2]에 의해서 cfs_quota_us값은 50000이 된다.

(Request milicpu / Node Total milicpu) * 1024 = shares
Contaier A : (1500 / 2000) * 1024 = 768
Contaier B : (500 / 2000) * 1024 = 256
```
이 위에가 CPU weight 계산인데 [공식3] 
```
 CPU Request 값은 Linux에서 Process의 Scheduling 가중치를 주는데 이용되는 Cgroup의 CPU Weight를 설정하는데 이용된다. Cgroup에서 CPU Weigth는 shares라는 값으로 조작된다. Process A는 1024 shares를 갖고 있고, Process B는 512 shares를 갖고 있다면 Process A는 Process B보다 2배 많은 CPU Bandwith를 이용할 수 있게 된다. CPU Weight와 Kubernets의 Pod Scheduling을 이용하면 Container가 요구하는 CPU Request 값을 Container에게 제공할 수 있다.

2000 milicpu (2 CPU)를 갖고 있는 Node에 Container A는 1500 milicpu를 Request로 요청하고 Container B는 500 milicpu를 Request로 요청한다고 가정한다면, Container A와 Container B의 Weight의 비율은 3:1만 충족시키면된다. 비율을 적용하는 기준값은 shares의 기본 값인 1024를 이용한다. 따라서 Container A의 shares 값은 768이 되고 Container B의 shares 값은 256이 된다. shares 값은 [공식 3]을 통해서 계산할 수 있다
```

<https://kubernetes.io/blog/2018/07/24/feature-highlight-cpu-manager/>
cpu resource control에 대한 세가지 :
  1. CFS shares (what's my weighted fair share of CPU time on this system) 
  2. CFS Quota (what's my hard cap of CPU time over a period)
  3. CPU affinity (on what logical CPUs am I allowed to execute).

이제 container spec에 cpu limit 걸 때에는 CFS QUOTA를 이용해서  <https://www.kernel.org/doc/Documentation/scheduler/sched-bwc.txt>
조정. 이게 말하는 바는, given 'period' 동안 'quota' microsecond CPU time을 사용할 수 있게 한다는 것이다.

근데 CPU manager가 static policy 로 enable 되면, shared pool of CPUs 를 manage하게된다. 처음에 이 shared pool은 compute node의 모든 CPU를 가지고 있다. container with integer CPU request in a Guaranteed pod( 최상위 priority) 가 kubelet에 의해 생성되면,
CPUs for that container are removed from the shared pool and assigned exclusively for the lifetime of the container. 즉 shared pool의 cpu가 아닌 독자적인 cpu를 가지게 된다는 것. 다른 container들은 exclusively allocated cpu를 가지고 있었을 수도 있으니 여기서부터 migrated off 한다.

다른 non-exclusive CPU containers (Burstable, BestEffort and Guaranteed with non-integer CPU) run on the CPUs remaining in the shared pool. 즉 guaranteed 된 것중에 integer cpu 값으로 설정하면 static 인 게 된다는 것 같은데 그치.

어.. 그 memory 값까지 지정같이 안해주면 guaranteed 모드가 안되네. (/kube/testphp2/hpa-test2.yaml 로 성공)
describe node 해보면 2000 ( 즉 8000 * 1/4 )가 cpu: "2" 값으로 정해져있고,
실제로 부하를 가하니 2000m을 사용한다. responsetime은 엄청나게 늘어나서 5초 7초..
일단 small-test2.yaml 을 실행시키고 기존 php-apache는 best effort로 바꿔서 large load를 가한다.

기존 php-apache : 3992m - small-apache : 895m-> 999m (small은 load 1개 기존은 load 4개)

여기서 php-apache:의 로드를 늘려본다.
response time이 느려졌다? 일단 cpu는 4319 : 999  70% 사용중 ( 총 8000m) 
아직 small pod는 responsetime 동일 4986m : 999m 75% 사용중

이제 로드를 php-apache에 더주면, 전체적으로 response time이 더 늘어나며,
5972m : 999m 87퍼
아직 small은 response time에는 큰 차이 없는듯? 
이제 php-apache에 load를 더 가했다. 아직은 response time에 차이가 없다.
일단은 best effort니 만큼 최대한을 쓰는 것 같다. 6931: 999m 노드사용률 99% 7969

흠.. 하나를 늘리면 guarantee에서는 안뺏어가겠지? ? responsetime이 늘어나는 것 같아보이진 않는다.
음 아마 6950:995: 현재상태 유지인것 같다.
일단 하나를 늘렸는데도 guarantee에서는 못 뺏어갔어.
하나를 더 늘리니 (9개인듯?) response time이 늘어나고있어. 
하지만 6597: 993 여전하네. 

이제 small-apache에 부하를 가해보자. 
response time이 늘어나보이는데 ( 기존거) 


일단 실험해볼거는

현재 /kube/testphp2/hpa-test.yaml 로 php-apache 하나 만들고
현재 /kube/testphp2/small-test2.yaml 로 small-apache 하나 만들고

small-apache에 small1 로 로드를 가해서 그때의 top node를 구할꺼야
그리고 기존 -apache에 lo1~ lo 6까지 가해서 그때의 top pod와 top node값을 출력해

기존 -apache에 lo7,8 까지 가해서 그떄의 top pod 와 top node값을 출력해
이러면 과부하 상태일텐데,
이 상태에서 small2 로 small에 로드를 가해서 그때의 top node 값과 top pod 값을 출력
하면 오늘 나온 결과랑 똑같겠지?

그리고 
while true; do wget -q -O- http://php-apache.default.svc.cluster.local; done
으로 구했었는데, 
echo $(date +"%T")
echo $(date +"%r") <https://mkblog.co.kr/2019/12/29/bash-current-date-time/>
하면 현재시간 나오는데 이거랑 어떻게 붙일수없나?
while true; echo $(date +"%T") >>helloworld.txt ; do wget -q -O- http://google.com >>helloworld.txt ; done
이런식으로 하면 되나본데
>> result.txt

#### 20-08-12 오늘의 회의록
priority 가 과도하게 차지하도록 하게 되었을때 낮은애들을 다 죽여야 하느냐 에 대한 의문

real time > AF > Best Effort 

semi-guaranteed 같이 얘보다는 조금 나은 priority를 가지는 애에게 

response time graph가 필요해~

그리고 HPA는 왜 필요한가  내 생각에는 한 노드에 한 파드가 cpu 를 몽땅 갖는것이 안되는
상황 ( 여러 노드에 pod를 분산시키는 것이 좋은 상황) 에서 쓰는 것 같은데..

그렇다면 지금 best effort 끼리는 cpu를 나눠갖고있는데 우리의 의문점은 이미 solved되어 
있는 것이 아닌가?

<https://bcho.tistory.com/1259> <https://nirsa.tistory.com/156> <- 더 자세한설명
이 글을 보고 hostPath 라는 yaml 파일을 만들어서 하자.

아 그리고 생성되는 자료는 hulkbuster node에 위치한다는 점.
<https://medium.com/coinone-official/%EC%A2%8C%EC%B6%A9%EC%9A%B0%EB%8F%8C-kubernetes-%EC%9D%B5%ED%9E%88%EA%B8%B0-3-5d6cd6b6b1d0>

결국 문제는 busybox 자체만 실행시켰을 때는 시킨 일이 없으니 0초만에 끝나버리는거.
그래서 sleep command를 주고 
```bash
kubectl exec -it hostpath-pod -- bin/sh
```

로 한 다음 /hostpath에 vi test.txt를 생성하니
hulkbuster desktop 에서 yaml 파일 아래에 기재한 내용 에 따라

```bash
1 apiVersion: v1                                                                                                                                                                                                                          
  2 kind: Pod                                                                                                                                                                                                                               
  3 metadata:                                                                                                                                                                                                                               
  4   name: hostpath-pod                                                                                                                                                                                                                    
  5 spec:                                                                                                                                                                                                                                   
  6   containers:                                                                                                                                                                                                                           
  7   - name: hostpath-pod                                                                                                                                                                                                                  
  8     image: busybox                                                                                                                                                                                                                      
  9     command: ['sh', '-c', 'echo Hello Kubernetes! && sleep 3600 ']                                                                                                                                                                      
 10     volumeMounts:                                                                                                                                                                                                                       
 11     - mountPath: /hostpath                                                                                                                                                                                                              
 12       name: hostpath-volume                                                                                                                                                                                                             
 13   volumes:                                                                                                                                                                                                                              
 14   - name: hostpath-volume                                                                                                                                                                                                               
 15     hostPath:                                                                                                                                                                                                                           
 16       path: /home/byeon/kube/testphp2/results  # 해당 디렉토리가 존재해야 합니다.                                                                                                                                                       
 17       type: DirectoryOrCreate                                                                                                                                                                                                           
~                                         
```
와 같이 hostPath의 경로에 저장이 되어있었다.
컨테이너의 /hostpath에 텍스트파일을 생성했더니.

<https://itlove.tistory.com/1710> 를 참고해서 php에서 milisecond를 잴 수 있고, 
<https://victorydntmd.tistory.com/53>를 참고해서 github에 엑세스했다
best effort 자료는 office cloud에 자동저장시켜놨고,
ppt에 어떤 것을 실험하는 것인지 써 놓았다.

result.txt, result2.txt는 best effort php-apache 서비스에 로드를 가할 때 응답시간을 시간순으로 적어놓은 문서이다.

small.txt~ 시리즈는 best effort small-apache pod에 로드를 가할 때 응답시간을 시간순으로 적어놓은 문서이다.

first experiment 폴더에 넣어놓겠다.


다음실험을 진행하기에 앞서, 모든 파드가 7200초에 꺼지니까 불안하다.
고로 reset을 한번 시키고 했으면 좋겠는데.
kubectl get pods 보니까 5시간 16분째라고 한다. 일단 45분내로 한번 끝내면될듯


우선 git에 업로드하려면

git init을 통해 새로운 로컬 repository를 지정해줘야한다.
git add를 통해 변경된 파일을 storage에 추가하고
git commit을 통해 add한 파일을 local repository에 저장
git push를 통해 local repository를 remote repository에 업로드 

1. 원하는 폴더로 가서 git init.
2. git status로 어떤 게 repository와 다른지 알 수 있어.
3. sudo git remote add origin https://github.com/bsj805/lab-research.git 와 같이 origin이라는 별명으로
repository에 등록을 하고. 
4. git add . 을 통해서 버전 관리할 파일들을 추가해. .을 arg로 넣은 것은 현재 디렉토리
5. sudo git pull -f origin master 로 다운로드 (pull, 끌어오고) 
6. sudo git commit -m "메세지 내용"
7. git push origin master  ( origin은 repository 별명, master는 branch이름) 
이러면 username과 비번치라하는데 bs@gm Q~
하면 된다.


나중에는

git add .
git commit -m "메세지 내용"
git push origin 브랜치이름
만 해도 된다고 한다.


```bash

while true; echo -n $(date +"%T") "  " >> /hostpath/result.txt ; do wget -q -O- http://php-apache.default.svc.cluster.local >>/hostpath/result.txt; done
while true; echo -n $(date +"%T") "  " >> /hostpath/result2.txt ; do wget -q -O- http://php-apache.default.svc.cluster.local >>/hostpath/result2.txt; done
while true; echo -n $(date +"%T") "  " >> /hostpath/result8.txt ; do wget -q -O- http://php-apache.default.svc.cluster.local >>/hostpath/result8.txt; done
while true; echo -n $(date +"%T") "  "  ; do wget -q -O- http://php-apache.default.svc.cluster.local ; done

while true; echo -n $(date +"%T") "  " >> /hostpath/small5.txt ; do wget -q -O- http://small-apache.default.svc.cluster.local >>/hostpath/small5.txt; done
while true; echo -n $(date +"%T") "  " >> /hostpath/small1.txt ; do wget -q -O- http://small-apache.default.svc.cluster.local >>/hostpath/small1.txt; done
while true; echo -n $(date +"%T") "  " >> /hostpath/small2.txt ; do wget -q -O- http://small-apache.default.svc.cluster.local >>/hostpath/small2.txt; done
while true; echo -n $(date +"%T") "  " >> /hostpath/small3.txt ; do wget -q -O- http://small-apache.default.svc.cluster.local >>/hostpath/small3.txt; done

```
index.php는 
millisecond 단위로
```
  1 <?php                                                                                              
  2     date_default_timezone_set('Asia/Seoul');                                                       
  3     #$now =new DateTime();                                                                         
  4     #$now = explode(' ',microtime());                                                              
  5     #$bef = floor(($now[0] + $now[1])*1000);                                                       
  6     $start = microtime(true);                                                                      
  7                                                                                                    
  8     $x = 0.0001;                                                                                   
  9     for ($i = 0; $i <= 10000000; $i++) {                                                           
 10         $x += sqrt($x);                                                                            
 11     }                                                                                              
 12     #$diff =new DateTime();                                                                        
 13     #$sum = $diff->getTimestamp() - $now->getTimestamp();                                          
 14     echo (microtime(true) - $start);                                                               
 15     echo " OK!";                                                                                   
 16 ?>  
 ```
 실행시간 측정.
