.PHONY:	install format lint test sec
ISORT_ARGS=--trailing-comma --multi-line 3
PYTHONPATH=./lista_de_listas_cli

install:
	@poetry install
	@pip uninstall pylint-django -y
format:
	@poetry run blue .
	@poetry run isort . $(ISORT_ARGS)
lint:
	@poetry run blue . --check
	@poetry run isort . --check $(ISORT_ARGS)
test:
	@poetry run prospector . --with-tool pydocstyle --doc-warning
	@poetry run pytest . -v --cov --cov-report term-missing
