#!/usr/bin/env bash
set -eux

cd $(git rev-parse --show-toplevel)
POETRY_NAME_VERSION="$(poetry version)"
NAME=${POETRY_NAME_VERSION% *}
VERSION=${POETRY_NAME_VERSION#* }
PPATARGET=chmouel/${NAME}
RELEASE=1
GPG_KEY=${GPG_KEY:-""}

finalaction="debuild -S --force-sign -k${GPG_KEY} && cd .. && dput ppa:${PPATARGET} *source.changes"
echodebug=

while getopts "vd" o; do
    case "${o}" in
    v)
        echodebug="echo"
        ;;
    d)
        finalaction="/bin/bash"
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
    esac
done
shift $((OPTIND - 1))

[[ -n ${GPG_KEY} ]] || {
    echo "You need to setup your GPG_KEY"
    exit 1
}
gpg --list-secret-keys >/dev/null || {
    echo "You need to have a secret GPG key"
    exit 1
}

for dockerdistroversion in latest rolling; do
    dockerfile=/tmp/Dockerfile.${dockerdistroversion}.$$
    sed "s/FROM ubuntu:.*/FROM ubuntu:${dockerdistroversion}/" ./packaging/debian/Dockerfile >${dockerfile}
    sudo docker build -f ${dockerfile} -t ${NAME}-${dockerdistroversion}-builder .
    fpath=$(readlink -f .)
    pname=${NAME//-/_}
    sudo docker run --rm \
        -v $HOME/.gnupg:/home/builder/.gnupg:ro \
        -v /run/user/$(id -u)/:/run/user/$(id -u)/:ro \
        -v ${fpath}:/home/builder/build/src \
        --name ${NAME}-${dockerdistroversion}-builder \
        --env USER=${USER} \
        --env PPATARGET=${PPATARGET} \
        --env GPG_KEY=${GPG_KEY} \
        -it ${NAME}-${dockerdistroversion}-builder \
        /bin/bash -xec "echo gpg-agent --pinentry-program /usr/bin/pinentry --daemon && \
                         ${echodebug} tar xzf src/dist/${pname}-${VERSION}.tar.gz && \
                         ${echodebug} mv ${pname}-${VERSION}  ${NAME}-${VERSION} && \
                         ${echodebug} cp -a src/packaging/debian ${NAME}-${VERSION}/ && \
                         ${echodebug} cd ${NAME}-${VERSION} && \
                         ${echodebug} dch -M -v ${VERSION}-${RELEASE}~\`lsb_release -cs\`1 -D \`lsb_release -cs\` \"new update\" && \
                         ${echodebug} dpkg-source -b . && \
                         ${finalaction}"
    rm -f ${dockerfile}
done
