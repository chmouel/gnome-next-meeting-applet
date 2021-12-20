#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

POETRY_NAME_VERSION="$(poetry version)"
PKGNAME=${POETRY_NAME_VERSION% *}
AUTHOR_EMAIL="$(git config --get user.email)"
AUTHOR_NAME="$(git config --get user.name)"
RELEASE=1
image_name=${PKGNAME}-aur-builder
finalaction="git push origin master"
gitdir=$(git rev-parse --show-toplevel)
cd "${gitdir}"

while getopts "d" o; do
    case "${o}" in
        d)
            finalaction="echo done"
            ;;
        *)
            echo "Invalid option"; exit 1;
            ;;
    esac
done
shift $((OPTIND-1))

VERSION=${1:-${POETRY_NAME_VERSION#* }}

sudo docker build -f ./packaging/aur/Dockerfile -t ${image_name} .

sudo docker run --rm \
           -v ~/.config/copr:/home/builder/.config/copr \
           -v "${gitdir}":/src \
           -v $SSH_AUTH_SOCK:/ssh-agent --env SSH_AUTH_SOCK=/ssh-agent \
           --name ${PKGNAME}-builder \
           -it ${image_name} \
           /bin/bash -c "set -x;mkdir -p ~/.ssh/;chmod 0700 ~/.ssh && \
                         ssh-keyscan aur.archlinux.org >> ~/.ssh/known_hosts && \
                         git clone --depth=1 ssh://aur@aur.archlinux.org/${PKGNAME} /tmp/${PKGNAME} && \
                         cd /tmp/${PKGNAME} && \
                         git config --global user.email '${AUTHOR_EMAIL}' && \
                         git config --global user.name '${AUTHOR_NAME}' && \
                         sed -E 's#(pkgver=).*#\1$VERSION#' -i PKGBUILD && \
                         sed -E 's#(pkgrel=).*#\1$RELEASE#' -i PKGBUILD && \
                         updpkgsums && \
                         makepkg --printsrcinfo > .SRCINFO && \
                         git clean -f && \
                         git commit -v -m 'Update to ${VERSION}' .SRCINFO PKGBUILD && \
                         ${finalaction}"
