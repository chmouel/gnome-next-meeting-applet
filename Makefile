
fmt:
	@poetry run yapf -i */*.py

lint:
	@poetry run pylint -r y gnma/
