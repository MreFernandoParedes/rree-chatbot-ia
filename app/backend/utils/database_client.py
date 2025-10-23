# from azure.cosmos import CosmosClient
# import azure.cosmos.exceptions as exceptions
# from azure.cosmos.partition_key import PartitionKey
from config import CONFIG_COSMOS_DB_URL, CONFIG_COSMOS_DB_KEY, CONFIG_DATABASE_USERS, CONFIG_CONTAINER_USERS

# class DatabaseClient:
# def __init__(self):
#     self.client = CosmosClient(CONFIG_COSMOS_DB_URL, {"masterKey": CONFIG_COSMOS_DB_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
#     self.database = self.client.get_database_client(CONFIG_DATABASE_USERS)
#     self.container = self.database.get_container_client(CONFIG_CONTAINER_USERS)
#     try:
#         db = self.client.create_database(id=CONFIG_DATABASE_USERS)
#         print("Database with id \'{0}\' created".format(CONFIG_DATABASE_USERS))

#     except exceptions.CosmosResourceExistsError:
#         db = self.client.get_database_client(CONFIG_DATABASE_USERS)
#         print("Database with id \'{0}\' was found".format(CONFIG_DATABASE_USERS))

#     try:
#         container = db.create_container(id=CONFIG_CONTAINER_USERS, partition_key=PartitionKey(path='/userId'))
#         print("Container with id \'{0}\' created".format(CONFIG_CONTAINER_USERS))

#     except exceptions.CosmosResourceExistsError:
#         container = db.get_container_client(CONFIG_CONTAINER_USERS)
#         print("Container with id \'{0}\' was found".format(CONFIG_CONTAINER_USERS))


# def check_existing_user(self, email):
#     query = f"SELECT * FROM c WHERE c.Email = '{email}'"
#     find_duplicated_emails = list(self.container.query_items(
#         query=query,
#         enable_cross_partition_query=True
#     ))
#     duplicated_emails = [item["Email"] for item in find_duplicated_emails]
#     print(f"duplicated emails: {duplicated_emails}")
#     return len(find_duplicated_emails) > 0


# def create_user(self, user_data):
#     print(f"start DatabaseClient user_data: {user_data}")
#     try:
#         print("Inserting User")
#         self.container.create_item(body=user_data)
#         print(f"User {user_data['Email']} added correctly")
#         return True
#     except exceptions.CosmosHttpResponseError as e:
#         print(f"User {user_data['Email']} not added. Error: {e.message}")
#         return False

# def create_chat(self, chat_data):
#     try:
#         print("Inserting User")
#         self.container.create_item(body=chat_data)
#         print(f"User {chat_data['Email']} added correctly")
#         return True
#     except exceptions.CosmosHttpResponseError as e:
#         print(f"User {chat_data['Email']} not added. Error: {e.message}")
#         return False
