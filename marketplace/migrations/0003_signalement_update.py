from django.db import migrations, models


def migrate_statut_signalement(apps, schema_editor):
    """Migre les anciennes valeurs textuelles vers les nouvelles clés enum."""
    Signalement = apps.get_model('marketplace', 'Signalement')
    Signalement.objects.filter(statut='En attente').update(statut='PENDING')
    Signalement.objects.filter(statut='Traité').update(statut='ACCEPTED')


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_update_marketplace'),
    ]

    operations = [
        migrations.AddField(
            model_name='signalement',
            name='message_admin',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='signalement',
            name='date_traitement',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # D'abord migrer les données existantes, PUIS changer le champ
        migrations.RunPython(migrate_statut_signalement, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='signalement',
            name='statut',
            field=models.CharField(
                choices=[
                    ('PENDING',  'En attente'),
                    ('ACCEPTED', 'Accepté'),
                    ('REJECTED', 'Rejeté'),
                ],
                default='PENDING',
                max_length=30,
            ),
        ),
    ]
