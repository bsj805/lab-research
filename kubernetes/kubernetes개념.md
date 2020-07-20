
# Kubernetes basic


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
