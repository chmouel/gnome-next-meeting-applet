ID = com.chmouel.gnomeNextMeetingApplet
CMD = flatpak-builder --user --force-clean build $(ID).yaml

.PHONY: build
build:
	$(CMD)

.PHONY: install
install:
	$(CMD) --install

.PHONY: run
run:
	flatpak run $(ID) -v

