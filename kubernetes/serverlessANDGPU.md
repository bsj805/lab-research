
### 2020-08-21

FaaS( Function as a Service) 란 함수를 서비스로 제공하는 형태
한 function당 150gb, 300초가 제한. 이런걸 보면 어떻게 사용하냐면, backend로.

서버를 쓰는 용도로는 거의 못쓰니까. 이벤트 처리를 Faas쪽에서 시켜주는 거지.

클라이언트에서 사용자 인터랙션 로직을 대부분 처리
자주 사용하는 서버 기능은 서버리스형 서비스로 처리
각종 연계를 위해 사용하는 작은 함수(FaaS)

처리를 FaaS쪽에서 하는거라고 보면 돼.

<https://futurecreator.github.io/2019/03/14/serverless-architecture/>
<https://velopert.com/3543>


##### machine learning
<https://sdc-james.gitbook.io/onebook/1./1.1.-artificial-intelligence>

```

머신러닝은 프로그래머의 프로그래밍 없이 컴퓨터 스스로 원하는 방식으로 배우게 하는 능력을 갖게 하는 기술입니다. 
기본적으로 알고리즘을 이용해 데이터를 분석하고, 이 데이터를 이용해서 학습하고, 학습된 정보를 기반으로 판단이나 예측을 하는 시스템을 말합니다. 
프로그래머를 고용하여 복잡한 규칙을 가진 프로그래밍을 하는 것보다 머신러닝을 통하여 프로그램을 생산하는 것이 시간과 비용면에서 더 효율적이기 때문에 각광을 받고 있는 것입니다.
```
프로그래머가 일일이 모든 사진에 대해서 편향치를 갖도록 설정하는것 보다야 낫다는 것이지.

딥러닝은 머신러닝의 세부 방법주 ㅇ하나. 
머신러닝은 컴퓨터에게 다양한 정보를 가르치고, 그 학습한 결과에 따라 컴퓨터가 새로운 것을 예측,

딥러닝은 가르치는 과정 없이도 스스로 학습하고 미래 상황을 예측할 수 있어.

```
현재 기업과 개발자들의 인공지능 개발 방식은 크게 세 가지로 나눌 수 있습니다. 첫 번째는 데이터 수집 및 분석, 머신러닝, 인공신경망 구축 등 모든 작업을 처음부터 끝까지 직접 하는 것입니다. 인공지능 기술 역량을 축적하기에는 매우 좋지만 개발 속도가 매우 느려진다는 단점이 있습니다. 두 번째는 텐서플로, 카페, 토치 등 오픈소스 인공지능 프레임워크를 활용해 인공지능을 개발하는 것입니다. 인공지능 개발에 들어가는 시간을 제법 단축할 수 있고, 데이터 가공이나 인공신경망 구축 등 핵심 기술에 대한 노하우도 많이 얻을 수 있어 대학과 연구소를 중심으로 많이 선호 받고 있는 방식입니다. 세 번째는 구글, 마이크로소프트, 아마존 등이 클라우드 컴퓨팅 서비스를 통해 제공하는 인공지능 API를 적극 활용해 인공지능을 개발하는 것입니다. 기술 종속이 일어날 수 있지만, 인공지능 모델을 빠르게 완성해 상용화할 수 있다는 점에서 많은 기업들에게 각광받은 방식입니다.
```

GPU는 병렬 처리를 효율적으로 처리하기 위한 수천 개의 코어를 가지고 있습니다. 
어플리케이션의 연산집약적인 부분을 GPU로 넘기고 나머지 코드만을 CPU에서 처리하는 GPU 가속 컴퓨팅은 특히 딥러닝, 머신러닝 영역에서 강력한 성능을 제공합니다. 사용자 입장에서는 연산 속도가 놀라울 정도로 빨라졌음을 느낄 수 있습니다.

CPU는 여러가지 ALU가 있지만 GPU는 한 ALU 단순한게 여러개가 있다.
```
GPU는 SIMT(singl instruction multiple threads)모델을 사용한다.
```
<https://ccode.tistory.com/220>
```
3. CPU-GPU와의 통신.



CPU-GPU같의 데이터 전송은 PCI를 이용해 이루워지는데



이 또한 굉장히 느리다.



이 데이터 전송량을 최소화하고,



memory transfer overlapping이란 방법을 사용한 최적화가 필요하다.
```

____
###### CUDA 프로그래밍 (compute Unified Device Architecture" ) 

<https://arisu1000.tistory.com/1173>

CUDA는 일반적인 CPU 연산이 아닌 GPU 연산을 해. 
GPU 연산을 위해서는 CPU의 데이터를 GPU용으로 바꿔야 해.
메인보드 ram에 있는 데이터를 GPU ram으로 옮기는 것이야.

메모리에 데이터를 어떻게 할당하고, GPU의 여러가지 종류의 메모리중 어떤 메모리를 활용하느냐에 따라 성능차이가 많이 난다.

그 다음에 그 데이터를 이용해서 GPU상의 계산을 해.
계산 결과가 GPU에 있으니 이 데이터를 CPU로 copy 해주는 것 까지가 CUDA의 역할.
CUDA가 C++이래.
```
일반적인 GPGPU에서는 이렇게 데이터를 GPU에 올리고 내리고 할때 그래픽스에 관한 지식이 있어야 가능하지만 CUDA의 목적은 그런 지식 없이도 일반적인 C프로그래머들이 접근하기 용이하게 만드는게 목적입니다

출처: https://arisu1000.tistory.com/1173 [아리수]
```

GPU는 CPU보다 많은 ALU를 보유하고 있어.
CPU에서는 특정 ALU를 이용하라고 프로그래머가 지정해주지 않지만, CUDA에서는 ALU 하나하나를 
![image](https://user-images.githubusercontent.com/47310668/90856735-9668dc00-e3bd-11ea-8a53-edf229f9aec7.png)
다 프로그래머가 제어해줘야 한다. 
![image](https://user-images.githubusercontent.com/47310668/90856781-ada7c980-e3bd-11ea-917f-5038ae3c2e52.png)
여기서 thread라고 하는 것이 CUDA에서 가장 작은 단위이다.
이 THread들이 BLock의 하위에 있고 Block들은 다시 Grid의 하위에 있다.

연산을 할 때 몇번 Grid의 몇번 Block의 몇번 Thread를 사용해서 계산하겠다고 지정해주어야 한다.

각 쓰레드는 자신만의 local memory 가 있고 thread간의 shared memory가 따로 있고 block들의 집합인 Grid간의
데이터 공유를 위한 global memory가 있어.

이 메모리간에 데이터 이동비용이 꽤 커서 이 메모리 사용을 잘 해야한다. 메모리들 간의 속도차이도 있어.

그 Thread 하나하나를 kernel이라고 부른다. 

```
SIMT 유닛은  32개의 병렬 스레드의 그룹을 만드는데 이것들을 warps 라고 부릅니다.
device에서 계산을 시작하게 되면 SIMT 유닛은 warps안에 각각의 스레드를 분해해서 넣습니다. 여기서 첫번째 warp는 Thread ID 0을 가지게 되는 겁니다.


출처: https://arisu1000.tistory.com/1259?category=477475 [아리수]
```
<https://medium.com/finda-tech/kubernetes-%EB%84%A4%ED%8A%B8%EC%9B%8C%ED%81%AC-%EC%A0%95%EB%A6%AC-fccd4fd0ae6>
```
client pod가 service 네트워크를 통해 server pod1으로 http request를 요청하는 과정은 아래와 같다.
client pod가 http request를 service-test라는 DNS 이름으로 요청한다.
클러스터 DNS 서버(coredns)가 해당 이름을 service IP(예시로 10.3.241.152 이라고 한다)로 매핑시켜준다.
http 클라이언트는 DNS로부터 IP를 이용하여 최종적으로 요청을 보내게 된다.
```
즉, service-test 라는 걸 dns 서버가 해당 IP로 매핑시켜주는 역할.
그럼 나는 이 클러스터 DNS 서버에 먼저 통신을 하겠네?

클러스터 dns 서버는
http://팟이나서비스이름.default(네임스페이스영역).svc(pod이면 pod.).cluster.local

아하 pod 안에서만 이 core dns ( kube-dns) 를 거치기 때문에, 내가 외부에서 암만 물어봤자
이걸 resolve host할수 없는 거구나.
<https://jonnung.dev/kubernetes/2020/05/11/kubernetes-dns-about-coredns/> 를 참고하슈


해당 노드에 설정되어 있는 NAT 테이블을 조회
```
sudo iptables -S -t nat
```
service들과 어떤식으로 연결되는 지 알 수 있게 해준다. 

자 문제점

어떻게 성능을 측정할 것인가.


메인토픽은 pod을 컨테이너상에서 돌릴 때, 그걸 이용해서 GPU에 명령을 내리고
그 GPU가 일을 마쳤을 때, pod에게 그 값을 전달할 때 네트워크의 full bandwith를 활용하지 못한다
