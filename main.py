from dotenv import load_dotenv
from livekit import api
import os

load_dotenv()

user_id = input("Enter user identity: ")
user_name = input("Enter user name: ")

# will automatically use the LIVEKIT_API_KEY and LIVEKIT_API_SECRET env vars
token = api.AccessToken() \
    .with_identity(user_id) \
    .with_name(user_name) \
    .with_grants(api.VideoGrants(
        room_join=True,
        room="my-room",
    )).to_jwt()

print(token)
