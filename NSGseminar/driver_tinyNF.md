2월 17일 
이도현 박사과정님의 세미나
![image](https://user-images.githubusercontent.com/47310668/108168607-f48f3580-713a-11eb-829e-3ce73ccc7c88.png)

에서 TCP function은 buffer이 필요해.
non-TCP function은 buffer이 안필요해.
bridge나 router는 패킷 하나당 처리가 가능한데,
fire wall은 TCP를 모아서 http 헤더를 만들고 검열해서 문제가 있으면 차단해야되니까 
그런 경우에는 1 by 1 처리가 불가능. 
![image](https://user-images.githubusercontent.com/47310668/108169351-f279a680-713b-11eb-912f-27b6496daf0c.png)
DPDK는 BSD 소켓과는달리 메모리 풀에서 alloc이 되는 구조라고한다.
그래서 정해진 개수의 버퍼들만 사용할 수 있다. 하지만 빠르다는 장점이 있는 것.
그걸 closed 모델 
BSD는 패킷을 받을 때 malloc 즉 운영체제단에서 메모리할당을 해야하기 때문에 느리다. 

초기 initialize 이후에 alloc이나 free가 이뤄지지않고 계속 단계사이에서 돌아다니는 것을 하자는
Tiny NF

일반적으로 NIC에 있는 Ring buffer은 (packet ring)
packet descriptor들이 저장되어있는 자료 저장 층이다. 
일반적인 ring처럼 head와 tail로 구성된 circular. 그래서 head에서 tail까지만 사용가능하다.
근데 원래는 receive와 transmit때 쓰는 ring이 다른데,
transmit과 receive에 쓰는 ring이 똑같으면 어떨까? 이게 tiny NF
링 버퍼에서 가지고 있는게
