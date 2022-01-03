ID = com.chmouel.gnomeNextMeetingApplet
CMD = flatpak-builder --user --force-clean build
RELEASEY = $(ID).yaml

# different ID screws everything
DEVY = $(ID)-dev.yaml

GITHUB_PASS_TOKEN = github/chmouel-token

.PHONY: build
build-release:
	$(CMD) $(RELEASEY)

.PHONY: generate-dev
generate-dev: $(RELEASEY)
	@sed 's/- release.yaml/- dev.yaml/' >  $(DEVY)

.PHONY: build-dev
build-dev: generate-dev
	$(CMD) $(DEVY)

.PHONY: install-dev
install-dev:
	$(CMD) --install $(DEVY)

.PHONY: run-dev
run-dev: install-dev
	flatpak run $(ID) -v

.PHONY: install-release
install-release:
	$(CMD) --install $(RELEASEY)

.PHONY: run
run-release: install
	flatpak run $(ID) -v

update-release-yaml:
	sed '/sources/,$$d' release.yaml > /tmp/.release.temp.yaml
	./update-release.sh >> /tmp/.release.temp.yaml
	sed -i -e :a -e '/^\n*$$/{$$d;N;ba' -e '}' /tmp/.release.temp.yaml
	mv /tmp/.release.temp.yaml release.yaml

upload-to-flathub: update-release-yaml
	target_release=`poetry version|cut -d" " -f2` ; \
	./upload-file-to-github.py --branch-ref refs/heads/master flathub/$(ID) \
		--token "`pass show $(GITHUB_PASS_TOKEN)`" --message "Release $$target_release" \
		--destination release.yaml --filename release.yaml

