#!/usr/bin/env bash
set -eux

cd $(git rev-parse --show-toplevel)
NAME=gnome-next-meeting-applet
PPATARGET=chmouel/${NAME}
GPG_KEY=${GPG_KEY}
YUBIKEY=${YUBIKEY:-}
DISTRO_VERSION="groovy"
RELEASE=4
VERSION=$(python3 -c 'import gnome_next_meeting_applet as f;print(f.__version__)')


[[ -n ${GPG_KEY} ]] || {
    echo "You need to setup your GPG_KEY"
    exit 1
}
gpg --list-secret-keys >/dev/null || { echo "You need to have a secret GPG key"; exit 1 ;}

for dockerdistroversion in latest rolling;do
    dockerfile=/tmp/Dockerfile.${dockerdistroversion}.$$
    sed "s/FROM ubuntu:.*/FROM ubuntu:${dockerdistroversion}/" ./debian/Dockerfile > ${dockerfile}
    sudo docker build -f ${dockerfile} -t ${NAME}-${dockerdistroversion}-builder .
    fpath=$(readlink -f .)
    sudo docker run --rm \
           -v ~/.gnupg:/home/builder/.gnupg \
           -v ${fpath}:/home/builder/build/src \
            --name ${NAME}-${dockerdistroversion}-builder \
           --env USER=${USER} \
           --env PPATARGET=${PPATARGET} \
           --env GPG_KEY=${GPG_KEY} \
           -it ${NAME}-${dockerdistroversion}-builder \
           /bin/bash -c "gpg-agent --pinentry-program /usr/bin/pinentry --daemon && \
                         cp -a src/ ${NAME}-${VERSION} && rm -rf ${NAME}-${VERSION}/.git && \
                         cd ${NAME}-${VERSION} && \
                         dch -M -v ${VERSION}-${RELEASE}~\`lsb_release -cs\`1 -D \`lsb_release -cs\` \"new update\" && \
                         dpkg-source -b . && \
                         debuild -S --force-sign -k${GPG_KEY} && \
                         cd .. && \
                         dput ppa:${PPATARGET} *source.changes"
            rm -f ${dockerfile}
done
                         
