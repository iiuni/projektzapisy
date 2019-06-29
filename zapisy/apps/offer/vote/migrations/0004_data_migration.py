from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0003_auto_20190414_1147'),
    ]

    operations = [
        migrations.RunSQL('''DELETE FROM vote_singlevote v1
                    USING vote_singlevote v2
                WHERE
                    v1.student_id = v2.student_id
                    AND v1.entity_id = v2.entity_id
                    AND v1.state_id = v2.state_id
                    AND v1.id < v2.id
            ''',  # Deletes duplicate votes.
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL([
            '''UPDATE vote_singlevote
                SET proposal_id = i.id
                FROM
                    courses_courseinformation i
                WHERE vote_singlevote.entity_id = i.entity_id
            '''], reverse_sql=migrations.RunSQL.noop
        ),
    ]
