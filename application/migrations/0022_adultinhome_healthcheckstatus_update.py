from __future__ import unicode_literals

from django.db import migrations

update_sql = """
            UPDATE public."ADULT_IN_HOME" SET 
            health_check_status = 'Started' 
            WHERE health_check_status = 'Flagged';
            """

reverse_update_sql = """
            UPDATE public."ADULT_IN_HOME" SET 
            health_check_status = 'Flagged' 
            WHERE health_check_status = 'Started';
            """

class Migration(migrations.Migration):

    dependencies = [
        ('application', '0021_auto_20180727_1400')
    ]

    operations = [
        migrations.RunSQL(sql=update_sql,
                          reverse_sql=reverse_update_sql)
    ]
