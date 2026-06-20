from django.conf import settings
from django.db import models
from django.db.models import Avg


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True, default='')
    ville = models.CharField(max_length=100, blank=True, default='')
    est_actif = models.BooleanField(default=True)
    est_banni = models.BooleanField(default=False)
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(auto_now=True)
    est_acheteur = models.BooleanField(default=True)
    est_vendeur = models.BooleanField(default=False)
    est_administrateur = models.BooleanField(default=False)

    class Meta:
        db_table = 'marketplace_profile'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ({self.user.username})'

    def note_moyenne(self):
        result = self.user.evaluations_recues.aggregate(avg=Avg('note'))
        return round(result['avg'] or 0, 1)

    def nb_evaluations(self):
        return self.user.evaluations_recues.count()
