#!/usr/bin/env bash
set -eux
gitdir=$(git rev-parse --show-toplevel)
cd "${gitdir}"

VERSION=$(python3 -c 'import gnome_next_meeting_applet as f;print(f.__version__)')
RELEASE=1
NAME=gnome-next-meeting-applet
AUTHOR_EMAIL="Chmouel Boudjnah <chmouel@chmouel.com>"

[[ -e ~/.config/copr ]] || {
    echo "Cannot find ~/.config/copr"
    exit 1
}

sudo docker build -f ./rpm/Dockerfile -t gnome-next-meeting-applet-builder .

sudo docker run --rm \
           -v ~/.config/copr:/home/builder/.config/copr \
           -v "${gitdir}":/src \
           --name gnome-next-meeting-applet-builder \
           -it gnome-next-meeting-applet-builder \
           /bin/bash -c "sed 's/_VERSION_/${VERSION}/' /src/rpm/${NAME}.spec > /tmp/${NAME}.spec && \
                         sed -i -e \"/^%changelog/a\* $(date '+%a %b %-d %Y') ${AUTHOR_EMAIL} - ${VERSION}-${RELEASE}\n- New vesion ${VERSION}\n\" /tmp/${NAME}.spec && \
                         cat /tmp/${NAME}.spec && \
                         git archive --prefix=${NAME}-${VERSION}/ --format=tar ${VERSION} |gzip  >/tmp/${NAME}-${VERSION}.tar.gz
                         rpmbuild -bs /tmp/${NAME}.spec --define '_sourcedir /tmp/' --define '_srcrpmdir /tmp/' && \
                         echo copr-cli build ${NAME} /tmp/${NAME}-${VERSION}-1\$(rpm --eval '%{?dist}').src.rpm"
