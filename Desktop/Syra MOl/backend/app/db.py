from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]

# Collections
users_col = db["users"]
patients_col = db["patients"]
reminders_col = db["reminders"]
moods_col = db["moods"]
locations_col = db["locations"]
alerts_collection = db["alerts"]
comfort_collection = db["comfort_messages"]
family_images_collection = db["family_images"]
family_messages_collection = db["family_messages"]
logs_collection = db["daily_logs"]
devices_collection = db["devices"]
vitals_collection = db["vitals"]
