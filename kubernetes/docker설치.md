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
>>>예ㅔ에에엥 컨테이너

```bash
docker run [OPTIONS] IMAGE[:TAG|@DIGEST] [COMMAND] [ARG...]
``` 
로 도커를 실행한다.
<table>
 옵션	설명
-d	detached mode 흔히 말하는 백그라운드 모드
-p	호스트와 컨테이너의 포트를 연결 (포워딩)
-v	호스트와 컨테이너의 디렉토리를 연결 (마운트)
-e	컨테이너 내에서 사용할 환경변수 설정
–name	컨테이너 이름 설정
–rm	프로세스 종료시 컨테이너 자동 제거
-it	-i와 -t를 동시에 사용한 것으로 터미널 입력을 위한 옵션
–link	컨테이너 연결 [컨테이너명:별칭]
 </table>
