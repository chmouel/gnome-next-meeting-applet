#!/usr/bin/env  bash
# Chmouel Boudjnah <chmouel@chmouel.com>
set -euf

RELEASE=${1:-""}

ASSETSFILE=$(gh release view ${RELEASE} -q .assets[].url --json assets)

[[ -z ${ASSETSFILE} ]] && {
    echo "cannot find asseetsfile"
    exit 1
}

TMP=$(mktemp /tmp/.mm.XXXXXX)
clean() { rm -f ${TMP}; }
trap clean EXIT

echo sources: 

for asset in ${ASSETSFILE};do
   curl -L -s -f --fail-early ${asset} -o ${TMP}
   sha=$(sha256sum ${TMP}|cut -d " " -f1)
   t=file
   [[ ${asset} == *.tar.gz ]] && t=archive
   cat <<EOF
  - type: ${t}
    url: ${asset}
    sha256: ${sha}

EOF
done
