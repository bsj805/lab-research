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
