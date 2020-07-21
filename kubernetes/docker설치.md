### 도커 설치
https://subicura.com/2017/01/19/docker-guide-for-beginners-2.html

______
도커는 리눅스 기반이라, 리눅스상에 설치해야한다. 설치해보자.
먼저 xshell을 통해 내 서버에 들어간다.

 tmux -new 를 통해 새 tmux를 열고

 ctrl a 내 tmux prefix key를 입력 후 , v를 통해 화면을 분할한다
 alt R로 편하게 볼 수 있게 바꿔놓은뒤, 

curl -fsSL https://get.docker.com/ | sudo sh

설치!

docker -v 로 확인해보면 docker가 깔려있음을 알 수 있다.

docker은 기본적으로 root 권한이 필요하다. 

<sudo 없이 사용하기

docker는 기본적으로 root권한이 필요합니다. root가 아닌 사용자가 sudo없이 사용하려면 해당 사용자를 docker그룹에 추가합니다.

```bash
sudo usermod -aG docker $USER # 현재 접속중인 사용자에게 권한주기

sudo usermod -aG docker your-user # your-user 사용자에게 권한주기
```
사용자가 로그인 중이라면 다시 로그인 후 권한이 적용됩니다.>

<마크다운 언어 : https://heropy.blog/2017/09/30/markdown/>

나는 로그아웃을 해야되는줄 알았더니 ssh에서 접속을끊고 로그인하면 로그인이 이루어 지는 것 이었다.  
Tmux 상에서 docker가 sudo 권한을 자꾸 필요로 하는 경우가 있었는데,
<http://www.kwangsiklee.com/2017/05/%ED%95%B4%EA%B2%B0%EB%B0%A9%EB%B2%95-solving-docker-permission-denied-while-trying-to-connect-to-the-docker-daemon-socket/>
<https://programmersought.com/article/85971397610/>
를 참고하면된다. 

제대로 깔려있다면, 
```bash
docker version
```
을 입력했을 때 client 정보랑 server정보가 표시될 것이다.
```bash
Client: Docker Engine - Community
 Version:           19.03.5
 API version:       1.40
 Go version:        go1.12.12
 Git commit:        633a0ea838
 Built:             Wed Nov 13 07:29:52 2019
 OS/Arch:           linux/amd64
 Experimental:      false

Server: Docker Engine - Community
 Engine:
  Version:          19.03.12
  API version:      1.40 (minimum version 1.12)
  Go version:       go1.13.10
  Git commit:       48a66213fe
  Built:            Mon Jun 22 15:44:07 2020
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.2.10
  GitCommit:        b34a5c8af56e510852c35414db4c1f4fa6172339
 runc:
  Version:          1.0.0-rc8+dev
  GitCommit:        3e425f80a8c931f88e6d94a8c831b9d5aa481657
 docker-init:
  Version:          0.18.0
  GitCommit:        fec3683
```

또 내가 선호하는 vim 세팅을 넣어주자.
``` bash
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')
" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'
" The following are examples of different formats supported.
" Keep Plugin commands between vundle#begin/end.
" plugin on GitHub repo
Plugin 'tpope/vim-fugitive'
" plugin from http://vim-scripts.org/vim/scripts.html
" Plugin 'L9'
" Git plugin not hosted on GitHub
Plugin 'git://git.wincent.com/command-t.git'
" git repos on your local machine (i.e. when working on your own plugin),
Plugin 'file:///home/jjeaby/Dev/tools/vim-plugin'
" The sparkup vim script is in a subdirectory of this repo called vim.
" Pass the path to set the runtimepath properly.
Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}
" Install L9 and avoid a Naming conflict if you've already installed a
" different version somewhere else.
" Plugin 'ascenator/L9', {'name': 'newL9'}
" All of your Plugins must be added before the following line
Plugin 'vim-airline/vim-airline'
Plugin 'scrooloose/nerdtree'
Plugin 'airblade/vim-gitgutter'
Plugin 'scrooloose/syntastic'
Plugin 'ctrlpvim/ctrlp.vim'
Plugin 'nanotech/jellybeans.vim'
call vundle#end()            " required
map <Leader>nt <ESC>:NERDTree<CR>
let NERDTreeShowHidden=1
let g:ctrlp_custom_ignore = {
  \ 'dir':  '\.git$\|vendor$',
    \ 'file': '\v\.(exe|so|dll)$'
    \ }
 color jellybeans
 filetype on                                 "vim filetype on
 nmap <F2> :NERDTreeToggle<CR>
 nmap <C-H> <C-W>h                           "왼쪽 창으로 이동
 nmap <C-J> <C-W>j                           "아래 창으로 이동
 nmap <C-K> <C-W>k                           "윗 창으로 이동
 nmap <C-L> <C-W>l                           "오른쪽 창으로 이동
 set nu
 set title
 set showmatch
 set ruler
 if has("syntax")
         syntax on
 endif
 set t_Co=256
 set wrap
 set autoindent
 set smartindent
 set tabstop=4
 set shiftwidth=4
 set softtabstop=4
 set smarttab
 set expandtab
 set paste
 set mouse-=a
 set encoding=utf-8
 set termencoding=utf-8
 set cursorline
 set laststatus=2 
 set statusline=\ %<%l:%v\ [%P]%=%a\ %h%m%r\ %F\
 set ignorecase
 au BufReadPost *
                         \ if line("'\"") > 0 && line("'\"") <= line("$") |
                         \ exe "norm g`\"" |
                         \ endif
 augroup markdown
             " remove previous autocmds
                 autocmd!
                     " set every new or read *.md buffer to use the markdown filetype
                         autocmd BufRead,BufNew *.md setf markdown
                 augroup END
```

%%tmux background color 이 black이라서 visual mode가 안보이는데, 또
%%copy설정도 (clipboard 설정도) tmux에 대해서랑 vim 에 대해서랑 해줘야함.

____________________________________________

근데 왜 버전설정이 저렇게 서버와 클라이언트 정보로 나뉘어져 있을까? 실제로 도커는 
클라이언트와 서버역할을 각각 할 수 있기 떄문이다. 도커 커맨드를 입력하면 도커 클라이언트가
도커 서버로 명령을 전송하고 결과를 받아 터미널에 출력해 준다.


![](https://subicura.com/assets/article_images/2017-01-19-docker-guide-for-beginners-2/docker-host.png)
즉 항상 서버의 도커가 아웃풋을 내려주는 것이다. 

### 컨테이너 실행하기


```bash
docker run [OPTIONS] IMAGE[:TAG|@DIGEST] [COMMAND] [ARG...]
``` 
로 도커를 실행한다.

-d	detached mode 흔히 말하는 백그라운드 모드
-p	호스트와 컨테이너의 포트를 연결 (포워딩)
-v	호스트와 컨테이너의 디렉토리를 연결 (마운트)
-e	컨테이너 내에서 사용할 환경변수 설정
–name	컨테이너 이름 설정
–rm	프로세스 종료시 컨테이너 자동 제거
-it	-i와 -t를 동시에 사용한 것으로 터미널 입력을 위한 옵션
–link	컨테이너 연결 [컨테이너명:별칭]


```bash
docker run ubuntu:16.04 
```
를 하면 ubuntu:16.04 라는 이미지를 찾아서 만약 사용할 이미지가 저장되어 있는지 확인하고
없으면 이미지를 다운로드 한 후에 컨테이너가 실행된다.
컨테이너는 정상적으로 실행되었지만 뭘 하라는 명령어를 전달하지 않았기 때문에 컨테이너가 생성되자마자 종료.
컨테이너 == 프로세스라서 실행중인 프로세스가 없으면 컨테이너가 종료된다.

```bash
docker run --rm -it ubuntu:16.04 /bin/bash

#in container ( 즉 실제 실행되고있는 컨테이너안에서)
$cat /etc/issue
Ubuntu 16.04.1 LTS \n \l

$ ls
```
하면 컨테이너 의 배쉬를 실행시킬 수 있는거다. 
프로세스가 종료되었을 때 컨테이너가 자동으로 삭제되도록 --rm 옵션도 추가되어 있다. -it 옵션은 
키보드 입력을 하기 위함
ctrl + c 하면 컨테이너 종료할 수 있다. 


#### 도커 기본 명령어

```bash 
docker ps [OPTIONS] 
```
컨테이너 목록확인-a 태그는 종료된 것도 표시docker 

```bash 
docker stop [OPTIONS] container이름 [container ID] #둘중 하나
docker rm #위와 동일
```
모든 중지된 컨테이너 삭제?
```bash
docker rm -v $(docker ps -a -q -f status=exited) 
```

뒤에걸로 exited 상태의 컨테이너 아이디를 다 가져와서 한번에 삭제

*pull은 이미지 다운로드, (최신버전으로 받아올 수 있다는 장점)
*rmi 이미지 삭제하기
*logs 컨테이너의 로그를 확인할 수 있다. (실시간으로 확인하려면 -f 옵션)
- 어떻게 로그를 알 수 있지? 표준 스트림 중 stdout, stderr을 수집한다. 컨테이너에서 실행되는 프로그램의 
로그를 stdout으로 설정해주면 ( 로그의 출력 방식을 stdout으로 바꿔주면) 모든 컨테이너의 로그가
동일하게 관리받을 수 있다.
컨테이너의 로그파일이 json 방식으로 저장이 되는데 이 용량이 커지니까 주의해야한다. 
*exec 실행중인 컨테이너에 명령을 내릴 수 있게 된다. run은 무조건 컨테이너를 하나 생성하는거라 달라. 여기도 key 입력이 필요하니 -it옵션을 주어야한다. 이러면 mysql같이 서버만 실행시키고 호스트 컴퓨터의 mysql로 
접속해서 실행했어야 하는것에서 서버의 mysql에 직접 명령을 내릴 수 있게 된다. 

```bash
docker run -d -p 3306:3306 -e MYSQL_ALLOW_EMPTY_PASSWORD=true --name mysql mysql:5.7

docker exec -it mysql /bin/bash

$mysql -uroot

mysql> show databases;

mysql> quit

exit
```

컨테이너를 삭제한다는 건 컨테이너에서 생성된 파일이 사라진다는 뜻입니다. 데이터베이스라면 그동안 쌓였던 데이터가 모두 사라진다는 것이고 웹 어플리케이션이라면 그동안 사용자가 업로드한 이미지가 모두 사라진다는 것입니다. ㄷㄷ
즉 컨테이너 업데이트를 할 때 위에 쌓여있는 정보가 날라가면 안되지 않을까? 즉 컨테이너 삭제시 유지해야 하는 데이터는 컨테이너 내부가 아닌 외부 스토리지에 저장해야한다는 단점이 있다.
클라우드 서비스를 이용하거나, 데이터 볼륨이라는 별도의 스토리지를 컨테이너에 추가해서 사용해야 한다.
데이터 볼륨을 사용하면 해당 디렉토리는 컨테이너와 별도로 저장된다.

*데이터 볼륨을 사용하는 방법
_________________________
호스트의 디렉토리를 마운트해서 사용할 수 있다.
run 명령어에서 -v 로 특정 디렉토리를 컨테이너 안의 특정 디렉토리로 연결 해주자.
-v 라는 것은 volume mount 의 약자.
최신 버전의 이미지를 다운받고 다시 컨테이너를 실행할 때 동일한 디렉토리를 마운트 한다면 그대로 데이터를 사용할 수 있다. 
```bash
# before
docker run -d -p 3306:3306 \
  -e MYSQL_ALLOW_EMPTY_PASSWORD=true \
  --name mysql \
  mysql:5.7

# after
docker run -d -p 3306:3306 \
  -e MYSQL_ALLOW_EMPTY_PASSWORD=true \
  --name mysql \
  -v /my/own/datadir:/var/lib/mysql \ # <- volume mount
  mysql:5.7
  ```
  

* Docker Compose. 
YAML 방식의 설정파일을 이용한 도커의 설정을 관리하기 위한 툴.

_______________________________________
#### 도커 이미지 만들기
![](https://subicura.com/assets/article_images/2017-02-10-docker-guide-for-beginners-create-image-and-deploy/create-image.png)

<https://subicura.com/2017/02/10/docker-guide-for-beginners-create-image-and-deploy.html>

도커는 이미지를 만들기 위해 컨테이너의 상태를 그대로 이미지로 저장하는 방식을 사용한다.
어떤 어플을 이미지로 만들면, 리눅스만 설치된 컨테이너에 어플리케이션을 설치하고 그 상태를 그대로 이미지로 저장한다.
호스트의 디렉토리를 루비가 설치된 컨테이너의 디렉토리에 마운트한다음 그대로 명령어를 실행하면 로컬에 개발 환경을 구축하지 않고 도커 컨테이너를 개발환경으로 사용할 수 있습니다. 어으썸!

도커를 개발환경으로 사용하면 개발=테스트=운영이 동일한 환경에서 실행되는 놀라운 상황이 펼쳐집니다. 이 부분은 재미있는 내용이 많지만, 주제에서 벗어나므로 이 정도만 언급하고 다음 기회에 더 자세히 알아봅니다.
```bash
docker run --rm -p 4567:4567 -v $PWD:/usr/src/app -w /usr/src/app ruby bash -c "bundle install && bundle exec ruby app.rb -o 0.0.0.0"
```
curl https://localhost:4567 과 같이 이 웹서버에 접근해보면 
byeon@uhoontu:~/sinatra$ curl http://localhost:4567
f4f1f0e85b84byeon@uhoontu:~/sinatra$ 와 같이 get을 얻어오는 것을 볼 수 있다.

이제 이미지를 만들 준비가 다 됐다고 한다.
#### image 만들기

도커는 이미지를 만들기 위해 Dockerfil이라는 이미지 빌드용 DSL(Domain Specific Language) 파일을 사용한다. 이는 단순 텍스트 파일로 일반적으로는 소스와 함께 관리된다.
![](https://subicura.com/assets/article_images/2017-02-10-docker-guide-for-beginners-create-image-and-deploy/dockerfile.png)
즉 이런 방식으로 이미지가 만들어진다. 

### 도커 배포하기
컨테이너 배포 방식
컨테이너를 배포하는 방식은 기존 어플리케이션을 배포하는 방식과 차이가 나지.
어떤 언어던 어떤 프레임워크를 쓰던 배포방식이 동일. 이미지를 다운받고 컨테이너를 실행하면 끝이다.
즉 서버에 접속해서 컨테이너를 실행시켜주면 USER들은 어 새 어플이 생겼다 하는거지. 
업데이트도 새 컨테이너를 만들고 이전 컨테이너를 중지하자. 
