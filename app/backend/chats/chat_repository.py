import uuid
import logging
from datetime import datetime, timezone, timedelta

from utils.database_chats import DatabaseClient
import azure.cosmos.exceptions as exceptions


class ChatRepository:
    def __init__(self):
        self.db_client = DatabaseClient()

    def register_chat(self, chat_data):
        # print(f'{chat_data["chatQuestion"]=}')
        # print(f'{chat_data["chatAnswer"]=}')
        current_time_utc = datetime.now(timezone.utc)
        current_time_gmt5 = current_time_utc - timedelta(hours=5)

        chat = {
            "id": str(uuid.uuid4()),
            "userId": str(uuid.uuid4()),
            # "user": chat_data["userEmail"],
            "question": chat_data["chatQuestion"],
            "answer": chat_data["chatAnswer"],
            "inputTokens": chat_data["promptTokens"],
            "outputTokens": chat_data["completionTokens"],
            "totalTokens": chat_data["totalTokens"],
            "date": current_time_gmt5.strftime("%Y-%m-%d %H:%M:%S GMT-5"),
        }

        date = {
            "id": str(uuid.uuid4()),
            "userId": str(uuid.uuid4()),
            "monthReport": f"{current_time_gmt5.year}-{current_time_gmt5.month}",
            "totalInputTokens": 0,
            "totalOutputTokens": 0,
            "interactionsCount": 0,
        }

        try:
            success_chat = self.db_client.create_chat(chat)
            if success_chat:
                success_report = self.db_client.create_report(chat, date)
                if success_report:
                    return {"success": True}
            else:
                return {"error": "Could not create chat in the database."}
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error registering chats: {e.message}")
            return {"error": "Error registering chats."}

    def get_number_interactions(self):
        current_time_gmt5 = datetime.now(timezone.utc) - timedelta(hours=5)
        month = f"{current_time_gmt5.year}-{current_time_gmt5.month}"
        return self.db_client.get_number_of_interaction_from_db(month)
