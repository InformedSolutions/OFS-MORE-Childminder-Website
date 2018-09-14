from __future__ import unicode_literals

from django.db import migrations

update_sql = """
            UPDATE public."APPLICATION" SET 
            your_children_status = 'NOT_STARTED' 
            WHERE your_children_status = null;
            """

reverse_update_sql = """
            UPDATE public."APPLICATION" SET 
            your_children_status = null 
            WHERE your_children_status = 'NOT_STARTED';
            """

class Migration(migrations.Migration):

    dependencies = [
        ('application', '0037_auto_20180911_1130')
    ]

    operations = [
        migrations.RunSQL(sql=update_sql,
                          reverse_sql=reverse_update_sql)
    ]
