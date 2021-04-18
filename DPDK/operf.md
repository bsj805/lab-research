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

