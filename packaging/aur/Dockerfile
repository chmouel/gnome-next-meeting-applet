FROM archlinux:latest
RUN pacman -Sy python-setuptools python-dephell pacman-contrib openssh binutils git --noconfirm  &&  pacman -Sc --noconfirm

RUN useradd -ms /bin/bash builder
USER builder
WORKDIR /src
