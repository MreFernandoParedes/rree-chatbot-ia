import uuid

# from utils.database_client import DatabaseClient
# from utils.security import hash_password
# import azure.cosmos.exceptions as exceptions

# class UserRepository:
#     def __init__(self):
#         self.db_client = DatabaseClient()

#     def check_existing_user(self, email):
#         return self.db_client.check_existing_user(email)

#     def register_user(self, user_data):
#         if self.check_existing_user(user_data["Email"]):
#             return {"error": f"User with email '{user_data['Email']}' already exists."}

#         user = {
#             "id": str(uuid.uuid4()),
#             "userId": str(uuid.uuid4()),
#             "Email": user_data["Email"],
#             "Name": user_data["Name"],
#             "LastName": user_data["LastName"],
#             "Company": user_data["Company"],
#             "PasswordHash": hash_password(user_data["Password"])
#         }

#         success = self.db_client.create_user(user)
#         if success:
#             return {"success": True}
#         else:
#             return {"error": "Could not create user in the database."}

#     def get_user_by_email(self, email):
#         query = f"SELECT * FROM c WHERE c.Email = '{email}'"
#         try:
#             result = list(self.db_client.container.query_items(
#                 query=query,
#                 enable_cross_partition_query=True
#             ))
#             return result[0] if result else None
#         except exceptions.CosmosHttpResponseError as e:
#             print(f"Error retrieving user by email: {e.message}")
#             return None
