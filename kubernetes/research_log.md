## 우수학부생 연구학점제


### 2020.09.05

첫번째 미팅

우선, kubernetes 상에서 발생하는 문제라 cni가 관여하지 않는가에 대한 생각이 들었다
-> 문제 단순화해서, 

![image](https://user-images.githubusercontent.com/47310668/92705840-fdf7c300-f38e-11ea-8f7c-32ee60272771.png)

여기서 docker 0만 있는 상태에서 
pod-native간 상태는 어떠한가?

라고 봤을때 여전히 같은 문제가 발생했다.

즉, kubernetes 상에서만 발생하는 문제는 아닐수 도 있다는 생각이 든다.

-> 지금 operf로 해서 나왔던 nf_conntrack은 정말 nat때문에 발생하는 문제일 수도 있다는 생각.
<https://linuxstory1.tistory.com/entry/iptables-%EA%B8%B0%EB%B3%B8-%EB%AA%85%EB%A0%B9%EC%96%B4-%EB%B0%8F-%EC%98%B5%EC%85%98-%EB%AA%85%EB%A0%B9%EC%96%B4>
```bash
iptables --list-rule
```
로 보니까 
![image](https://user-images.githubusercontent.com/47310668/92706719-b6256b80-f38f-11ea-8334-270f144075a4.png)
이런게 있어서.
흠 

forward 룰을 보다보면, 어떤식으로 패킷을 받는것인지 알 수 있지 않을까 싶었다.


![image](https://user-images.githubusercontent.com/47310668/92706625-a27a0500-f38f-11ea-8f6a-a93ea1bc98e0.png)

-A FORWARD -j DOCKER-USER  # append, forward룰,  https://qastack.kr/server/245711/iptables-tips-tricks 에 따르면 그냥 interface를 define하는 것이라한다.
-A FORWARD -j DOCKER-ISOLATION-STAGE- 
-A FORWARD -o docker0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT  패킷이 docker0를 통해서 나갈 때, conntrack이라는 모듈 (connectiont tracking extension == conntrack)을 사용하라는 명령.
ctstate는 conntrack의 일부. related 라 함은, 기존 연결에 속하지만, 새로운 연결을 요청하는 패킷, established는 기존 연결의 일부인 패킷. iptables의 연결 추적 기능! 
이걸 포워딩하겠다는 것은,  docker0에서 나갈 때 기존 연결과 관련된 패킷만 forward하겠다. 
-A FORWARD -o docker0 -j DOCKER    docker 0 를 통해서 나가는 패킷은, DOCKER라는 룰로 점프해라?  DOCKER룰은 docker0로 들어오는 모든 패킷을 return 시키라는데?
-A FORWARD -i docker0 ! -o docker0 -j ACCEPT  docker0를 통해서 들어오는 패킷은 docker0로 나간 것이 아니던 맞던 포워딩해주면된다. 
-A FORWARD -i docker0 -o docker0 -j ACCEPT 
-A FORWARD -s 10.244.0.0/16 -j ACCEPT  //flannel 송신자
-A FORWARD -d 10.244.0.0/16 -j ACCEPT // flannel 수신자
-A OUTPUT -m conntrack --ctstate NEW -m comment --comment "kubernetes service portals" -j KUBE-SERVICES
-A OUTPUT -j KUBE-FIREWALL
-A DOCKER-ISOLATION-STAGE-1 -i docker0 ! -o docker0 -j DOCKER-ISOLATION-STAGE-2  docker0로 들어오는 패킷이 아닌데 docker0로 나간 패킷이면 DOCKER_ISOLATION_STAGE 2로 가라.
-A DOCKER-ISOLATION-STAGE-1 -j RETURN   아니면 리턴~
-A DOCKER-ISOLATION-STAGE-2 -o docker0 -j DROP  // docker0로 나간패킷은 드랍~
-A DOCKER-ISOLATION-STAGE-2 -j RETURN
-A DOCKER-USER -j RETURN


https://ssup2.github.io/theory_analysis/Linux_conntrack/
에 따르면
-A FORWARD -o docker0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

는 docker0에서 포워드 되려는 패킷이 connection tracking helper에 의해 예상된 새로운 connection을 생성하려는 상태거나 현재 존재하는 커넥션을
통해 통신하려는 경우 허용하는 rule을 명령어로 정하고 있다.

iptable에서 nat rule을 설정하면 이와 반대되는 reverse NAT는 iptable에 reverse Nat rule이 없어도 자동으로 수행된다.
이 conntrack Module의 커넥션정보를 바탕으로 암묵적으로 reverse NAT를 수행하기 때문!
![image](https://user-images.githubusercontent.com/47310668/92718069-39e55500-f39c-11ea-80e2-4212a56a8047.png)
아마 이거가 나오는 걸 보니
저패킷이 저렇게 바뀌는 것이아닐까?
