ID = com.chmouel.gnomeNextMeetingApplet
CMD = flatpak-builder --user --force-clean build
RELEASEY = $(ID).yaml
EMAIL := `git config --get user.email`
NAME := `git config --get user.name`

# different ID screws everything
DEVY = $(ID)-dev.yaml

GITHUB_PASS_TOKEN = github/chmouel-token

.PHONY: build
build-release:
	$(CMD) $(RELEASEY)

.PHONY: clean
clean:
	rm -rf .flatpak-builder/

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

.PHONY: run-release
run-release: install-release
	flatpak run $(ID) -v

.PHONY: release
release:
	./update-release.sh
	target_release=`poetry version|cut -d" " -f2` ; \
	./upload-file-to-github.py --branch-ref refs/heads/master -o flathub/$(ID) \
		--email "$(EMAIL)" --name "$(NAME)" \
		--token "`pass show $(GITHUB_PASS_TOKEN)`" --message "Release $$target_release" \
		--destination release.yaml --filename release.yaml && \
		git commit -m "Release flatpak release.yaml $$target_release" release.yaml && \
		env NOTESTS=ci git push origin main
