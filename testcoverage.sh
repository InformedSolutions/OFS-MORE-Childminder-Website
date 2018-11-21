#!/usr/bin/env bash
# Script to test unit test coverage for app-childminder and produce html document from report
. ./dev-env-vars.txt
rm -r htmlcov 2> /dev/null
coverage erase
coverage run --omit=.env/*,*/migrations/*,*/__init__.py,*/models.py,manage.py,/home/vagrant/example-venv/* --branch /vagrant/OFS-MORE-DevOps-Tooling/app-childminder/manage.py test --settings=childminder.settings.dev --exclude-tag=selenium --no-input
coverage report -m --omit=.env/*,*/migrations/*,*/__init__.py,*/models.py,manage.py,/home/vagrant/example-venv/*
coverage html --omit=.env/*,*/migrations/*,*/__init__.py,*/models.py,manage.py,/home/vagrant/example-venv/* -d htmlcov
firefox htmlcov/index.html
