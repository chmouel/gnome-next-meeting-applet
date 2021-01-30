#!/usr/bin/env bash
set -eux

cd $(git rev-parse --show-toplevel)
NAME=gnome-next-meeting-applet
PPATARGET=chmouel/${NAME}
GPG_KEY=${GPG_KEY}
YUBIKEY=${YUBIKEY:-}
DISTRO_VERSION="groovy"

[[ -n ${GPG_KEY} ]] || {
    echo "You need to setup your GPG_KEY"
    exit 1
}
gpg --list-secret-keys >/dev/null || { echo "You need to have a secret GPG key"; exit 1 ;}

sudo docker build -f debian/Dockerfile -t ${NAME}-builder .

version=$(python3 -c 'import gnome_next_meeting_applet as f;print(f.__version__)')
release=1

fpath=$(readlink -f .)
sudo docker run --rm \
       -v ~/.gnupg:/home/builder/.gnupg \
       -v ${fpath}:/home/builder/build/${NAME}-${version}-${release} \
	    --name ${NAME}-builder \
       --env USER=${USER} \
       --env PPATARGET=${PPATARGET} \
       --env GPG_KEY=${GPG_KEY} \
       --user root \
       -it ${NAME}-builder #\
       # /bin/bash -c "gpg-agent --pinentry-program /usr/bin/pinentry --daemon && \
       #               cd ${NAME}-${version}-${release} && \
       #               dch -M -v ${version}-${release} -D ${DISTRO_VERSION} \"new update\" && \
       #               debuild -S --force-sign -k${GPG_KEY} && \
       #               cd .. && \
       #               echo dput ppa:${PPATARGET} *source.changes"
