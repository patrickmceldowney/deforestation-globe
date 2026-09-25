import planet_client
from config import AOI_BBOX

scenes = planet_client.search_scenes(AOI_BBOX, year=2023)
item_id = scenes[0]["id"]
print(f"Ordering: {item_id}")

order_id = planet_client.place_order(item_id, AOI_BBOX)
print(f"Order placed: {order_id}")
