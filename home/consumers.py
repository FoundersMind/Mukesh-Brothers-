import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .sender import send_order_status_update

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.custom_order_id = self.scope['url_route']['kwargs']['custom_order_id']
        self.room_group_name = f'order_{self.custom_order_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        status = text_data_json['status']

        # Send message to room group
        await send_order_status_update(self.channel_layer, self.room_group_name, status)

    async def order_status_update(self, event):
        status = event['status']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'status': status
        }))
