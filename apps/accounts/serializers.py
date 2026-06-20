from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source='last_name')
    prenom = serializers.CharField(source='first_name')
    est_administrateur = serializers.SerializerMethodField()
    est_banni = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'nom', 'prenom', 'email', 'est_administrateur', 'est_banni']

    def get_est_administrateur(self, obj):
        profile = getattr(obj, 'profile', None)
        return obj.is_staff or bool(profile and profile.est_administrateur)

    def get_est_banni(self, obj):
        profile = getattr(obj, 'profile', None)
        return bool(profile and profile.est_banni)


class ProfileSerializer(serializers.ModelSerializer):
    user          = UserSerializer(read_only=True)
    note_moyenne  = serializers.SerializerMethodField()
    nb_evaluations= serializers.SerializerMethodField()
    photo_url     = serializers.SerializerMethodField()

    class Meta:
        model  = Profile
        fields = [
            'id', 'user', 'photo', 'photo_url', 'telephone', 'ville',
            'est_actif', 'est_banni', 'date_inscription', 'derniere_connexion',
            'est_acheteur', 'est_vendeur', 'est_administrateur',
            'note_moyenne', 'nb_evaluations'
        ]

    def get_note_moyenne(self, obj):
        return obj.note_moyenne()

    def get_nb_evaluations(self, obj):
        return obj.nb_evaluations()

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    prenom   = serializers.CharField(source='user.first_name', required=False)
    nom      = serializers.CharField(source='user.last_name', required=False)
    email    = serializers.EmailField(source='user.email', required=False)
    username = serializers.CharField(source='user.username', required=False)

    class Meta:
        model  = Profile
        fields = ['prenom', 'nom', 'email', 'username', 'telephone', 'ville', 'photo']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if 'email' in user_data:
            new_email = user_data['email']
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                raise serializers.ValidationError({'email': 'Cet email est déjà utilisé.'})
            user.email = new_email
        if 'username' in user_data:
            new_username = user_data['username']
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                raise serializers.ValidationError({'username': "Ce nom d'utilisateur est déjà pris."})
            user.username = new_username
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RegistrationSerializer(serializers.ModelSerializer):
    nom        = serializers.CharField(write_only=True, required=True)
    prenom     = serializers.CharField(write_only=True, required=True)
    email      = serializers.EmailField(required=True)
    password   = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    est_acheteur= serializers.BooleanField(default=True, write_only=True)
    est_vendeur = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'nom', 'prenom', 'est_acheteur', 'est_vendeur']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username  =validated_data['username'],
            email     =validated_data['email'],
            password  =validated_data['password'],
            first_name=validated_data['prenom'],
            last_name =validated_data['nom']
        )
        Profile.objects.create(
            user        =user,
            est_acheteur=validated_data.get('est_acheteur', True),
            est_vendeur =validated_data.get('est_vendeur', False)
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        try:
            profile = user.profile
            # ── Vérification bannissement ──
            if profile.est_banni:
                raise serializers.ValidationError(
                    'Votre compte a été suspendu. Contactez l\'administrateur.'
                )
            data['user'] = {
                'id'               : user.id,
                'username'         : user.username,
                'email'            : user.email,
                'nom'              : user.last_name,
                'prenom'           : user.first_name,
                'est_administrateur': user.is_staff or profile.est_administrateur,
                'est_vendeur'      : profile.est_vendeur,
                'est_acheteur'     : profile.est_acheteur,
            }
        except serializers.ValidationError:
            raise
        except Profile.DoesNotExist:
            data['user'] = {
                'id'     : user.id,
                'username': user.username,
                'email'  : user.email,
                'nom'    : user.last_name,
                'prenom' : user.first_name,
            }
        return data
