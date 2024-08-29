# notifications.py

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_order_status_change(order):
    channel_layer = get_channel_layer()
    # Send a message to the WebSocket channel group for the specific order
    async_to_sync(channel_layer.group_send)(
        f'order_{order.custom_order_id}',  # Use custom_order_id
        {
            'type': 'order_status_update',
            'order_id': order.custom_order_id,  # Use custom_order_id
            'status': order.progress_status,
        }
    )
