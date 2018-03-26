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


Once these dependencies have been gathered, you can run the prototype itself by issuing the command `python manage.py runserver`. After running this command, the prototype will be made available (using the default Django port) on http://127.0.0.1:8000.