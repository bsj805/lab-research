ovs에 dpdk 포트가 연결되었다 하면 poll mod thread 가 돌아 (이 port에 대해)
pmd_thread_main -> (ovs- dpif-netdev.c) dp_netdev_process_rxq_port-> (ovs- netdev.c) netdev_rxq_recv ->
[rx->netdev->netdev_class->rxq_recv 이게] (dpdk rte_ethdev.h) rte_eth_rx_burst 

//이게 0000:03:00.1의 rx queue가 full인데
container에서 제공하는 virtqueue에는 패킷이 충분히 안들어와있다는 거니 

0000:03:00.1의 rx queue -> emc 체크 -> vhost의 virtqueue 과정이 맞다면 emc 체크하고 virtqueue에 넣어주는 과정이 bottleneck이 되는게 맞겠죠? 

rte_ethdev.h를 보면,
dpdk의 함수인데,ethernet device의 receive queue에 burst of input packets를 주는 거래.
retrieved packet들이 rte_mbuf structure에 packet들이 쌓이는거고.

rte_mbuf structure이 *rx_pkts* 라는 배열로 들어오나봐. 여기다 쌓아주는거지 

rte_eth_rx_burst() 라는 함수가 루프를 돌면서 RX ring of receive queue를 파싱하면서 *nb_pkts* 만큼 체크를 한대.
ring에 있는 (파싱이)완료 된 RX descriptor마다 다음 operation을 수행한다.

	1.RX descriptor마다 존재하는 *rte_mbuf* 라는 자료구조를 초기설정한다. NIC에 읳 제공된 정보를 그 rx descriptor에게 넣는다.
	2.*rte_mbuf* 자료구조를 *rx_pkts* 배열의 다음 entry에 저장한다. (ring descriptor마다 rte_mbuf 구조가 있고 rx_pkts에 연속적으로 저장하기 위해 
  ![image](https://user-images.githubusercontent.com/47310668/118901178-96e2d300-b94d-11eb-975f-9d44a0ea305b.png)

	3.replenish( 다시 채우다, 보충하다) RX descriptor를 새 *rte_mbuf* buffer로 채운다 ( init시간에 receive queue와 연결된 메모리 풀에서부터) 


컨트롤러에 의해  여러 receive descriptor에게 input packet이 scatter 되었으면, rte_eth_rx_bust() 함수가 associated 된 *rte_mbuf* 버퍼들을 
패킷의 첫번째 버퍼에 추가한다. 

rte_eth_rx_bust() 함수는 실제로 retrieved 된 패킷들의 수를 return한다. 이는 *rx_pkts* 배열에 공급된 *rte_mbuf* 수를 나타낸다. 
인자로 들어온 *nb_pkts* 는 # of maximum packets to receive인데, 이거랑 return 값이 같다는건, RX queue에 최소 *rx_pkts* 수만큼 패킷이 있다는거고,
다른 receieved packet도 input queue에 남아있을 수 있다. (더 들어오고자 하느 패킷이남아있을 수 있다)

그러니까 이 함수 쓰려면 nb_pkts보다 적은 패킷이 들어올때까지 계속 이 함수를 호출하라. 하는데
![image](https://user-images.githubusercontent.com/47310668/118903508-ea0b5480-b952-11eb-883a-aa90f396518c.png)
이 실행부분을 보면 한번만 부르고 떙이고,


4772  * The rte_eth_rx_burst() function returns the number of packets          
4773  * actually retrieved, which is the number of *rte_mbuf* data structures  
4774  * effectively supplied into the *rx_pkts* array.                         
4775  * A return value equal to *nb_pkts* indicates that the RX queue contained
4776  * at least *rx_pkts* packets, and this is likely to signify that other   
4777  * received packets remain in the input queue. Applications implementing  
4778  * a "retrieve as much received packets as possible" policy can check this
4779  * specific case and keep invoking the rte_eth_rx_burst() function until  
4780  * a value less than *nb_pkts* is returned.     

이렇다는데?

<https://doc.dpdk.org/guides/sample_app_ug/skeleton.html>
dpdk sample app을 보면, configure하는 step이 나와있다. 막 set mtu도 하고, 
우리는 그게 dpdk_eth_dev_port_config


