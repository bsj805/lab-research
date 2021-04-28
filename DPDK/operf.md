pktgen으로 돌리면, pktgen을 실행시키는데 (화면을 띄우는데) 
core를 100%로 사용하기 때문에, 정확한 성능 측정이 어렵다.
따라서, operf tool을 이용해서 어떤 함수에서 얼마만큼의 cpu를 잡아먹는지를 테스트해보고자 한다.

<https://idchowto.com/?p=15485>
operf는 profiling을 통해서 
```
• 실행중인 프로세스의 CPU Usage를 프로파일링
• 실행중인 프로세스의 어떤 함수가 CPU 자원을 많이 사용하는지를 식별
• 특정 함수가 많은 자원을 사용할 경우, 프로그램은 그 함수 콜을 줄일 수 있는 방법으로 재설계될 수 있음
• 이는 CPU 사용률이 낮은 장비에서는 별로 쓸모가 없음
```
<https://ubunlog.com/ko/oprofile-%ED%86%B5%EA%B3%84-%ED%94%84%EB%A1%9C%ED%8C%8C%EC%9D%BC-%EC%9A%B0%EB%B6%84%ED%88%AC/>
operf 사용방법 

사실 oprofile이다.
<http://manpages.ubuntu.com/manpages/bionic/man1/oprofile.1.html>
이게 manual page이다. 

```

sudo apt install oprofile 
• How to use
   – $ opcontrol --start (--no-vmlinux) (커널 자체에 대한 프로파일을 할 필요가 없을 때 해줌)
   – 여기에서 실제 벤치마킹 수행
   – $ opcontrol --dump
   – $ opcontrol --shutdown
   – $ opreport -l  /usr/local/bin/mysqld
```

원래는
```
sudo operf -s //systemwide man operf로 매뉴얼봐
opreport 
로 본다.
sudo rm -Rf oprofile_data
이후 이걸로 지워준다

나는
sudo operf -s -c 
opreport -x 
```

![image](https://user-images.githubusercontent.com/47310668/115147702-426ede00-a097-11eb-9af4-839abc772027.png)

패킷젠쪽에서 찍어봐도 operf로는 불가능한거같다


sudo operf ./tools/run.py defb로 해봐도 
![image](https://user-images.githubusercontent.com/47310668/115147773-9b3e7680-a097-11eb-9391-4a72ec20c9aa.png)

이런결과정도만 나온다.

https://cslab.cbnu.ac.kr/board/bbs/board.php?bo_table=libfaq&wr_id=29&page=15

opreport -l 로 해봐

![image](https://user-images.githubusercontent.com/47310668/115147873-0be59300-a098-11eb-8b99-885b56e5635b.png)

이런식으로 어떤함수가 썼는지가 나온다.


지금 pktgen에서 display processing이 lcore 2
rx processing은 3번
tx porcessing은 4번

white@ Pktgen디렉토리의 pktgen_operf_10sec.txt
ovs-dpdk성능테스트 <https://o365skku-my.sharepoint.com/:x:/g/personal/bsj805_o365_skku_edu/ES2rIdjVQm1OmLuwzIMVEZgBM9eoK84I3SVY3LoEE8d2tA?e=aY1jj9>
에서도 확인할 수 있다.
tx는 pcap_filter에 다 썼고
rx는 ixgbe_recv_pkts_lro
ixgbe_xmit_pkts 에 다썼다.




부족하면 http://www.brendangregg.com/blog/2014-06-22/perf-cpu-sample.html를 시도해봐도될듯

pktgen_operf_tx_10sec.txt은 10초동안 192.168.1.1로 보낸거
9.5gb/s로 보낸다

보내기를 하니까 tx코어쪽에 11%의 ixgbe_crypto_add_sa가 생겼다
10%의 ixgbe_pf_host_configure가 생겼고
51%의 pcap_filter
9%의 set_page_size
정도?




45.2478		librte_pmd_ixgbe.so.20.0.3	pktgen	ixgbe_xmit_pkts
31.7049		pktgen	pktgen	/root/Pktgen-DPDK-pktgen-20.10.0/usr/local/bin/pktgen
13.3982		librte_pmd_ixgbe.so.20.0.3	pktgen	ixgbe_recv_pkts_lro
2.8057	librte_mbuf.so.20.0.3	pktgen	rte_pktmbuf_free
2.4773		librte_mbuf.so.20.0.3	pktgen	rte_pktmbuf_clone
1.9923		librte_mbuf.so.20.0.3	pktgen	__rte_pktmbuf_linearize
1.2427		librte_mbuf.so.20.0.3	pktgen	rte_pktmbuf_pool_create_by_ops
0.5882		ld-2.31.so	pktgen	/usr/lib/x86_64-linux-gnu/ld-2.31.so
0.3798		librte_mbuf.so.20.0.3	pktgen	rte_pktmbuf_pool_init
0.0075		igb	3:0-even	/igb
0.0073		kallsyms	pktgen	asm_sysvec_apic_timer_interrupt
0.0064	kallsyms	pktgen	prepare_exit_to_usermode
0.0051		kallsyms	pktgen	__update_load_avg_se
0.0044		kallsyms	pktgen	__update_load_avg_cfs_rq
0.0039		kallsyms	pktgen	__irqentry_text_end
0.0035		kallsyms	pktgen	_raw_spin_lock_irqsave
0.0031		kallsyms	pktgen	read_tsc
0.003		kallsyms	pktgen	update_curr
![image](https://user-images.githubusercontent.com/47310668/116279384-6ed6d880-a7c2-11eb-9a4d-a24a2ca16aa8.png)

이게 rx 할때 이런 값들이 보이는거같다.

<https://access.redhat.com/solutions/3394851> 여기
vhost user의 작동원리

https://medium.com/@jain.sm/kvm-and-qemu-as-linux-hypervisor-18271376449
vhost에서 왜 virtqueue를쓰는가.
