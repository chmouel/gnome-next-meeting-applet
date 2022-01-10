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
TMP2=$(mktemp /tmp/.mm.XXXXXX)
clean() { rm -f ${TMP} ${TMP2}; }
trap clean EXIT

sed '/sources/,$d' release.yaml > ${TMP}
echo "sources:" >> ${TMP}

for asset in ${ASSETSFILE};do
   curl -L -s -f --fail-early ${asset} -o ${TMP2}
   sha=$(sha256sum ${TMP2}|cut -d " " -f1)
   t="file"
   [[ ${asset} == *.tar.gz ]] && t="archive"
   cat <<EOF >> ${TMP}
  - type: ${t}
    url: ${asset}
    sha256: ${sha}

EOF
done

mv ${TMP} release.yaml
