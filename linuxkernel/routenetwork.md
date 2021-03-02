https://www.cyberciti.biz/faq/linux-route-add/

route를 add하니까
sudo ifconfig ens4f1 10.0.0.3 netmask 255.255.255.0 up
로 잡아줬던 NIC끼리 통신을한다.

항상 route -n을 확인해주자.
![image](https://user-images.githubusercontent.com/47310668/109603851-d1ff1280-7b65-11eb-9c7c-6f2b4cf62452.png)
