# Apply to be a Childminder Beta

A Django-based prototype for users to apply to be a childminder.

## Pre-setup

These environment variables have to be defined before running Childminder:


| Name                | Description                                                                           |
| ------------------- | ------------------------------------------------------------------------------------- |
| PROJECT_SETTINGS    | Defines which settings file to use. For each environment there's separate config file |
| APP_NOTIFY_URL      | URL for notify-gateway service                                                        |
| APP_PAYMENT_URL     | URL for payment-gateway service                                                       |
| APP_ADDRESS_GATEWAY | URL for address-gateway service                                                       |
| POSTGRES_HOST       | Database hostname                                                                     |
| POSTGRES_DB         | Database name                                                                         |
| POSTGRES_USER       | Database username                                                                     |
| POSTGRES_PASSWORD   | Database password                                                                     |
| POSTGRES_PORT       | Database port                                                                         |

## Makefile structure

We're using Makefile to speed usage of this app

| Target name   | Description                                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------------------- |
| install       | installs depedencies                                                                                             |
| run           | run application with manage.py                                                                                   |
| test          | run django tests                                                                                                 |
| migrate       | make and run migrations                                                                                          |
| static        | generate statics                                                                                                 |
| shellplus     | enter shell of manage.py                                                                                         |
| graph         | generate uml graph of django model                                                                               |
| load          | load fixtures to database                                                                                        |
| export        | export fixtures from database                                                                                    |
| flush         | clear database                                                                                                   |
| compose       | run this service in docker                                                                                       |
| compose-shell | enter container with bash shell                                                                                  |
| compose-%     | run make targets inside container, for example `make compose-run` will launch this service inside of a container |

