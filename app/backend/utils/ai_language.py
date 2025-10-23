import os
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient, PiiEntityCategory
from azure.core.credentials import AzureKeyCredential


load_dotenv()
language_key = str(os.environ.get("LANGUAGE_KEY"))
language_endpoint = str(os.environ.get("LANGUAGE_ENDPOINT"))


def authenticate_client():
    ta_credential = AzureKeyCredential(language_key)
    text_analytics_client = TextAnalyticsClient(endpoint=language_endpoint, credential=ta_credential)
    return text_analytics_client


CLIENT = authenticate_client()


def pii_recognition_list(doc_list):
    response = CLIENT.recognize_pii_entities(
        doc_list, language="es", categories_filter=[PiiEntityCategory.PERSON, PiiEntityCategory.PHONE_NUMBER]
    )
    result = [doc for doc in response if not doc.is_error]
    doc_result = []
    for doc in result:
        # print("Redacted Text: {}".format(doc.redacted_text))
        doc_result.append(doc.redacted_text)

    print("AI Language succesfully executed")
    # for entity in doc.entities:
    #     print("Entity: {}".format(entity.text))
    #     print("\tCategory: {}".format(entity.category))

    return doc_result


# document_list = [
#     "Hola, mi nombre es Juan Perez, mi DNI es 46801357 y tengo una consulta sobre...",
#     "Encantado de ayudarte Juan en tu trámite sobre...",
# ]
# document_result = pii_recognition_list(document_list)
# print(f"{document_result=}")
