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


Pod는 3개의 다른 class 중 하나가 될 수 있다.
limits 와 requests (얘는 있어도 되고 없어도 되고)  가 set for all resources across all containers and they are qeual, pod is classified as **Guaranteed.** (보장..)

Requests 와 limits(얘는 있어도 되고 없어도 되고) 가 set for one or more resources and they are not equal, pod is **burstable**.(원하면 CPU를 더 가져간다!) 
limit이 specified 되지 않으면 node capacity만큼이다. 

request와 limit이 not set이면 **best-effort** 로 분류돼.( 새거가 들어오면 기꺼이 내주지 & CPU guarantee가 맞지 않으면 pods가 killed 되는거.)



best effort pod: 가 lowest priority 그래도 노드에 있는 만큼의 resource사용가능

guaranteed pods: top-priority and guaranteed to not be killed until they exceed their limits. 자기보다 lower priority만 먼저 죽이도록 되어있다.

Burstable pods: minimal resource guarantee( requests만있어) 가지고 있어,
can use more resources when available. 이런 container은 best effort pod가 없을  때 killed 되는 victim이 된다. 


Out Of Memory score 이 있네 높을수록 kill

Swap off 하는 이유가 이 QOS때문이라고. 
swap space 때문에 memory가 threshold에 부딪혔을 때 다른 현상이 발생가능











