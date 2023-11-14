PACKAGE := gnome-next-meeting-applet

.PHONY: requirements
requirements:
	poetry install --only main

.PHONY: requirements_tools
requirements_tools:
	poetry install

.PHONY: fmt
fmt: requirements_tools
	@poetry run black */*.py

.PHONY: lint
lint: requirements_tools
	@poetry run pylint -r y gnma/

.PHONY: run
run:
	@unset DBUS_SESSION_BUS_ADDRESS ;\
		env poetry run $(PACKAGE) -v
