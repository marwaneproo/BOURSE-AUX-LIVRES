from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import Profile


class Command(BaseCommand):
    help = 'Crée le compte admin par défaut admin_emsi / #Mar2005?'

    def handle(self, *args, **options):
        username = 'admin_emsi'
        password = '#Mar2005?'
        email    = 'admin@emsi.ma'

        if User.objects.filter(username=username).exists():
            u = User.objects.get(username=username)
            u.set_password(password)
            u.is_staff      = True
            u.is_superuser  = True
            u.first_name    = 'Admin'
            u.last_name     = 'EMSI'
            u.save()
        else:
            u = User.objects.create_superuser(
                username  =username,
                email     =email,
                password  =password,
                first_name='Admin',
                last_name ='EMSI'
            )

        profile, _ = Profile.objects.get_or_create(user=u)
        profile.est_administrateur = True
        profile.est_vendeur  = True
        profile.est_acheteur = True
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f'✅ Compte admin prêt → username: {username}  |  password: {password}'
        ))
