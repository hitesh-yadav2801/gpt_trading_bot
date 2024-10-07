import motor.motor_asyncio
from pymongo.errors import PyMongoError

# Initialize MongoDB client and select database and collection
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/trading')
db = client['trading_bot']  # Replace with your database name
collection = db['trading_bot_users']  # Replace with your collection name

# Function to create a new document
async def create_user(telegram_id, user_signal_count=0, is_registered=False, has_deposited=False):
    user = {
        "telegram_id": telegram_id,
        "user_signal_count": user_signal_count,
        "is_registered": is_registered,
        "has_deposited": has_deposited
    }
    try:
        result = await collection.insert_one(user)
        return result.inserted_id
    except PyMongoError as e:
        print(f"An error occurred while creating the user: {e}")
        return None

# Function to get all users/documents
async def get_all_users():
    try:
        users = await collection.find({}).to_list(length=None)
        return users
    except PyMongoError as e:
        print(f"An error occurred while fetching all users: {e}")
        return []

# Function to get a user/document by telegram_id
async def get_user_by_telegram_id(telegram_id):
    try:
        user = await collection.find_one({"telegram_id": telegram_id})
        return user
    except PyMongoError as e:
        print(f"An error occurred while fetching the user: {e}")
        return None

# Function to update a user's signal count
async def update_user_signal_count(telegram_id, new_signal_count):
    try:
        result = await collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"user_signal_count": new_signal_count}}
        )
        return result.modified_count
    except PyMongoError as e:
        print(f"An error occurred while updating signal count: {e}")
        return 0

# Function to update the registration status of a user
async def update_user_registration(telegram_id, is_registered):
    try:
        result = await collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"is_registered": is_registered}}
        )
        return result.modified_count
    except PyMongoError as e:
        print(f"An error occurred while updating registration status: {e}")
        return 0

# Function to update the deposit status of a user
async def update_user_deposit_status(telegram_id, has_deposited):
    try:
        result = await collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"has_deposited": has_deposited}}
        )
        return result.modified_count
    except PyMongoError as e:
        print(f"An error occurred while updating deposit status: {e}")
        return 0

# Function to update multiple fields of a user
async def update_user(telegram_id, user_signal_count=None, is_registered=None, has_deposited=None):
    update_fields = {}
    if user_signal_count is not None:
        update_fields["user_signal_count"] = user_signal_count
    if is_registered is not None:
        update_fields["is_registered"] = is_registered
    if has_deposited is not None:
        update_fields["has_deposited"] = has_deposited

    try:
        result = await collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": update_fields}
        )
        return result.modified_count
    except PyMongoError as e:
        print(f"An error occurred while updating the user: {e}")
        return 0

# Function to delete a user by telegram_id
async def delete_user(telegram_id):
    try:
        result = await collection.delete_one({"telegram_id": telegram_id})
        return result.deleted_count
    except PyMongoError as e:
        print(f"An error occurred while deleting the user: {e}")
        return 0

# Example usage
async def main():
    user = await collection.find_one({"telegram_id": 793076295})
    print(user)
    print(type(user))
#     # Create a new user
#     telegram_id = 123456789
#     await create_user(telegram_id, user_signal_count=0, is_registered=False, has_deposited=False)

#     # Get a user by telegram_id
#     user = await get_user_by_telegram_id(telegram_id)
#     print(user)

#     # Update user's signal count
#     await update_user_signal_count(telegram_id, 5)

#     # Update user's registration status
#     await update_user_registration(telegram_id, True)

#     # Update multiple fields of a user
#     await update_user(telegram_id, user_signal_count=10, has_deposited=True)

#     # Get all users
#     all_users = await get_all_users()
#     print(all_users)

#     # Delete a user
#     await delete_user(telegram_id)

# # If running this file, execute the async main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
