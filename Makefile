.PHONY:	install format lint test sec
ISORT_ARGS=--trailing-comma --multi-line 3
PYTHONPATH=./lista_de_listas_cli

install:
	@poetry install
	@pip uninstall pylint-django -y
format:
	@blue .
	@isort . $(ISORT_ARGS)
lint:
	@blue . --check
	@isort . --check $(ISORT_ARGS)
test:
	@prospector . --with-tool pep257 --doc-warning
	@pytest . -v --cov --cov-report term-missing
