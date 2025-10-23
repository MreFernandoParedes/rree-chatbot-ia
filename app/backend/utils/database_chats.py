import logging
import uuid
from azure.cosmos import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

from config import (
    CONFIG_COSMOS_DB_URL,
    CONFIG_COSMOS_DB_KEY,
    CONFIG_DATABASE_CHATS,
    CONFIG_CONTAINER_CHATS,
    CONFIG_CONTAINER_REPORTS,
)


class DatabaseClient:
    def __init__(self):
        self.client = CosmosClient(
            CONFIG_COSMOS_DB_URL,
            {"masterKey": CONFIG_COSMOS_DB_KEY},
            user_agent="CosmosDBPythonQuickstart",
            user_agent_overwrite=True,
        )
        self.database = self.client.get_database_client(CONFIG_DATABASE_CHATS)
        self.container_chat = self.database.get_container_client(CONFIG_CONTAINER_CHATS)
        self.container_report = self.database.get_container_client(CONFIG_CONTAINER_REPORTS)

        try:
            db = self.client.create_database(id=CONFIG_DATABASE_CHATS)
            print("Database with id '{0}' created".format(CONFIG_DATABASE_CHATS))

        except exceptions.CosmosResourceExistsError:
            db = self.client.get_database_client(CONFIG_DATABASE_CHATS)
            # print("Database with id '{0}' was found".format(CONFIG_DATABASE_CHATS))

        try:
            container_chat = db.create_container(id=CONFIG_CONTAINER_CHATS, partition_key=PartitionKey(path="/userId"))
            print("Container with id '{0}' created".format(CONFIG_CONTAINER_CHATS))

        except exceptions.CosmosResourceExistsError:
            container_chat = db.get_container_client(CONFIG_CONTAINER_CHATS)
            # print("Container with id '{0}' was found".format(CONFIG_CONTAINER_CHATS))

        try:
            container_report = db.create_container(
                id=CONFIG_CONTAINER_REPORTS, partition_key=PartitionKey(path="/userId")
            )
            print("Container with id '{0}' created".format(CONFIG_CONTAINER_REPORTS))

        except exceptions.CosmosResourceExistsError:
            container_report = db.get_container_client(CONFIG_CONTAINER_REPORTS)
            # print("Container with id '{0}' was found".format(CONFIG_CONTAINER_REPORTS))

    def create_chat(self, chat_data):
        try:
            self.container_chat.create_item(body=chat_data)
            print(f"Chat added correctly.")
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"Chat not added. Error: {e.message}")
            return False

    def create_report(self, chat_data, chat_date_data):
        try:
            # print(f"{chat_date_data=}")
            report = self.get_report_by_month(chat_date_data["monthReport"])
            # print(f"{report=}")
            if report:
                self.overwrite_report(chat_data, report)
                print(f"Chat report updated.")
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"Chat not reported. Error: {e.message}")
            return False

    def get_number_of_interaction_from_db(self, month):
        query = f"SELECT * FROM c WHERE c.monthReport = '{month}'"

        try:
            results_query = list(self.container_report.query_items(query=query, enable_cross_partition_query=True))
            if len(results_query) == 0:
                return 0
            elif len(results_query) > 0:
                return results_query[0]["interactionsCount"]

        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"error: {e}")

    def get_report_by_month(self, month):
        # print(f"{month=}")
        query = f"SELECT * FROM c WHERE c.monthReport = '{month}'"

        try:
            results_query = list(self.container_report.query_items(query=query, enable_cross_partition_query=True))
            # print(f"{results_query=}")
            if len(results_query) == 0:
                result = {
                    "id": str(uuid.uuid4()),
                    "userId": str(uuid.uuid4()),
                    "monthReport": month,
                    "totalInputTokens": 0,
                    "totalOutputTokens": 0,
                    "interactionsCount": 0,
                }
                self.container_report.create_item(body=result)
                print(f"Chat report created correctly.")
            else:
                result = results_query[0]

            report_data = {
                "id": result["id"],
                "userId": result["userId"],
                "monthReport": result["monthReport"],
                "totalInputTokens": result["totalInputTokens"],
                "totalOutputTokens": result["totalOutputTokens"],
                "interactionsCount": result["interactionsCount"],
            }

            # print(f"{report_data=}")

            return report_data

        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"error: {e}")

    def overwrite_report(self, chat_data, chat_date_data):
        try:
            read_item = self.container_report.read_item(
                item=chat_date_data["id"], partition_key=chat_date_data["userId"]
            )
            read_item["totalInputTokens"] = read_item["totalInputTokens"] + chat_data["inputTokens"]
            read_item["totalOutputTokens"] = read_item["totalOutputTokens"] + chat_data["outputTokens"]
            read_item["interactionsCount"] = read_item["interactionsCount"] + 1

            self.container_report.upsert_item(body=read_item)
            logging.info(f"Report updated successfully.")
            return True

        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"Error upserting the report: {e}")
            return False
