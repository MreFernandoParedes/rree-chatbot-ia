import os
from quart import jsonify
from .chat_repository import ChatRepository
from utils.ai_language import pii_recognition_list

# from .chat_schema import validate_chat_data
# from users.user_repository import UserRepository


async def register_chat(chat_data):
    try:
        # validation_errors = validate_chat_data(chat_data)
        # if validation_errors:
        #     return jsonify({"errors": validation_errors}), 400
        # print(f"{chat_data=}")
        try:
            chat_data["chatQuestion"] = pii_recognition_list([chat_data.get("chatQuestion")])
            chat_data["chatAnswer"] = pii_recognition_list([chat_data.get("chatAnswer")])
        except Exception as e:
            print(f"Error generado en AI Language: {e}")
        # print(f"{chat_data=}")
        # user_repo = UserRepository()
        chat_repo = ChatRepository()
        chat_repo.register_chat(chat_data)
        return jsonify({"message": "Chat registered correctly."}), 201

        # search_user = user_repo.get_user_by_email(user_email)
        # if search_user:
        #     user_id = search_user.get("userId")
        #     chat_data["userId"] = user_id
        #     chat_result = chat_repo.register_chat(chat_data)

        #     if chat_result.get("success", False):
        #         return jsonify({"message": "Chat registered correctly."}), 201
        #     else:
        #         return jsonify({"error": f"Chat not registered."}), 409
        # else:
        #     return jsonify({"error": f"There is not user_id with email: {user_email}"}), 409
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


async def is_limit_reached():
    # print("Numero de interacciones cargando")
    try:
        monthly_limit_chat = os.environ["MONTHLY_CHAT_LIMIT"]
        if int(monthly_limit_chat) == 0:
            return jsonify({"available": True, "message": "Available chat."}), 201
        chat_repo = ChatRepository()
        interactions = chat_repo.get_number_interactions()
        if int(interactions) > int(monthly_limit_chat):
            return jsonify({"available": False, "message": "Resource limit reached."}), 201
        else:
            return jsonify({"available": True, "message": "Available chat."}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
