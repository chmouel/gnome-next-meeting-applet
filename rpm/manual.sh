#!/usr/bin/env bash
set -eux
NAME=gnome-next-meeting-applet
AUTHOR_EMAIL="Chmouel Boudjnah <chmouel@chmouel.com>"
VERSION=$(python3 -c 'import gnome_next_meeting_applet as f;print(f.__version__)')
RELEASE=1
TARGET_DIR=/${NAME}
[[ ! -d ${TARGET_DIR} ]] && TARGET_DIR=/src


finalaction="rpmbuild -ba /tmp/${NAME}.spec --define '_sourcedir /tmp/' --define '_srcrpmdir /tmp/' && mkdir -p ${TARGET_DIR}/dist/ ; cp ~/rpmbuild/RPMS/noarch/gnome-next-meeting-applet-${VERSION}-${RELEASE}$(rpm --eval '%{?dist}').noarch.rpm ${TARGET_DIR}/dist/"

/bin/bash -c "sed 's/_VERSION_/${VERSION}/' ${TARGET_DIR}/rpm/${NAME}.spec > /tmp/${NAME}.spec && \
              sed -i -e \"/^%changelog/a\* $(date '+%a %b %-d %Y') ${AUTHOR_EMAIL} - ${VERSION}-${RELEASE}\n- New vesion ${VERSION}\n\" /tmp/${NAME}.spec && \
              git archive --prefix=${NAME}-${VERSION}/ --format=tar ${VERSION} |gzip  >/tmp/${NAME}-${VERSION}.tar.gz
              rpmbuild -bs /tmp/${NAME}.spec --define '_sourcedir /tmp/' --define '_srcrpmdir /tmp/' && \
              ${finalaction}"
