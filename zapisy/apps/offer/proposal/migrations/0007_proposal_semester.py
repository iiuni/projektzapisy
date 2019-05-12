import apps.offer.proposal.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0006_proposal_semester'),
        ('courses', '0018_remove_courseinformation_semester'),
    ]

    operations = [
        migrations.RenameField(
            'proposal',
            'smtr',
            'semester',
        ),
    ]
