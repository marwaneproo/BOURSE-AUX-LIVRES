from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Profile : ajouter photo, telephone, ville, est_banni
        migrations.AddField(
            model_name='profile',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='profiles/'),
        ),
        migrations.AddField(
            model_name='profile',
            name='telephone',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='profile',
            name='ville',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='est_banni',
            field=models.BooleanField(default=False),
        ),
        # Notification : ajouter lien, commande + nouveaux types
        migrations.AddField(
            model_name='notification',
            name='lien',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='notification',
            name='commande',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='notifications',
                to='marketplace.commande'
            ),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type_notification',
            field=models.CharField(
                choices=[
                    ('MESSAGE', 'Message'),
                    ('COMMANDE', 'Commande'),
                    ('COMMANDE_ACCEPTEE', 'Commande acceptée'),
                    ('COMMANDE_REFUSEE', 'Commande refusée'),
                    ('FAVORI_DEVENU_DISPONIBLE', 'Favori devenu disponible'),
                    ('ALERTE_SYSTEME', 'Alerte système'),
                    ('ADMIN_MESSAGE', 'Message admin'),
                ],
                max_length=30
            ),
        ),
        # Commande : ajouter statut REFUSEE
        migrations.AlterField(
            model_name='commande',
            name='statut',
            field=models.CharField(
                choices=[
                    ('EN_ATTENTE', 'En attente'),
                    ('CONFIRMEE', 'Confirmée'),
                    ('REFUSEE', 'Refusée'),
                    ('EN_COURS_DE_LIVRAISON', 'En cours de livraison'),
                    ('LIVREE', 'Livrée'),
                    ('ANNULEE', 'Annulée'),
                ],
                default='EN_ATTENTE', max_length=30
            ),
        ),
        # Evaluation : ajouter commande FK + unique_together
        migrations.AddField(
            model_name='evaluation',
            name='commande',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='evaluations',
                to='marketplace.commande'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='evaluation',
            unique_together={('evaluateur', 'commande')},
        ),
        # Signalement : ajouter traite_par
        migrations.AddField(
            model_name='signalement',
            name='traite_par',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='signalements_traites',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
