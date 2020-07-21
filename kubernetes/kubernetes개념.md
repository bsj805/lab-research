
# Kubernetes basic

## 2020-07-21 today I learned

쿠버네티스 구성: 노드와 컨트롤 플레인으로 구성.
컨트롤 플레인은 워커 노드와 파드를 관리한다. (node는 kublet을 통해 kube-api-server( control plane) 와 통신

#### Control Plane Components
______________________
애초에 클러스터 내의 어떤 머신에서던 control plane을 배정할 수 있지만 보통 worker node와 분리시킨다. 
즉슨, 컨트롤 플레인은 실제 일을 하는 머신과 물리적으로나 어떻게던 떨어져 있는 머신에 배정하게 되나보다.

 * kube-apiserver
 - 쿠버네티스 api를 관리. 수평적 확장을 고려해서 디자인 되어 있다.
 - 마스터 노드의 핵심 모듈이다. (마스터노드 == 컨트롤 플레인) 
 - 사용자의 모든 요청을 처리
 - kubectl의 요청 뿐만 아니라 control plane 즉 마스터 노드 안의 모듈의 요청도 처리하며 권한을 체크해서 요청 거부도 가능
 - 사실 원하는 상태를 JSON 처럼 key -value 저장소에 저장하고 저장된 상태를 조회하는 매우 단순한 일을 해.
 - pod을 노드에 할당하고 상태를 체크하는 일을 하지는 않음. (다른 모듈이 담당) 
 
 * etcd 분산 데이터 저장소.
 - RAFT 라는 분산환경 데이터 저장 알고리즘을 이용한 key- value 저장소. (여러개로 분산해서 복제도 가능)==reliabilty , fast, watch 기능도 있어 어떤 상태 변경시 특정 로직 실행 가능.
 - 클러스터의 모든 설정과 상태 데이터가 여기에만! 저장되고 다른 모듈은 stateless기에 etcd만 있어도 클러스터 복구 가능. 
 - etcd는 오직 api server만을 통해 접근 가능. 물론 etcd 또한. 이것도 그냥 sql중 하나라 미니 쿠버네티스 처럼 용량 작게 할 떈 sqlite 를 사용한다. 
 
 * kube-scheduler
 - 스케줄러는 할당되지 않은 pod을 여러 조건에 따라 적절한 노드 서버에 할당해준다. 
 - 즉 노드에 직접 pod 배정해주는 애가 얘임.
 
 * kube-controller-manager
 - 쿠버네티스의 거의 모든 오브젝트의 상태를 관리. 
 - 노드 컨트롤러: 노드 다운 시 통제
- 레플레키에션 컨트롤러: 파드 수 조절
- 엔드포인트 컨트롤러: 서비스-파드 연결
- 서비스 어카운트 및 토큰 컨트롤러: 새로운 네임스페이스에 대한 계정 및 API 토큰 생성
 - 오브젝트별로 분업화 되어 있어 deployment가 replicaset을 생성, replicaset이 pod를 생성, pod은 스케줄러에 의한 관리 받음
 
 * cloud-controller-manager
 - AWS,GCE,Azure 등 클라우드에 특화된 모델. 노드를 추가 삭제하고 로드 밸런서를 연결하거나 볼륨을 붙일 수 있다.
 
___________________________________
#### 하나의 pod이 생성되는 과정 (https://subicura.com/2019/05/19/kubernetes-basic-1.html)

1. 관리자가 애플리케이션 배포를 위해 replicaset을 생성하려고 해.
$ kubectl ~~~ 라며 api server에 replicaset을 만들라고 요청.
2. controller은 이 replica set의 생성 요청을 감시하다 replica set이 만들어졌음을 알게 될 것
3. 이제 pod 생성 요청이 controller과 api server간에 이루어지고
4. 할당되지 않은 pod 이 생성되는 것을 보고자 하는 Scheduler은 pod 생성 요청을 감시하다가 
5. 노드에 pod를 할당해달라고 api server에 요청한다.
6. node의 kubelet은 api-server에 통신하며 pod가 자기 노드에 할당되는지 감시한다.
7. node의 kubelet은 노드안의 docker에 컨테이너를 생성해달라는 요청을 하고
8. kubelet은 api server에 pod이 어떤 상태인지 업데이트 시그널을 보내준다 .
![](https://subicura.com/assets/article_images/2019-05-19-kubernetes-basic-1/create-replicaset.png)


## 2020-07-20 first day in lab

### 최종목표
 현재 kubernetes에서는 pod라는 최소한의 단위가 있음. ( 보통 한 pod에 한 컨테이너 지만 컨테이너는 여러개 들어가도 돼)
 한 pod은 리소스를 분배해주는 최소 단위가 된다. 
 이 단위는 controller에서 negotiating을 통해서 받아오는 데, HPA라는 horizontal pod auto scaler mechanism flow 가 존재한다. 
 이를 가지고 연구실원들이 테스트를 해 보았을 때 (환경: nginx 라는 웹서버를 올려놓고( 한 컨테이너에) 수많은 request를 넣고 repsonse를 내뱉게 해놓음) 
 request를 받는 port 하나가 있고 각 thread마다 controller는 pod를 생성해서 response를 만들어 내도록 해놓았다.
 이말인 즉슨, 이 horizontal로 했을 때는 각 쓰레드마다 자원을 배분하는 방식으로 간다 이거다. 
 
 지금 교수님께서 하고자 하시는 것은 virtical 한 방식이다.
 기존에 HPA는 이와같이 필요한게 생기면 pod하나의 리소스를 늘리는 것이라기 보다는 여러 pod를 만들어서 
 각자 처리를 하고 결과물을 낼 수 있도록 함인데, 
 VPA는 pod 하나의 리소스를 늘려서 처리하는 방식이 될 것이다.
 만약 pod 하나에 cpu burst, 즉 cpu처리량이 큰 ( 큰 오픈소스를 컴파일 하는 등의 workload) 작업이 있다면,
 (컴파일이라는 작업은 보통 1000개의 뭐 라이브러리 등 소스코드가 있다면 먼저 소스코드 각각을 각각의 쓰레드에서 컴파일 한다음, 
 각 쓰레드에서 컴파일을 마친 뒤에 linking이 시작된다. 즉 쓰레드를 많이 쓰는데 HPA방식이라면 많은 양의 pod가 생길 것이다) 
 
 1.이런 작업은 latency가 중요치 않고 오히려 cpu처리량이 작은 작업이 latency가 중요하니 cpu처리량이 작은 작업에게 리소스를 내주고
 cpu 처리량이 큰 작업의 일부를 sleep 상태로 주는 것이 어떠한가 에 대한 의문인 것이다. 
 
 2.그래서 생기는 궁금증은 (물론 thread를 많이 쓰는 이상 synchronous하게 코딩이 되어 있겠지만)
 synchronous 하게 맞춰야 하는 것 때문에 단순히 두 쓰레드가 멈춘 것의 오버헤드 이상의 문제가 발생하는지 ( 엄청나게 느려지는지 얼마나 느려지는지)
 (이것의 performance metric은 시간이겠지. 시간이 정상적으로 컴파일되는데 걸리는게 100이라면 89% 정도의 효율을 예상하는데 70%까지 떨어지는가 이런거) 
 또 VPA를 했을 때 , (이건 controller 뒤쪽의 scaler인데 아마 얼마나 줄지 결정해주는듯)
 sleep 시킬 작업을 어떻게 정하는지. 이것도 우리가 신경써야 하는 특징 중 하나일지를 결정해야한다. 문제의 구체화가 부족하다 아직.
 
 3.또한, VPA를 쓸 이유가 HPA보다 무언가가 있어야 할 것이다. 우리가 만약 VPA로 이걸 한다고 했을 때 장점을 찾지 못한다면
 해볼 이유가 없는 것이다. 
 _________________
 ### 내가 해보아야 하는 것.
 compiler을 HPA상에서 돌려보면서 이 CPU burst인 작업이 어떻게 진행되는지를 알아봐야 하는 것이다.
 우선 쿠버네티스의 동작을 익혀보고, 컨테이너 위에서 cpu burst인 우분투 컴파일링 을 돌렸을때 (any open source compiling) 
 pod가 몇개가 생성되고, 얼마나 많은 리소스가 쓰이고 얼마나 많은 시간이 걸리고를 측정해봐야 할 것이다. 
 
#### reference
https://github.com/Susoon/Research_Report/blob/master/DPDK_Summary.md 
-> understandings about writing in github (전수환)
https://www.notion.so/Kubernetes-ddc927fce1bb4456825d46f8188b54d4
-> notion of kubernetes  쿠버네티스 문서 정리 (강성민)
https://www.notion.so/NSLab-2020-7-1-2-33bf408a782e40bc81313d3ba973bde9
-> kubernetes 실제 사용 (강성민)
images 라는 폴더를만들고 거기의 경로를 지정해서 이미지를 가져올 수 있음
#![Alt_text](images/
