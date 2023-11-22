PACKAGE := gnome-next-meeting-applet

all: requirements

.PHONY: requirements
requirements:
	@echo "🫖 Installing requirements..."
	@env PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring \
		poetry install -q --only main

.PHONY: requirements_tools
requirements_tools:
	@echo "⛲ Installing requirements..."
	@env PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring \
		poetry install -q

.PHONY: fmt
fmt: requirements_tools
	@echo "🧹 Formatting..."
	@poetry run ruff format  */*.py

.PHONY: lint
lint: requirements_tools
	@echo "🚿 Linting..."
	@poetry run ruff check --fix gnma/

.PHONY: run
run:
	@echo "🚀 Running..."
	@unset DBUS_SESSION_BUS_ADDRESS ;\
		env poetry run $(PACKAGE) -v

.PHONY: test
test: requirements_tools
	@echo "🧪 Testing..."
	@poetry run pytest -v

