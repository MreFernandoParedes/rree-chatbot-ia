"""
Configuration values for the backend.

Sensitive values such as database keys should **never** be hard‑coded here.
Instead, we read them from environment variables to prevent secrets from being
checked into version control. If required variables are not set in the
environment, empty strings will be used as fallbacks.
"""

import os

###############################################################################
# Constants identifying configuration keys for use throughout the application.
# These values are not secrets; they name the configuration entries used when
# populating the Quart/Flask app context.
###############################################################################

CONFIG_OPENAI_TOKEN = "openai_token"
CONFIG_CREDENTIAL = "azure_credential"
CONFIG_ASK_APPROACH = "ask_approach"
CONFIG_ASK_VISION_APPROACH = "ask_vision_approach"
CONFIG_CHAT_VISION_APPROACH = "chat_vision_approach"
CONFIG_CHAT_APPROACH = "chat_approach"
CONFIG_BLOB_CONTAINER_CLIENT = "blob_container_client"
CONFIG_USER_UPLOAD_ENABLED = "user_upload_enabled"
CONFIG_USER_BLOB_CONTAINER_CLIENT = "user_blob_container_client"
CONFIG_AUTH_CLIENT = "auth_client"
CONFIG_GPT4V_DEPLOYED = "gpt4v_deployed"
CONFIG_SEMANTIC_RANKER_DEPLOYED = "semantic_ranker_deployed"
CONFIG_VECTOR_SEARCH_ENABLED = "vector_search_enabled"
CONFIG_SEARCH_CLIENT = "search_client"
CONFIG_OPENAI_CLIENT = "openai_client"
CONFIG_INGESTER = "ingester"
CONFIG_LANGUAGE_PICKER_ENABLED = "language_picker_enabled"
CONFIG_SPEECH_INPUT_ENABLED = "speech_input_enabled"
CONFIG_SPEECH_OUTPUT_BROWSER_ENABLED = "speech_output_browser_enabled"
CONFIG_SPEECH_OUTPUT_AZURE_ENABLED = "speech_output_azure_enabled"
CONFIG_SPEECH_SERVICE_ID = "speech_service_id"
CONFIG_SPEECH_SERVICE_LOCATION = "speech_service_location"
CONFIG_SPEECH_SERVICE_TOKEN = "speech_service_token"
CONFIG_SPEECH_SERVICE_VOICE = "speech_service_voice"
CONFIG_CHAT_HISTORY_BROWSER_ENABLED = "chat_history_browser_enabled"

###############################################################################
# Secrets and URLs pulled from the environment.
#
# These environment variables must be defined by whatever deploys or runs the
# application. For local development you can set them in a `.env` file (which
# is ignored by git) or export them in your shell before running the backend.
###############################################################################

CONFIG_COSMOS_DB_URL = os.getenv("COSMOS_DB_URL", "")
CONFIG_COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY", "")

###############################################################################
# Names of databases and containers used in Cosmos DB.
###############################################################################

CONFIG_DATABASE_CHATS = "ChatDB"
CONFIG_CONTAINER_CHATS = "ChatCollection"
CONFIG_CONTAINER_REPORTS = "ReportsCollection"
