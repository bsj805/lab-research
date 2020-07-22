
#### interactive tutorial using minikube
<https://kubernetes.io/docs/tutorials/kubernetes-basics/create-cluster/cluster-interactive/>

먼저 
```bash
kubectl version
```
으로 kubectl이 configured 되었는지 체크해야 한다. 

```bash
kubectl cluster-info
```
으로 kubectl 클러스터의 정보를 알 수 있다.
클러스터의 노드에 대한 view를 얻기 위해서
```bash
kubectl get nodes
```
가 있는데. 
이러면 일단, 

<https://zerobig-k8s.tistory.com/10> 를 통해 proxy server 와 클러스터의 관계를 좀 파악할 수 있을 것이다.
이는 <https://kubernetes.io/docs/tutorials/kubernetes-basics/deploy-app/deploy-interactive/> 의 내용이 기반이다.

![HPA mechanism](https://user-images.githubusercontent.com/47310668/88129685-abfab280-cc13-11ea-8e64-5d516600dcf6.png)

