import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from devices.models import WaterPump
from .mqtt_handler import mqtt_handler

User = get_user_model()


class WebSocketConsumer1(AsyncWebsocketConsumer):
    # @login_required
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))

    # async def send_mqtt_update(self, event):
    #     print('Receiver---------------')
    #     message = event["message"]

    #     # Send the MQTT update to the WebSocket
    #     await self.send(text_data=json.dumps({"message": message}))

# You'll need to trigger the `send_mqtt_update` method from your MQTT handler
# when new MQTT messages are received.


# class TankOwnerConsumer(WebsocketConsumer):
#     def connect(self):
#         self.owner_topic = self.scope["url_route"]["kwargs"]["owner_topic"]
#         self.owner_topic_group_name = f"account_{self.owner_topic}"

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.owner_topic_group_name, self.channel_name
#         )

#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.owner_topic_group_name, self.channel_name
#         )

#     # Receive message from WebSocket
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Send message to account group
#         async_to_sync(self.channel_layer.group_send)(
#             self.owner_topic_group_name, {
#                 "type": "account.message", "message": message}
#         )

#     # Receive message from account group
#     def account_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": message}))


class TankOwnerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.owner_topic = self.scope["url_route"]["kwargs"]["owner_topic"]
            self.owner_topic_group_name = f"account_{self.owner_topic}"

            # Join room group
            await self.channel_layer.group_add(self.owner_topic_group_name, self.channel_name)

            await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the group when they disconnect
        # Leave account group
        await self.channel_layer.group_discard(self.owner_topic_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Do internal some processes, do not send to channel group
        if message.get('action') == 'TooglePump':
            pump_topic = message.get('pumpTopic')
            topic_parts = pump_topic.split('/')
            pump_obj = await self.pump_by_topic(topic_parts[-2])
            if pump_obj is not None:
                current_status = message.get('currentStatus')
                new_status = 'On' if current_status == 'Off' else 'Off'
                new_topic = f'{pump_topic}Manual'
                mqtt_handler.publish_to_mqtt_topic(new_topic, new_status)

        else:
            # Send message to account group
            await self.channel_layer.group_send(
                self.owner_topic_group_name, {
                    "type": "account.message", "message": message}
            )

    # Receive message from account group
    async def account_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    # Custom methods to deal with some updates
    @database_sync_to_async
    def pump_by_topic(self, pump_topic):
        return WaterPump.objects.filter(mqtt_topic=pump_topic).first()
