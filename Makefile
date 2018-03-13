# Include Makefile settings
-include .makerc

# Detect OS
ifeq ($(OS),Windows_NT)
	WIN := 1
endif

# run server
run:
	python manage.py runserver $(PROJECT_IP):$(PROJECT_PORT)  --settings=$(PROJECT_SETTINGS)

# run tests
test:
	python manage.py test --settings=$(PROJECT_SETTINGS)

# install depedencies (and virtualenv for linux)
install:
ifndef WIN
	-virtualenv -p python3 .venv
endif
	pip install -r requirements.txt

# handle django migrations
migrate:
	python manage.py makemigrations --settings=$(PROJECT_SETTINGS)
	python manage.py migrate --settings=$(PROJECT_SETTINGS)

# handle statics
static:
	python manage.py collectstatic --settings=$(PROJECT_SETTINGS)

shell:
	python manage.py shell_plus --settings=$(PROJECT_SETTINGS)

graph:
	python manage.py graph_models -a -o childminder_models.png --settings=$(PROJECT_SETTINGS)

load:
	python manage.py loaddata db.json --settings=${PROJECT_SETTINGS}
