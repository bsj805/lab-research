![image](https://user-images.githubusercontent.com/47310668/112301714-94615580-8cdd-11eb-87b9-a113468add56.png)
core을 2, 3-4
로 하고 

[3].0 [4].1 로 해보았어.
![image](https://user-images.githubusercontent.com/47310668/112302971-11d99580-8cdf-11eb-94c2-aaa2b85a9b0e.png)
이게 원래 [3:4] [5:6] 한거.


한쪽으로만 보내지는게 이상하다
https://stackoverflow.com/questions/65427335/pkt-gen-dpdk-not-sending-any-packets-issue

dpdk가 shared mode로 build되어서그런걸지도
```bash
find / -name "librte_*.so" | grep ena
```
