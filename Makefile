SHELL := /bin/bash

# Include Makefile settings
-include .makerc

# Detect OS
ifeq ($(OS),Windows_NT)
	WIN := 1
endif

compose:
	docker-compose up $(APP)

compose-shell:
	docker-compose run $(APP) /bin/bash

compose-%:
	docker-compose run $(APP) make $*

# run tests
test:
	python manage.py test --settings=$(PROJECT_SETTINGS)

# install depedencies (and virtualenv for linux)
install:
ifndef WIN
	-virtualenv -p python3 .venv
endif
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -r requirements.dev.txt

# run server
run:
	python manage.py runserver $(PROJECT_IP):$(PROJECT_PORT)  --settings=$(PROJECT_SETTINGS)


# handle django migrations
migrate:
	python manage.py makemigrations --settings=$(PROJECT_SETTINGS)
	python manage.py migrate --settings=$(PROJECT_SETTINGS)

# handle statics
static:
	python manage.py collectstatic --settings=$(PROJECT_SETTINGS)

shellplus:
	python manage.py shell_plus --settings=$(PROJECT_SETTINGS)

graph:
	python manage.py graph_models -a -o childminder_models.png --settings=$(PROJECT_SETTINGS)

load:
	python manage.py loaddata db.json --settings=${PROJECT_SETTINGS}

export:
	python manage.py dumpdata --indent 2 --natural-foreign --natural-primary -e sessions -e admin -e contenttypes -e auth.Permission  > db.json --settings=${PROJECT_SETTINGS}

flush:
	python manage.py sqlflush --settings=${PROJECT_SETTINGS}

rebase:
	git stash
	git checkout develop
	git pull --rebase origin develop
	if [ $$(git status --porcelain | wc -l) -lt 1 ]; then \
		git checkout -;\
		git rebase develop;\
	fi;



