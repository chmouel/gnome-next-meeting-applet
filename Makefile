PACKAGE := gnome-next-meeting-applet

.PHONY: requirements
requirements:
	poetry install --no-dev

.PHONY: requirements_tools
requirements_tools:
	poetry install

.PHONY: fmt
fmt: requirements_tools
	@poetry run yapf -i */*.py

.PHONY: lint
lint: requirements_tools
	@poetry run pylint -r y gnma/

.PHONY: run
run: requirements
	@poetry run $(PACKAGE)
