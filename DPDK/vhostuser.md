vhost가무엇인가
<https://www.redhat.com/en/blog/how-vhost-user-came-being-virtio-networking-and-dpdk>

<https://www.redhat.com/en/blog/journey-vhost-users-realm>
일단 우리는 
```
The vhost-net/virtio-net architecture provides a working solution which has been widely deployed over the years. On the one hand the solution is very convenient for a user developing an application running on a VM given that it uses standard Linux sockets to connect to the network (through the host). On the other hand, the solution is not optimal and contains a number of performance overheads which will be described later on. 

In order to address the performance issues we will introduce the vhost-user/virtio-pmd architecture. To understand the details we will review the data plane development kit (DPDK), how OVS can connect to DPDK (OVS-DPDK) and how does virtio fit into the story both on the backend side and the frontend side.
```
즉 
virtio 사용하면 유닉스 소켓으로 패킷전달하는거라
vhost-user/virtio-pmd 아키텍쳐가 등장한거야


왜 DPDK 받는쪽에서도 쓰냐
```
This, however, comes at a cost from usability aspects. In the vhost-net/virtio-net architecture the data plane communication was straightforward from the guest OS point of view: simply add the virtio drivers to the guest kernel and the guest user space applications automatically gets a standard Linux networking interface to work with.
In contrast in the vhost-user/virtio-pmd architecture the guest user space application is required to use the virtio-pmd driver (from the DPDK library) in order to optimize the data plane. This is not a trivial task and requires expertise for properly configuring and optimizing the DPDK usage. 
```

봐봐

기존의 vhost-net/virtio-net 인터페이스를 활용하면
unix socket기반의 send와 recv() 등을 활용해서 송신을 하고 수신을 하는 형식의 데이터 전송이 가능하다.
(Inter Process communication 활용) 
In this post scope, the server of the communication binds a Unix socket to a path in the file system, so a client can connect to it using that path. From that moment, the processes can exchange messages
unix sockets can also be used to exchange file descriptors between processes. 

다만 vhost-user이랑 virtio-pmd를 이용하면 expertise가 필요하지만 부가적인 통신이 필요하지 않기때문에 bypass the kernel 하면서 
overall performance can improve by a factor of 2 to 4. 라서?
Unix sockets are a way to do Inter-Process Communication (IPC) on the same machine in an efficient way. 

왜 기존 virtio가 안좋은가
<https://www.redhat.com/en/blog/deep-dive-virtio-networking-and-vhost-net>
어떻게작동하길래? 
