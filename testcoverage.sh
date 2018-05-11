#!/usr/bin/env bash
rm -r htmlcov
coverage erase
coverage run --omit=.env/*,*/migrations/*,*/__init__.py,*/models.py,manage.py,/home/vagrant/example-venv/* --branch /vagrant/OFS-MORE-DevOps-Tooling/app-childminder/manage.py test --settings=childminder.settings.dev --exclude-tag=selenium --no-input
coverage report -m --omit=.env/*,*/migrations/*,*/__init__.py,*/tests.py,*/models.py,manage.py,/home/vagrant/example-venv/*
coverage html -d
firefox htmlcov/index.html
