import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            destinataire_id = data.get('destinataire_id')
            contenu = data.get('contenu')

            if not destinataire_id or not contenu:
                await self.send(text_data=json.dumps({"error": "destinataire_id et contenu requis."}))
                return

            msg = await self.save_message(self.user, destinataire_id, contenu)
            if msg is None:
                await self.send(text_data=json.dumps({"error": "Destinataire introuvable."}))
                return

            await self.channel_layer.group_send(
                f"user_{destinataire_id}",
                {
                    "type": "chat_message",
                    "message": {
                        "id": msg.id,
                        "expediteur_id": self.user.id,
                        "expediteur_username": self.user.username,
                        "contenu": msg.contenu,
                        "date_envoi": str(msg.date_envoi)
                    }
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Format JSON invalide."}))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": str(e)}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def save_message(self, sender, receiver_id, content):
        try:
            receiver = User.objects.get(id=receiver_id)
            return Message.objects.create(expediteur=sender, destinataire=receiver, contenu=content)
        except User.DoesNotExist:
            return None
