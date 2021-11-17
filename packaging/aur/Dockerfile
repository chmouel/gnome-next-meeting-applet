FROM archlinux:latest
RUN pacman -Sy pacman-contrib openssh binutils git --noconfirm  &&  pacman -Sc --noconfirm

RUN useradd -ms /bin/bash builder
USER builder
WORKDIR /src
