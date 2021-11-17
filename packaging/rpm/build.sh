#!/usr/bin/env bash
set -eux
NAME=gnome-next-meeting-applet
AUTHOR_EMAIL="Chmouel Boudjnah <chmouel@chmouel.com>"
VERSION=$(python3 -c 'import gnome_next_meeting_applet as f;print(f.__version__)')
RELEASE=1
finalaction="copr-cli build ${NAME} /tmp/${NAME}-${VERSION}-1\$(rpm --eval '%{?dist}').src.rpm"

gitdir=$(git rev-parse --show-toplevel)
cd "${gitdir}"
justbuildrpm=""
image_name=gnome-next-meeting-applet-rpm-builder

while getopts "r" o; do
    case "${o}" in
        r)
            finalaction="rpmbuild -ba /tmp/${NAME}.spec --define '_sourcedir /tmp/' --define '_srcrpmdir /tmp/'"
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

sudo docker build -f ./packaging/rpm/Dockerfile -t ${image_name} .

sudo docker run --rm \
           -v ~/.config/copr:/home/builder/.config/copr \
           -v "${gitdir}":/src \
           --name gnome-next-meeting-applet-builder \
           -it ${image_name} \
           /bin/bash -c "sed 's/_VERSION_/${VERSION}/' /src/packaging/rpm/${NAME}.spec > /tmp/${NAME}.spec && \
                         sed -i -e \"/^%changelog/a\* $(date '+%a %b %-d %Y') ${AUTHOR_EMAIL} - ${VERSION}-${RELEASE}\n- New vesion ${VERSION}\n\" /tmp/${NAME}.spec && \
                         git archive --prefix=${NAME}-${VERSION}/ --format=tar ${VERSION} |gzip  >/tmp/${NAME}-${VERSION}.tar.gz
                         rpmbuild -bs /tmp/${NAME}.spec --define '_sourcedir /tmp/' --define '_srcrpmdir /tmp/' && \
                         ${finalaction}"
