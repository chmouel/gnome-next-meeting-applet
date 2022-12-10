#!/usr/bin/env bash
set -feux
POETRY_NAME_VERSION="$(poetry version)"
NAME=${POETRY_NAME_VERSION% *}
VERSION=${POETRY_NAME_VERSION#* }
AUTHOR_EMAIL="$(git config --get user.name) <$(git config --get user.email)>"
RELEASE=1
finalaction="copr-cli build ${NAME} /tmp/${NAME}-${VERSION}-1\$(rpm --eval '%{?dist}').src.rpm"

gitdir=$(git rev-parse --show-toplevel)
cd "${gitdir}"
image_name=gnome-next-meeting-applet-rpm-builder

echo ${finalaction}

while getopts "rd" o; do
    case "${o}" in
        r)
            finalaction="rpmbuild -ba /tmp/${NAME}.spec --define '_sourcedir /tmp/' --define '_srcrpmdir /tmp/'"
            ;;
        d)
            finalaction="echo rpmbuild -ba /tmp/${NAME}.spec --define \'_sourcedir /tmp/\' --define \'_srcrpmdir /tmp/\'; /bin/bash"
            ;;
        *)
            echo "Invalid option"; exit 1;
            ;;
    esac
done
shift $((OPTIND-1))

[[ -e ~/.config/copr ]] || {
    echo "Cannot find ~/.config/copr"
    exit 1
}

sudo docker pull fedora:latest
sudo docker build -f ./packaging/rpm/Dockerfile -t ${image_name} .

pname=${NAME//-/_}
sudo docker run --rm \
           -v $HOME/.config/copr:/home/builder/.config/copr \
           -v "${gitdir}":/src \
           --name gnome-next-meeting-applet-builder \
           -it ${image_name} \
           /bin/bash -c "sed 's/_VERSION_/${VERSION}/' /src/packaging/rpm/${NAME}.spec > /tmp/${NAME}.spec && \
                         sed -i -e \"/^%changelog/a\* $(date '+%a %b %-d %Y') ${AUTHOR_EMAIL} - ${VERSION}-${RELEASE}\n- New vesion ${VERSION}\n\" /tmp/${NAME}.spec && \
                         cp -v dist/${pname}-${VERSION}.tar.gz /tmp/${NAME}-${VERSION}.tar.gz && \
                         rpmbuild -bs /tmp/${NAME}.spec --define '_sourcedir /tmp/' --define '_srcrpmdir /tmp/' && \
                         ${finalaction}"
