#!/usr/bin/env bash
set -euf
VERSION=${1:-""}
POETRY_NAME_VERSION="$(poetry version)"
PKGNAME=${POETRY_NAME_VERSION% *}
CURRENT_VERSION=${POETRY_NAME_VERSION#* }
APP_DATA_FILE=data/desktop/com.chmouel.gnomeNextMeetingApplet.appdata.xml

TMP=$(mktemp /tmp/.mm.XXXXXX.yaml)
clean() { rm -f ${TMP}; }
trap clean EXIT

docker ps -q >/dev/null || exit 1

editChanges() {
   if [[ ${TERM} == *kitty ]];then
       kitty @ launch --keep-focus --cwd=current --tab-title "Git log ${CURRENT_VERSION}..HEAD" bash -c "git log --oneline ${CURRENT_VERSION}..HEAD;read -p 'Press Key...'" >/dev/null
   else
      echo "log between current version ${CURRENT_VERSION} and HEAD"
      read -t1 -p"Press Key to continue"
   fi
   if yq ".Version==\"${VERSION}\"" NEWS.yaml|grep -qw true;then
      echo "We already have a VERSION in ${VERSION}"
      rm -f ${TMP}
   else
       echo -e "---\nVersion: ${VERSION}\nDate: $(date +%Y-%m-%d)\nDescription:\n  - \n" > ${TMP}
   fi
   cat NEWS.yaml >> ${TMP}
   $EDITOR +5 $TMP
   while true;do
         read -p "continue releasing? [yN]: " ANSWER
         [[ ${ANSWER,} == y ]] && break
   done
   mv -v ${TMP} NEWS.yaml
   appstreamcli news-to-metainfo NEWS.yaml ${APP_DATA_FILE}
   yq -r "select(.Version==\"${VERSION}\") | .Description" NEWS.yaml > ${TMP}
}

bumpversion() {
   major=$(python3 -c "import semver,sys;print(str(semver.VersionInfo.parse(sys.argv[1]).bump_major()))" ${CURRENT_VERSION})
   minor=$(python3 -c "import semver,sys;print(str(semver.VersionInfo.parse(sys.argv[1]).bump_minor()))" ${CURRENT_VERSION})
   patch=$(python3 -c "import semver,sys;print(str(semver.VersionInfo.parse(sys.argv[1]).bump_patch()))" ${CURRENT_VERSION})

   echo "If we bump we get, Major: ${major} Minor: ${minor} Patch: ${patch}"
   read -p "To which version you would like to bump [M]ajor, Mi[n]or, [P]atch or Manua[l]: " ANSWER
   if [[ ${ANSWER,,} == "m" ]];then
       mode="major"
   elif [[ ${ANSWER,,} == "n" ]];then
       mode="minor"
   elif [[ ${ANSWER,,} == "p" ]];then
       mode="patch"
   elif [[ ${ANSWER,,} == "l" ]];then
       read -p "Enter version: " -e VERSION
       return
   else
       print "no or bad reply??"
       exit
   fi
   VERSION=$(python3 -c "import semver,sys;print(str(semver.VersionInfo.parse(sys.argv[1]).bump_${mode}()))" ${CURRENT_VERSION})
   [[ -z ${VERSION} ]] && {
       echo "could not bump version automatically"
       exit
   }
   echo "Releasing ${VERSION}"
}

[[ $(git rev-parse --abbrev-ref HEAD) != main ]] && {
    echo "you need to be on the main branch"
    exit 1
}
[[ -z ${VERSION} ]] && bumpversion
# editChanges
# vfile=pyproject.toml
# sed -i "s/^version = .*/version = \"${VERSION}\"/" ${vfile}
# git commit -S -m "Release ${VERSION} 🥳" ${vfile} NEWS.yaml ${APP_DATA_FILE}  || true
# git tag -s ${VERSION} -m "Releasing version ${VERSION}"
# git push --tags origin ${VERSION}
# env NOTESTS=ci git push origin main
# rm -rf build
# poetry build
# pname=${PKGNAME//-/_}
# gh release create -F ${TMP} ${VERSION} ./dist/${pname}-${VERSION}.tar.gz ./dist/${pname}-${VERSION}-py3-none-any.whl

./packaging/debian/build.sh
./packaging/aur/build.sh
./packaging/rpm/build.sh
make -C ./packaging/flatpak release
