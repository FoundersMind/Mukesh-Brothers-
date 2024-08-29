async def send_order_status_update(channel_layer, room_group_name, status):
    await channel_layer.group_send(
        room_group_name,
        {
            'type': 'order_status_update',
            'status': status
        }
    )
