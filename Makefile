BLACK ?= \033[0;30m
RED ?= \033[0;31m
GREEN ?= \033[0;32m
YELLOW ?= \033[0;33m
BLUE ?= \033[0;34m
PURPLE ?= \033[0;35m
CYAN ?= \033[0;36m
GRAY ?= \033[0;37m
WHITE ?= \033[1;37m
COFF ?= \033[0m

.PHONY: all shell build coverage-django coverage docker help migrate quality setup test-django test runserver makemigrations lint-django lint-django-fix

all: help

help:
	@echo -e "\n$(WHITE)Available commands:$(COFF)"
	@echo -e "$(CYAN)make setup$(COFF)            - Sets up the project in your local machine."
	@echo -e "                        This includes building Docker containers and running migrations."
	@echo -e "$(CYAN)make runserver$(COFF)        - Runs the django app in the container, available at http://127.0.0.1:8000"
	@echo -e "$(CYAN)make migrate$(COFF)          - Runs django's migrate command in the container"
	@echo -e "$(CYAN)make makemigrations$(COFF)   - Runs django's makemigrations command in the container"
	@echo -e "$(CYAN)make shell$(COFF)            - Starts a Linux shell (bash) in the django container"
	@echo -e "$(CYAN)make test$(COFF)             - Runs automatic tests on your python code"
	@echo -e "$(CYAN)make coverage$(COFF)         - Runs code test coverage calculation"
	@echo -e "$(CYAN)make quality$(COFF)          - Runs code quality tests on your code"


shell:
	@echo -e "$(CYAN)Starting Bash in the django container:$(COFF)"
	@docker-compose run --rm web bash

build:
	@echo -e "$(CYAN)Creating Docker images:$(COFF)"
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build

runserver:
	@echo -e "$(CYAN)Starting Docker container with the app.$(COFF)"
	@docker-compose up --remove-orphans
	@echo -e "$(CYAN)App ready and listening at http://127.0.0.1:8100.$(COFF)"

setup: build migrate
	@echo -e "$(GREEN)===================================================================="
	@echo "SETUP SUCCEEDED"
	@echo -e "Run 'make runserver' to start the Django development server and the node server.$(COFF)"

test-django:
	@echo -e "$(CYAN)Running automatic django tests:$(COFF)"
	@docker-compose run --rm web py.test

test: test-django
	@echo -e "$(GREEN)All tests passed.$(COFF)"

coverage-django:
	@echo -e "$(CYAN)Running automatic code coverage check for Python:$(COFF)"
	@docker-compose run --rm web sh -c "coverage run -m py.test && coverage html && coverage report"

coverage: coverage-django
	@echo -e "$(GREEN)Coverage reports generated:"
	@echo "- Python coverage: projement/coverage_html/"
	@echo -e "- JavaScript coverage: projement/coverage/$(COFF)"

makemigrations:
	@echo -e "$(CYAN)Running django makemigrations:$(COFF)"
	@docker-compose run --rm web ./manage.py makemigrations $(cmd)

migrate:
	@echo -e "$(CYAN)Running django migrations:$(COFF)"
	@docker-compose run --rm web ./manage.py migrate $(cmd)

lint-django:
	@echo -e "$(CYAN)Running Black check:$(COFF)"
	@docker-compose run --rm web black --check .

lint-django-fix:
	@echo -e "$(CYAN)Running Black formatting:$(COFF)"
	@docker-compose run --rm web black .

quality: lint-django
	@echo -e "$(GREEN)No code style issues detected.$(COFF)"
