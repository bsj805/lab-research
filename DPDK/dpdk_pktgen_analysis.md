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

![image](https://user-images.githubusercontent.com/47310668/112431601-1192d600-8d83-11eb-9791-963fe4ca3c3e.png)

dpdk 버전 낮추고 20.08, 패킷젠 버전 20.10으로 해결


pci function 1에다 보내도 1이받고, 0한테 보내도 1이받네.


host에서 host로 보낼때 (아래)
![image](https://user-images.githubusercontent.com/47310668/112434130-89163480-8d86-11eb-9c15-843c07cdc005.png)


![image](https://user-images.githubusercontent.com/47310668/112717402-ca961380-8f2f-11eb-8849-6582271105af.png)
host에선 dpdk 20.11 설치하고 (black) 컨테이너에서 20.08로 설치해서 dpdk pktgen사용가능.


ovs-ctl start
sudo ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-init=true
sudo ovs-ctl --no-ovsdb-server --db-sock="$DB_SOCK" start
sudo ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-lcore-mask=0x40
sudo ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-hugepage-dir="/mnt/huge"

vi /etc/fstab에 쓰여진대로 해보았어
0x04면 2번core에 thread생성
<https://developers.redhat.com/blog/2017/06/28/ovs-dpdk-parameters-dealing-with-multi-numa/>

log는
/usr/local/var/log

https://doc.dpdk.org/guides/howto/virtio_user_for_container_networking.html

![image](https://user-images.githubusercontent.com/47310668/112739718-89dede80-8fb1-11eb-9955-e329e1f08640.png)
와같이 구성해볼것.