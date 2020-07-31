
# Kubernetes basic
## 2020-07-31 TIL

여전히 metric server와 씨름중이다.
/var/lib/kubelet/config.yaml에 kubeadm에 대해 설정한게 있다.anonymous에 대한 authentication을 true로 설정해주었다.
이거는 처음 kubeadm init을 시킬 때에 api-server에 대해서 내 ip를 198.168.0.17로 지정해주어서 그런 것 같다.
kubeadm init을 다시 해볼 필요성이 있는 것 같아서

rm -rf /etc/cni/net.d
rm -rf $HOME/.kube/config
를 날리고
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 로 구성했다.
kubelet environment file with flags in /var/lib/kubelet/kubeadm-flags.env

config파일은 kubectl -n kube-system get cm kubeadm-config -oyaml 로 볼 수 있대. 

마침내 성공! 

~/metric/components.yaml 설정으로 되었다.
        args:                                                                                        
- --cert-dir=/tmp                                                                          
- --secure-port=4443                                                                       
- --kubelet-insecure-tls                                                                   
- --kubelet-preferred-address-types=InternalIP 
이제 kubectl top node가 된다.

kubeadm init은 flannel만 설정하는 옵션으로 했고
hulkbuster쪽에서 4443 포트 6443, 443 포트를 다 방화벽에서 해제했다.
0.3.7버전의 components.yaml은 image pull이 안되는 문제가 있다고 한다.
delete 커맨드로 밀고서 0.3.6 yaml로 설치한 결과이다.
key값은 메모장에 적혀있고, 

##### php 예제 연습
https://gruuuuu.github.io/cloud/monitoring-01hpa/
https://kubernetes.io/ko/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/


내 도커 id는 만들어야 해. bruzn 으로 만들었어. 내 도커 id가 bruzn
vim Dockerfile로 docker 파일 명세서를 만들고,
docker build --tag bruzn/php-apache .    <- 마침표를 찍어야 하더라..
docker images 로 확인해보면 bruzn/php-apache 가 존재한다.

yaml 파일을 작성하다가
tab을 쓰면 안된 다는 것을 깨달았다. 그래서 tab을 다 지운줄 알았는데
계속 같은 오류가 떠vim에 들어가서 / \t 로 tab character을 모두 찾아서 space로 대체해주었다.

hpa를 만드는 yaml을 설정해주고 (autoscaler.yaml) 
그리고 kubectl get hpa 를 하면 현재 시스템 부하 를 알 수 있어. 안에 내용은 yaml.에서 설정하고

kubectl apply -f autoscaler.yaml
로 적용했어. ~/kube/php/ 에서.

그리고 php서버에 요청을 전송해야하는데,
kubectl get service를 보면
php-apache의 cluster-ip가 10.111.10.119로 되어있는것을 볼 수 있고
포트가 80임을 볼 수 있어서
http://10.111.10.119:80 으로 해보았다.
요청이 보내진다!
251%까지 뛰었고 replica가 4 6 ... 늘어났다.
ctrl c로 취소하고
replicaset은 target 0/50% 가 되었지만 여전히 6개였었다.
## 2020-07-30 TIL

현재 새로운 서버를 생성해서 2222port로 접속할 수 있다. 
이게 한번에 join안되는 문제가 있었는데 6443 포트가 막혀있는게아닌가 하여
https://fblens.com/entry/%EB%A6%AC%EB%88%85%EC%8A%A4-%ED%8F%AC%ED%8A%B8-%ED%99%95%EC%9D%B8
를 따라서
netstat -nat | grep 6443 했는데 방화벽이 안 열린것 같아 
	
iptables -A INPUT -p tcp --dport 6443 -j ACCEPT

wget으로 파일다운로드가 가능하구나.

위의 명령어는 tcp 프로토콜의 포트를 열어주는 명령어입니다.
으로 열었다.
따라서 kubectl get nodes하면 드디어 우리 클러스터 노드가 보인다 ^^


이제 metric 서버를 열고, 자원사용량확인이되는지 확인해보고, 아래에 nginx tutorial을 진행해본다.

metric 서버를 여는것은 

kube-apiserver에 접속 못한다는 
the server is currently unable to handle the request (get nodes.metrics.k8s.io)
에러가 나면
/etc/kubernetes/manifests/kube-apiserver.yaml
에 https://github.com/kubernetes-sigs/metrics-server/issues/448

대로 --enable-aggregator-routing = true 를 붙여준다.
sudo로 안열면 아무것도 없는 것 처럼 보인다 (새파일처럼)

metric server은 /home/byeon/metrics-server/manifests/base 에 yaml 파일이 있다.

kubectl logs metrics-server-7df4c4484d-h75wr -n kube-system -c metrics-server

https://stackoverflow.com/questions/52702416/kubernetes-kubectl-top-nodes-pods-not-working
이걸 통해서 로그를 보니 포트가 막혀있어서 그런가 rnetes-master: Get "https://192.168.0.17:10250/stats/summary?only_cpu_and_memory=true": dial tcp 192.168.0.17:10250: i/o timeout
E0730 05:23:56.619399       1 server.go:115] unable to fully scrape metrics: unable to fully scrape metrics from node kubernetes-master: unable to fetch metrics from node kubernetes-master: Get "https://192.168.0.17:10250/stats/summary?only_cpu_and_memory=true": dial tcp 192.168.0.17:10250: i/o timeout
라고 한다. 

/etc/systemd/system/kubelet.service.d/10-kubeadm.conf
여기서 어떤 config파일이 적용되었는지 볼 수 있고,
/etc/kubernetes/에 가면 대부분의 config파일이존재
<https://lascrea.tistory.com/201> metric 서버가 어떻게 작용하는지에 대한 설명

VPA 설명
https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler

HPA 설명
https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/

kubectl delete -f /metrics-server/deploy/1.8+
kubectl apply -f /metrics-server/deploy/1.8+
메트릭서버 지우기

https://github.com/kubernetes-sigs/metrics-server/blob/master/FAQ.md
일단 known issue 중에 kubeadm으로 만든 클러스터에 대한 내용이 있어서 따라해보자.

흠..
Pod의 IP를 조회하는 방법은 -o wide 옵션을 추가한 kubectl get pods -o wide -A 명령어를 통해 가능하다.




## 2020-07-28, 2020-07-29 today I learned

*아직 클러스터 구성중
```bash
kubectl get node 
```
마스터 노드는 이미 등록되어 있고, 이제 클라이언트 노드를 체크해보자. 
kubeadm join 192.168.0.17:6443 --token oa782j.si1q33qc8ao0hmkt \                                                  --discovery-token-ca-cert-hash sha256:1f64b7fd2b51f8ee471df1e985f830f77d5c937a793749cefcb598884d879ba6  
이거 입력하면 내 클러스터에 join시킬 수 있는데.
현재는 kubectl 입력하면 the connection to the server localhost8080 was refused.

이 토큰이 24시간만 유효하다는 말이 있네.

kubeadm reset
하고,
kubeadm join 192.168.0.17:6443 --token t0zwfg.nemgefcego5a0wl8 \
    --discovery-token-ca-cert-hash sha256:59d91bc7f7453ea26f409949cfcf70dbb89a142fc40bde8822fd2b3e2a75a44a
    하자.

kubectl로 커맨드 안먹히는경우
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
chown으로 권한설정이 중요한듯.
메트릭 서버는 resource사용량을 볼 수 있도록 한 것 같은데
https://arisu1000.tistory.com/27856
이것과 비슷하다. 
<https://linux.systemv.pe.kr/metric-server-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0/>
이걸 참고하도록.

근데 메트릭서버가 실행되는지 보려고 kubectl get pods -n kube-system을 쳡니 메트릭서버가 실행되지 않는다. kubectl get deploy -n kube-system으로 확인해보니 metrics server에 배정가능한 replicaset이
없어보인다.
알고보니 
<https://stackoverflow.com/questions/52876792/kubernetes-metrics-server-dont-start> 
에서와 같이 더이상 schedule을 안하도록 하는 제한이 있었다. (taint)
이는 클러스터의 워커노드가 존재하지 않아서 생기는 문제라고 한다. 하긴, 슬레이브들의 자원을 모니터 하려고 만드는 메트릭 서버를 
마스터 하나있을 때에는 굳이 실행시킬 필요가 없던 것이다.

<https://gruuuuu.github.io/cloud/monitoring-01hpa/#> 여기를 통해서 HPA실습을 해보면 될 것 같은데.
<https://kubernetes.io/ko/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/> 이 내용을 기반으로 한 것이다.



## 2020-07-27 to do list, TIL

*client서버 접속할 수 있게 xshell 설정
*클러스터 구성 후, nginx 이용한 웹서버 구성
*HPA 적용방법 조사
* HPA 적용시에 pod의 개수 측정방법 or 어떻게 workload를 줄 지 조사

현재 ssh로 접속불가능한 문제가 있어서 다시 깔 예정.

우선 
sudo apt-get install docker 했는데, 
The following packages have unmet dependencies:
 docker.io :
 문제. 
sudo apt-get remove containerd.io
이걸로 해결가능 
https://bugs.launchpad.net/ubuntu/+source/docker.io/+bug/1830237

ssh가 안되는 문제가 있었는데,
그건 ssh를 sudo apt purge ssh-client 하니까 ssh 관련프로그램이 다 날라가면서 다시 접속가능해졌다.
또한 이걸 지울 때 docker 파일들이 같이날라가는 것을 보았는데, 어쩌면 docker의 설치가 
ssh에 연관이 생겨서 서로에게 영향을 준 것일지도 모르겠다.
일단 지울 때 에러메세지는 같은폴더의 errormess.txt를 참고하도록. 

<https://ubuntuforums.org/showthread.php?t=1145698> dhclient로 ssh 접속불가 해결
dhcp설정을 건드리는듯함.

## 2020-07-24 today I learned

일단 도커랑 kubernetes를 밀어버리고 다시 설치하려는데
ubuntu18.0.4 LTS 버전에서는
docker.io : Depends: containered 오류가 뜬다.

버전 업그레이드를 하거나 다른방법으로 패키지를 받거나 해야하는데
일단 다른 서버들도 다 버전이 20.0.4 ? 라고 하여 업데이트를 진행한 뒤 마저 설치를 하고자 한다.

apt -get install update-manager-core 

do-release-upgrade -d 를 하면 우분투 릴리스가 새로나왔는지 체크한다고한다
근데 또 * no development version of an LTS available* 이라고 하여 그냥
패키지자체를 다운받는걸로 했다.
아래 링크에서 참조하였다.
https://askubuntu.com/questions/1180060/getting-error-while-installing-docker-docker-ce-depends-containerd-io-1

<https://hiseon.me/linux/ubuntu/install-docker/>

setup의 자세한 이야기( <https://medium.com/finda-tech/overview-8d169b2a54ff> ) 

일단 이제 클러스터를 kubeadm init으로 구성했으니까 , 저 클라이언트 서버에 ssh접속할 방법을 알아내서
xshell 세팅을 하고 내 마스터 키 값( local 폴더에 저장되어있음 (내문서-klab) ) 으로 join시킨다.

kubectl -apply flannel.yml 이 안되는 문제가 있었는데 ,sudo 안붙이니까 됨.

## 2020-07-23 today I learned
<https://kubernetes.io/docs/concepts/architecture/nodes/>
#### 2 main ways to have Nodes added to the API server
1. kubelet on a node self-registers to the control plane.
2. human manually add a Node object

내가 Node object를 만들거나, kubelet on a node가 self-register 하면 ,control plane (master node쪽) 에서 
checks whether the new Node object is valid. 
```JSON
{
  "kind": "Node",
  "apiVersion": "v1",
  "metadata": {
    "name": "10.240.79.157",
    "labels": {
      "name": "my-first-k8s-node"
    }
  }
}
```
과 같이 만들었을 때, kubernetes는 node object를 internally 만들고, checks that a kubelet has
registered to the API server that matches the <b>metadata.name</b> field. 
만약 노드가 all necessary services가 running 중인 healthy node 라면, pod를 실행시킬 수 있다.

Cluster autoscaling.
<https://kubernetes.io/docs/tasks/administer-cluster/cluster-management/#cluster-autoscaling>
새 노드를 추가해서 현재 schedule 되어야 하는 pod들이 들어갈 수 있을지 판별하는
cluster auto scaler. 클러스터의 크기를 줄이기도 해. 
_________________
#### guestbook 만들기
<https://kubernetes.io/docs/tutorials/stateless-application/guestbook>

minikube없이도 클러스터를 구성하고 (노드를 생성하는 yaml 파일을 통해서) 

-만약 minikube를 이용한다면 ( service 종류가 nodeport** 밖에 안되는데, )
-나는 loadbalancer** 타입으로 해보았다.( 하지만 클러스터를 미니큐베로 구성했다는 것..이었다) 
<https://bcho.tistory.com/1308> 는 미니큐베에서 로드밸런서 타입을 테스트하는 것이다. 
만약 nodeport** 이라면 minikube service frontend --url 을 통해서 frontend service (frontend 가 서비스이름) 에 대한 ip주소:port번호 를 얻어오는 것 같다.
만약 load balancer 타입으로 frontend service를 만들었다면, 

```bash
kubectl get service frontend 
```
커맨드로 ip address를 얻어올 수있는데 ( 사실 get service랑 동일한거)  
나는 minikube를 통한 클러스터 구성을 했기 때문에, 위의 것에 따라서 해야한다.
______________________
<https://bcho.tistory.com/1255?category=731548>
#### 쿠버네티스 개념설명

왜 그냥 컨테이너 배포 하지 왜 컨테이너 운영환경이 필요한가?
수동으로 컨테이너를 배포할 때, 서버 수 ( 우리에게는 node의 수) 가 작으면 몰라도
서버가 몇십개 된다고 하면 일일이 여긴 CPU가 몇개니까 몇개 배포 이런게 힘들다.
-쿠버네티스 장점** 자원을 최적으로 사용하기 위한 컨테이너 분배 : (컨테이너를 적절한 서버에 배포하는게 스케줄링)

쿠버네티스 약자로 k8s 라고 한다. 
보통 VM을 올리고 그 위에 쿠버네티스를 배포하는 구조를 갖는데, 자원을 더 용이하게 사용하기 위해서라도 
이 VM이 필요하다는 것이다.

* Volume
pod가 기동할 때 컨테이너마다 로컬 디스크가 생성되잖아. 즉 로컬 디스크에 뭔가 저장될 때마다 
디스크의 기록이 사라지는데, DB같은 것은 파일을 영구저장해야 해. 이런 스토리지는 Volume** 이라고 하고
Pod가 기동할 때 컨테이너에 마운트가 되어 사용됨. 
이것도 따로 정의해야 사용된다. 이걸 어디에 마운트 해라 라고 하겠지.

* Service
Pod와 볼륨을 이용해서 컨테이너를 정의하고 pod를 서비스로 제공하면, 
한 pod으로 서비스를 제공하기 보다는 여러개의 pod를 서비스하면서 로드밸런서로 하나의 IP와 포트로 묶어서
서비스를 제공한다.
POD는 동적으로 생성되고, 장애가 생기면 자동으로 리스타트 되면서 IP가 바뀐다. 
따라서 로드 밸런서에서 pod의 목록을 지정할 때 IP주소를 이용하면 이상한 데에 access할 수도 있고

오토 스케일링으로 pod가 동적으로 추가/삭제 되니까 로드밸런서가 현재 running하는 pod를 잘 픽해줘야한다.
따라서 label** 과 label selector** 가 필요한 것이다.
서비스를 yaml로 정의할 때 어떤 pod를 서비스로 묶을지 정의하는데 이를 라벨 셀렉터라고 한다. 
각 pod를 생성할 때 메타데이타 정보 부분에 라벨을 정의하고
서비스는 라벨 셀렉터에서 특정 라벨을 가지는 pod만 선태개서 서비스에 묶게 되는 것이다.
kind: Service
apiVersion: v1
metadata:
  name: my-service
spec:
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9376



리소스 종류가 Service 이기 때문에, kind는 Service로 지정하고,

스크립트를 실행할 api 버전은 v1으로 apiVersion에 정의했다.

메타데이타에 서비스의 이름을 my-service로 지정하고

spec 부분에 서비스에 대한 스펙을 정의한다.

selector에서 라벨이 app:myapp인 Pod 만을 선택해서 서비스에서 서비스를 제공하게 하고

포트는 TCP를 이용하되, 서비스는 80 포트로 서비스를 하되, 서비스의 80 포트의 요청을 컨테이너의 9376 포트로 연결해서 서비스를 제공한다. 



출처: https://bcho.tistory.com/1256?category=731548 [조대협의 블로그]

보면 selector에서 app:myapp 을 한순간 같은 라벨이 metadata.label 에 정의 되어있는 pod들을 선택해서
가져가게 되는 것이다. 
포트는 TCP로 쓰되, 서비스는 80번 포트로 서비스 된다. 서비스의 80 포트의 요청은
각 컨테이너의 9376 포트로 연결해서 서비스를 제공하겠다는 이야기이다.

* Name space
네임스페이스는 한 클러스터 안에서 분리를 할 때 쓰인다.
즉 pod와 service가 각 네임스페이스 별로 생성, 관리가 될 수 있고 사용자의 권한도 네임스페이스 단위로
부여할 수 있다.
한 클러스터에 , 개발/운영/테스트 환경이 있을때 클러스터 하나를 세개로 나눠서 관리하는 것이다.
** 각 네임스페이스별로 리소스의 quota( 할당량)을 지정할 수 있다.** 
다른 네임스페이간의 pod라도 통신은 가능하다. 물리적으로는 붙어있으니까~
물론 네트워크 policy를 통해서 차단은 가능하다.

참고 자료 네임 스페이스에 대한 베스트 프랙틱스 : https://cloudplatform.googleblog.com/2018/04/Kubernetes-best-practices-Organizing-with-Namespaces.html

https://kubernetes.io/blog/2016/08/kubernetes-namespaces-use-cases-insights/

* 라벨 (label)
쿠버네티스의 리소스를 선택하느데 사용이 된다. 특정 리소스만 deploy 하거나 update하거나 service에 연결하거나.
아니면 특정 라벨로 선택된 리소스에만 네트워크 접근 권한 부여도 가능.
label은 metadata 섹션에서 key: value 값으로 지정, 여러 라벨을 가질 수 있다.

selector** 는 label selector를 지칭한다. 오브젝트 스펙에서 selector라고 정의하고 라벨 조건을 적어놓으면,
그 리소스만 선택할 수 있는 것ㅇ디ㅏ.
 Equaility based selector와, Set based selector 가 있다.

Equality based selector는 같냐, 다르냐와 같은 조건을 이용하여, 리소스를 선택하는 방법으로

- environment = dev

- tier != frontend

이처럼 같은지 다른지 조건에 따라서 리소스를 선택한다.
이보다 improved 된 selector 방식은 set based selector. 집합 개념을 사용한다.
- environment in (production,qa) 라고 하면, environment가 production이나 qa인 경우이고,
- tier notin (frontend,backend) 라면 environment가 frontend 도 아니고 backend도 아닌 리소스를 선택하는 것.

다음 예제는 my-service 라는 이름의 서비스를 정의한것으로 셀렉터에서 app: myapp 정의해서 Pod의 라벨 app이 myapp 것만 골라서 이 서비스에 바인딩해서 9376 포트로 서비스 하는 예제이다.



kind: Service
apiVersion: v1
metadata:
  name: my-service
spec:
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9376

보면 spec 부분에서 selector을 넣어주는 것을 볼 수 있다.
맨 아래 타겟 포트는 외부에서 IP:80 으로 들어온 정보를 다 해당컨테이너의 9376포트로 포워딩시키는 것.

이런 4개의 기본 오브젝트로 어플리케이션을 설정하고 배포하는 것이 가능한데, 
kubernetes controller 로 쉽게 관리한다. 
컨트롤러는 기본 오브젝트 생성과 관리하는 역할.
_______________________________________________
##### controller. 컨트롤러. ( replication controller(RC), replication set(rs), DaemonSet,Job,StatefulSet, Deployment) 

* replication controller 
 pod를 관리하는 역할을 한다. 이는 크게 3개의 파트. 
 1.Replica의 수, 2. Pod Selector , 3. Pod Template
 1. Replica 수: RC에 의해서 관리되는 POD의 수인데, 그 숫자만큼 pod의 수를 유지하도록 한다.
 이 replica 수가 3이면, 3개의 pod만 띄우고, 이보다 pod가 모자라면, 새 pod를 띄우고, 이보다 많으면 남는 pod를 삭제한다.
 2.Pod Selector: 라벨을 기반으로 하여 RC가 관리한 pod를 가지고오는데 사용
 3. Pod template pod를 추가로 생성해야 할 때 어떻게 pod를 만들지, pod에 대한 정보 ( 도커 이미지, 포트, 라벨) 에 대한
 정보가 필요한데 이를 pod template에서 정의한다.

이미 running 중인 pod가 있는데 RC 리소스를 생성하면, pod의 라벨이 RC의 라벨과 일치하면 새롭게 생성된
RC의 컨트롤을 받는다. RC에 정의되어있는 replica 수보다 pod 개수가 많으면 pod를 삭제하고 모자르면 
template 정보에 따라 pod를 생성하느데, 기존에 생성된 pod가 template의 spec과 다르더라도
pod를 삭제하진 않는다. 

* ReplicaSet
RS는 Replication Controller의 새 버전이다. 
Replica set은 Set 기반의 selector을 사용하고 RC는 equality 기반 Selector를 이용할 뿐.

*Deployment.
 위 RS나 RC보다 상위의 추상화 개념이다. 실제로는 RS나 RC를 바로 쓰기보단 DEPLOYMENT로 해결한다.
 ###### 쿠버네티스에서의 deployment
 deployment는 pod 배포를 위해서 RC를 생성하고 관리하는 역할을 한다. 
![Deployment](https://t1.daumcdn.net/cfile/tistory/996368425B02D9C734)

사실 RC, RS,Deployment는 일반적인 웹서버같은 워크로드에 대해 Pod를 관리하기 위한 controller이다.

데이터베이스, 배치 작업, 데몬 서버와 같이 다양한 형태의 워크로드 모델이 존재하는데, 
pod의 운영을 다양한 시나리오에 맞게 할 수 있다. 
___________
Job
워크로드 모델중에서 배치나 한번 실행되고 끝나는 형태의 작업이 있을 수 있다.

예를 들어 원타임으로 파일 변환 작업을 하거나, 또는 주기적으로 ETL 배치 작업을 하는 경우에는 웹서버 처럼 계속 Pod가 떠 있을 필요없이 작업을 할때만 Pod 를 띄우면 된다. 

이러한 형태의 워크로드 모델을 지원하는 컨트롤러를 Job이라고 한다.

job에 의해 관리되는 pod는 job이 끝날때 pod를 같이 종료한다. 
배치 작업의 경우 작업을 한번만 실행할 수 도 있지만, 같은 작업을 연속해서 여러번 수행하는 경우가 있다. (데이타가 클 경우 범위를 나눠서 작업하는 경우) 이런 경우를 위해서 Job 컨트롤러는 같은 Pod를 순차적으로, 여러번 실행할 수 있도록 설정이 가능하다. Job 설정에서 completion에 횟수를 주면, 같은 작업을 completion 횟수만큼 순차적으로 반복한다
즉 pod를 다시 생성하는 데에 대한 불이익은 거의 없을지도 모른다. 
parallelism을 가능케 할 수도 있다.

출처: https://bcho.tistory.com/1257?category=731548 [조대협의 블로그]
ClusterIP
디폴트 설정으로, 서비스에 클러스터 IP (내부 IP)를 할당한다. 쿠버네티스 클러스터 내에서는 이 서비스에 접근이 가능하지만, 클러스터 외부에서는 외부 IP 를 할당  받지 못했기 때문에, 접근이 불가능하다.
NodePort
클러스터 IP로만 접근이 가능한것이 아니라, 모든 노드의 IP와 포트를 통해서도 접근이 가능하게 된다. 예를 들어 아래와 같이 hello-node-svc 라는 서비스를 NodePort 타입으로 선언을 하고, nodePort를 30036으로 설정하면, 아래 설정에 따라 클러스터 IP의  80포트로도 접근이 가능하지만, 모든 노드의 30036 포트로도 서비스를 접근할 수 있다. 
<img width="392" alt="99ACBB4F5B288E161A" src="https://user-images.githubusercontent.com/47310668/88256228-a8d7f300-ccf5-11ea-8013-ca28f8cf34e4.png">

Load Balancer
보통 클라우드 벤더에서 제공하는 설정 방식으로, 외부 IP 를 가지고 있는 로드밸런서를 할당한다. 외부 IP를 가지고 있기  때문에, 클러스터 외부에서 접근이 가능하다. 



##### 마스터와 노드.
<https://bcho.tistory.com/1256?category=731548>
한 클러스터에 마스터가 있고 노드들이 있다. 클러스터를 관리하는 컨트롤러가 마스터이며, 컨테이너가 배포되는
머신인 노드가 존재한다.

기본 구성단위가 되는 basic object** 들이 있고, 이 기본 오브젝트를 생성하고 관리하는 컨트롤러로 이루어진다.
우리가 yaml 파일에서 보았던 object spec은 
오브젝트의 특성을 기술한 것이다. 설정정보.

기본 오브젝트는 pod, service, volume, namespace.
각각 컨테이너화 된 어플리케이션, 로드밸런서, 디스크, 패키지명 정도로 생각할 수 있다.

apiVersion: v1

kind: Pod

metadata:

  name: nginx

spec:

  containers:

  - name: nginx

    image: nginx:1.7.9

    ports:

    - containerPort: 8090



apiVersion은 이 스크립트를 실행하기 위한 쿠버네티스 API 버전이다 보통 v1을 사용한다.

kind 에는 리소스의 종류를 정의하는데, Pod를 정의하려고 하기 때문에, Pod라고 넣는다.

metadata에는 이 리소스의 각종 메타 데이타를 넣는데, 라벨(뒤에서 설명할)이나 리소스의 이름등 각종 메타데이타를 넣는다

spec 부분에 리소스에 대한 상세한 스펙을 정의한다.

Pod는 컨테이너를 가지고 있기 때문에, container 를 정의한다. 이름은 nginx로 하고 도커 이미지 nginx:1.7.9 를 사용하고, 컨테이너 포트 8090을 오픈한다.



출처: https://bcho.tistory.com/1256?category=731548 [조대협의 블로그]

왜 컨테이너를 pod 단위로 배포하게 될까?
pod 내의 컨테이너는 IP와 port를 공유해. 두 개의 컨테이너가 하나의 pod를 통해서 배포되었을 때,
localhost를 통해서 통신이 가능하다. 아하. 그러니까 컨테이너 A가 8080, 컨테이너 B가 7001로 deployment가
이루어졌을 때, A는 B에 대해서 localhost:7071로 호출가능하고, B는 A를 localhost:8080으로 호출할 수 있다.
같은 pod 의 컨테이너 사이에는 디스크 볼륨을 공유할 수 있다.
즉 다른 컨테이너에 있는 파일을 읽어올 수 있는 것이다.


###### 현재상황
나는 마스터노드로 설정할 서버를 가지고 있고
현재 white (맨 왼쪽) black( 그다음왼쪽) 이 각각 worker 과 master로 구성되어있다.
worker노드는 설정이 되어있는데
내가 가진 master 노드 ( 서버) 는 설정이 안되어 있으니 그거 설정을 해야 한다.
다만 ifconfig를 해보면 , docker0 이라는 interface가 보일텐데
만약 docker 의 컨테이너가 IP를 받는다면 도커로부터 ip를 할당받을 텐데
그러면 같은 ip를 가지고 있는 컨테이너 사이의 통신이 원활할까? 는 거의 아닐것이다.
broadcast를 했을때 목적지가 자신인 패킷이 보내질 수 도 있는 것이다.
NAT가 필요한 상황처럼 보면된다.

쿠버네티스는 CNI를 쓰라고 해서 그 CNI중 하나인 flannel 을 통해서
NAT같은 역할을 하게 해준다.
이를테면 Flannel에서 각 컨테이너에 IP를 할당 해주고, flannel IP를 가진 패킷이
나간다면, flannel 이 먼저 udp header을 추가로 씌워주고, 플라넬이 점검을 한번 하게 한다.
flannel 을 통하면 각각 다른 IP를 가진 것이 확정적이므로 flannel을 통해서 정보를 전송할 수 있게 된다.

이제 내 목표는 master 서버를 다 설정하고
worker 노드를 내 클러스터 (내 master 서버와 같은 클러스터) 에 집어넣는것!
kubectl join 이런거>

아참, 플라넬은 docker 아래 kubernetes 아래에 위치한다. 그 밑에 노드가 있는 셈.
따라서 원래는 docker0 라는 interface가 내 노드의 interface와 연결되어서 
단순 포워딩으로 정보를 전송했다. 


## 2020-07-22 today I learned
#### mechanism flow
_______
![HPA mechanism](https://user-images.githubusercontent.com/47310668/88129685-abfab280-cc13-11ea-8e64-5d516600dcf6.png)

오늘은 개괄적인 명령어, 쿠버네티스 개념정리를 마칠 것이다. 
##### 궁금증
* kubectl describe service를 하면이 여러 ip 가 나온다. 
tutorial을 진행하다보니 그 ip를 쓰는 것이 아닌 minikube ip 라는 것을 사용.
물론 거기 나오는 node ip를 쓰기도 하는데, 그 node ip는 사용하면 node port가 아닌 내부 포트번호를
써야지만 접속이 가능해진다. 이 서비스를 구성할 때 node port 옵션으로 구성했는데
아마 클러스터의 ip가 minikube ip와 같다고 생각한다. 그래서 클러스터에 access하면서 서비스의 load balancing을 거치는 것이었다 라고 생각이 든다. 
하지만 여전히 Node IP : Node Port로 access가 안되는 것에서는 의문이 든다.
NODE IP : NODE PORT로 접속했을 때 load balancing을 통하여 또는 NAT기법을 같이 사용하면서 각 pods에 
명령이 연결되도록 한 줄 알았는데 그게 아니었던 것이다.
POD들이 쓰는 8080 port로만 연결이 가능했던 것이다. NODE IP : PODS PORT.
이 구조가 궁금하다. 
________

#### kubectl 설치

```bash
curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
```
로 다운받고,
```bash
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
kubectl version --client
```
자 이제 클러스터를 구성해야 한다.
minikube를 통해서 클러스터를 구성한다고 하여, 
<https://kubernetes.io/ko/docs/setup/learning-environment/minikube/>
<https://kubernetes.io/ko/docs/tasks/tools/install-minikube/> 이걸로 설치하고 위의 링크를
따른다.
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 \
  && chmod +x minikube
를 입력하고
minikube start 를 쳤다.
다만 sudo apt install qemu 를 해서 hypervisor를 하나 설치해 놓았다.
![kube install](https://user-images.githubusercontent.com/47310668/88148158-2be74380-cc39-11ea-9c24-cbdaebd4a2b1.png)

간단한 HTTP 서버인 echoserver 이미지를 사용해서 쿠버네티스 디플로이먼트를 만들고 --port를 이용해서 8080 포트로 노출해보자.

kubectl create deployment hello-minikube --image=k8s.gcr.io/echoserver:1.10

deployment.apps/hello-minikube created 와 같이 생성이 되었다.
![kube install2](https://user-images.githubusercontent.com/47310668/88148643-deb7a180-cc39-11ea-8d97-566839257ab7.png)
```bash
비스 상세를 보기 위해서 노출된 서비스의 URL을 얻는다.

minikube service hello-minikube --url
```
이렇게 minikube start를 통해서 kubernetes cluster를 구성할 수 있다. 
이는 단일 노드 쿠버네티스 클러스터를 구동하는 가상 머신을 생성하고 구성한다. 

https://kubernetes.io/docs/tutorials/stateless-application/expose-external-ip-address/
오늘은 이내용으로 정리를해본다.
내일은 나머지 예제들과 
<https://github.com/kubernetes/examples/tree/master/>
여기있는 example들과, 
<https://zerobig-k8s.tistory.com/16?category=297761> 이 블로그글을 병행해가며 익혀나간다.

일단 minikube 로 클러스터 (마스터와 노드를 구성하는 것) 이 맞는지 먼저 해결해야 할 것 같다.
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

%%이런 사진 올리는버: issue 탭에서 new 한다음에 텍스트적는공간에 드래그앤드랍하면 됨.
(https://hanee24.github.io/2017/12/21/how-to-upload-image-with-github-readme/ )

*kubectl
- replicaset 명세를 yml 파일로 정의하고 kubectl 도구를 이용해서 replicaset 생성 명령을 API server에전달
- api server는 새 ReplicaSet Object를 etcd에 저장


*kube controller 
- kube Controller에 포함된 ReplicaSet Controller 가 ReplicaSet을 감시하다가 ReplicaSet에 정의된 Label Selector 조건을 만족하는 Pod 이 존재하는지 체크. 
-해당 라벨의 pod이 없으면 ReplicaSet의 Pod 템플릿을 보고 새로운 Pod을 생성 ( 이 생성 또한 API server에 전달되어 etcd에 저장. 
- 한 replicaset에 적어도 한 pod가 있어야 해서 그런가보다.

*kube scheduler
- kube scheduler는 할당되지 않은 pod가 있는지 체크, 있으면 조건에 맞는 Node를 찾아 pod를 할당

*Kubelet
- 자신의 노드에 할당되었지만 아직 생성되지 않은 pod이 있는지 체크.
- 생성되지 않은 pod이 있으면 명세를 보고 pod를 생성
- pod의 상태를 주기적으로 API Server에 전달.

#### 도커 이해 해보자
__________________
(https://subicura.com/2017/01/19/docker-guide-for-beginners-1.html)

##### container
격리된 공간에서 프로세스가 동작하는 기술을 말한다. 
기존에 OS 가상화는 호스트 OS 위에 게스트 OS를 가상화 (VMWARE, Virtual Box) 느려!
그래서 CPU 가상화 기술을 통해 KVM이나 Xen 이 등장. 전체 OS를 가상화 하진 않아서 성능이 향상 되었다.
![](https://subicura.com/assets/article_images/2017-01-19-docker-guide-for-beginners-1/vm-vs-docker.png)

어쩄던 추가적으로 OS를 설치해야 했는데, 프로세스만을 격리시키는 방식이 등장하였다.

* 하나의 서버에 여러개의 컨테이너를 실행하면 서로 영향을 미치지 않고 독립적으로 실행된다.
실행중인 컨테이너에 접속해서 명령어를 입력할 수도 있고, apt-get 이나 yum으로 패키지를 각각에 설치도 가능. 사용자를 추가하고 여러개의 프로세스를 백그라운드로 실행할 수도 있다.
* CPU나 메모리 사용량을 제한할 수도 있고, 호스트의 특정 포트와 연결하거나 호스트의 특정 디렉토리를 내부
디렉토리 인 것처럼 사용할 수도 있다. 
_________________
![](https://subicura.com/assets/article_images/2017-01-19-docker-guide-for-beginners-1/docker-image.png)
도커에서 가장 중요한 개념은 이미지라는 개념이다.
<b>이미지는 컨테이너 실행에 필요한 파일과 설정값 등을 포함하고 있는 것.</b> 
상태값을 가지지 않고 변하지 않는다. (Immutable). 
같은 이미지로 여러개의 컨테이너를 독립적으로 실행시킬 수 있고, 컨테이너 상태가 변해도 이미지는 immutable. 안 변 해. 
![](https://subicura.com/assets/article_images/2017-01-19-docker-guide-for-beginners-1/image-layer.png)

도커 이미지는 컨테이너를 실행하기 위한 모든 정보를 가지고 있는데, 용량이 수백메가겠지. 
그런데 이미지 위의 파일 하나 수정하는데 수백메가 짜리를 다시 다운받는다면 비효율적.
<b> Layer </b> 라는 개념이 등장하였다. 여러 레이어를 유니온 파일 시스템을 이용해서 하나의 File System으로 사용할 수 있게 해준다. 만약 A B C 로 우분투의 다양한 레이어가 있다면, C의 일부 파일이 변경 되었을 때 그 레이어만 다운받으면 효율적으로 관리할 수 있지. 
컨테이너 생성시에도 기존의 이미지 레이어 위에 read-write layer을 추가해서 이미지 레이어의 내용은 바뀌지 않고, 따라서 여러개의 컨테이너가 생성되도 최소한의 용량만이 사용된다. 

![](https://subicura.com/assets/article_images/2017-01-19-docker-guide-for-beginners-1/image-url.png)


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
