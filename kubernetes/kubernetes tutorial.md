
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
