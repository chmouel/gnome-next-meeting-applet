ID = com.chmouel.gnomeNextMeetingApplet
CMD = flatpak-builder --user --force-clean build
RELEASEY = $(ID).yaml

DEVID = $(ID)-dev
DEVY = $(DEVID).yaml

.PHONY: build
build-release:
	$(CMD) $(RELEASEY)

.PHONY: generate-dev
generate-dev: $(RELEASEY)
	@sed -e 's/^app-id:.*/app-id: $(DEVID)/' $(RELEASEY) -e \
		's/- release.yaml/- dev.yaml/' >  $(DEVY)

.PHONY: build-dev
build-dev: generate-dev
	$(CMD) $(DEVY)

.PHONY: install-dev
install-dev:
	$(CMD) --install $(DEVY)

.PHONY: run-dev
run-dev: install-dev
	flatpak run $(DEVID) -v

.PHONY: install-release
install-release:
	$(CMD) --install $(RELEASEY)

.PHONY: run
run-release: install
	flatpak run $(ID) -v

update-release:
	sed '/sources/,/^$$/d' release.yaml > /tmp/.release.temp.yaml
	./update-release.sh >> /tmp/.release.temp.yaml
	sed -i -e :a -e '/^\n*$$/{$$d;N;ba' -e '}' /tmp/.release.temp.yaml
	mv /tmp/.release.temp.yaml release.yaml
