import os
from typing import Any, Coroutine, List, Literal, Optional, Union, overload

from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorQuery
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)
from openai_messages_token_helper import build_messages, get_token_limit

from approaches.approach import ThoughtStep
from approaches.chatapproach import ChatApproach
from core.authentication import AuthenticationHelper


class ChatReadRetrieveReadApproach(ChatApproach):
    """
    A multi-step approach that first uses OpenAI to turn the user's question into a search query,
    then uses Azure AI Search to retrieve relevant documents, and then sends the conversation history,
    original user question, and search results to OpenAI to generate a response.
    """

    def __init__(
        self,
        *,
        search_client: SearchClient,
        auth_helper: AuthenticationHelper,
        openai_client: AsyncOpenAI,
        chatgpt_model: str,
        chatgpt_deployment: Optional[str],  # Not needed for non-Azure OpenAI
        embedding_deployment: Optional[str],  # Not needed for non-Azure OpenAI or for retrieval_mode="text"
        embedding_model: str,
        embedding_dimensions: int,
        sourcepage_field: str,
        content_field: str,
        query_language: str,
        query_speller: str,
    ):
        self.search_client = search_client
        self.openai_client = openai_client
        self.auth_helper = auth_helper
        self.chatgpt_model = chatgpt_model
        self.chatgpt_deployment = chatgpt_deployment
        self.embedding_deployment = embedding_deployment
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        self.query_language = query_language
        self.query_speller = query_speller
        self.chatgpt_token_limit = get_token_limit(chatgpt_model, default_to_minimum=self.ALLOW_NON_GPT_MODELS)

    @property
    def system_message_chat_conversation(self):
        return """
Eres un asistente virtual diseñado para proporcionar información y orientación únicamente sobre:
1. Trámites consulares y asistencia humanitaria y legal, incluyendo apoyo en casos de repatriación de restos, asistencia económica y orientación en situaciones de emergencia.
2. Información general de los servicios consulares, como circunscripción consular, direcciones de oficinas, teléfonos, correos electrónicos y páginas web de las Oficinas Consulares del Perú en el exterior (Consulados y Secciones Consulares).
3. Asistencia en casos específicos, brindando información detallada y pasos a seguir para obtener ayuda humanitaria y legal, así como orientación sobre los recursos disponibles para peruanos en el extranjero y sus familiares en el Perú.
4. Asistencia en la apostilla de documentos y otros trámites relacionados.

EN CASO TE PREGUNTEN POR TEMAS NO RELACIONADOS CON LOS PUNTOS ANTERIORES, PARAFRASEA EN EL MISMO IDIOMA DEL USUARIO ESTE MENSAJE, PERO PERSONALIZALO SEGUN LA CONSULTA DEL USUARIO:
"Lo siento, sólo puedo responder sobre consultas relativas a servicios consulares brindados en las Oficinas Consulares del Perú."

INSTRUCCIONES ADICIONALES:
- Tus respuestas brindadas deben ser fáciles de entender, con un tono amigable, profesional, cálido y cercano, incluyendo contactos y procedimientos necesarios.
- No inventes enlaces a páginas web externas, sólo utiliza la información de los documentos provistos.
- En el caso se solicite realizar seguimiento a un trámite de SUNARP, se debe indicar que el usuario se diriga a la página web: https://sigueloplus.sunarp.gob.pe/siguelo/
- Sólo muestra los costos en las monedas indicadas en los documentos (soles consulares), si te solicitan cambiar a otra moneda, indica que tu función es sólo mostrar las cantidades en los documentos sin convertirlos a otras monedas.
- En caso se desee realizar un trámite consultar, recomendar que el usuario acuda a la oficina consular más cercana.
- En caso se solicite apoyo para un connacional que se encuentra en un país distinto, no es necesario indicar la dirección del consulado en el otro país, sólo es necesario indicar el procedimiento a seguir por los otros medios de ese consulado, como correo o telefono.
- Sólo si te saludan, debes contestar:
  "¡Bienvenido!
  Soy el asistente virtual del Ministerio de Relaciones Exteriores, estoy aquí para responder tus preguntas sobre los servicios consulares brindados a través de las Oficinas Consulares del Perú.
  ¿En qué consulta consular puedo ayudarte?".
- RESPUESTA CUANDO EL ASISTENTE VIRTUAL REQUIERE DE UN FUNCIONARIO CONSULAR que debes responder en el mismo idioma que te preguntan:
  "Es una consulta muy específica, lo siento, no está dentro de mis capacidades poder brindar respuesta.
  Te sugiero enviar un correo electrónico o llamar al Consulado o Sección Consular más cercano a su ubicación,
  para lo cual le brindo el portal para ubicar el consulado correspondiente (http://www.consulado.pe/paginas/Inicio.aspx),
  a fin de que un funcionario consular pueda ayudarlo con su consulta.
  Asimismo, puede consultar los teléfonos o dirección de la Oficina Consular más cercana a usted."
- Tus respuestas deben ser en párrafos cortos y claros, sigue una estructura de la información efectiva (usando la técnica de la pirámide invertida).
- Es muy importante que tu respuesta la escribas en el MISMO IDIOMA que preguntó el usuario al inicio.
- Sólo responde con las fuentes proporcionadas sin mencionar el nombre de la fuente.
"""

    @overload
    async def run_until_final_call(
        self,
        messages: list[ChatCompletionMessageParam],
        overrides: dict[str, Any],
        auth_claims: dict[str, Any],
        should_stream: Literal[False],
    ) -> tuple[dict[str, Any], Coroutine[Any, Any, ChatCompletion]]: ...

    @overload
    async def run_until_final_call(
        self,
        messages: list[ChatCompletionMessageParam],
        overrides: dict[str, Any],
        auth_claims: dict[str, Any],
        should_stream: Literal[True],
    ) -> tuple[dict[str, Any], Coroutine[Any, Any, AsyncStream[ChatCompletionChunk]]]: ...

    async def run_until_final_call(
        self,
        messages: list[ChatCompletionMessageParam],
        overrides: dict[str, Any],
        auth_claims: dict[str, Any],
        should_stream: bool = False,
    ) -> tuple[dict[str, Any], Coroutine[Any, Any, Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]]]:
        seed = overrides.get("seed", None)
        use_text_search = overrides.get("retrieval_mode") in ["text", "hybrid", None]
        use_vector_search = overrides.get("retrieval_mode") in ["vectors", "hybrid", None]
        use_semantic_ranker = True if overrides.get("semantic_ranker") else False
        use_semantic_captions = True if overrides.get("semantic_captions") else False
        # CONFIGURACIÓN: Colocar el número de documentos relevantes de AI Search en una variable.
        RETRIEVE_DOCUMENTS = os.environ["RETRIEVE_DOCUMENTS"]
        top = overrides.get("top", RETRIEVE_DOCUMENTS)
        minimum_search_score = overrides.get("minimum_search_score", 0.0)
        minimum_reranker_score = overrides.get("minimum_reranker_score", 0.0)
        filter = self.build_filter(overrides, auth_claims)

        original_user_query = messages[-1]["content"]
        if not isinstance(original_user_query, str):
            raise ValueError("The most recent message content must be a string.")
        user_query_request = "Generate search query for: " + original_user_query

        tools: List[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": "search_sources",
                    "description": "Retrieve sources from the Azure AI Search index",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "Query string to retrieve documents from azure search eg: 'Health care plan'",
                            }
                        },
                        "required": ["search_query"],
                    },
                },
            }
        ]

        # STEP 1: Generate an optimized keyword search query based on the chat history and the last question
        query_response_token_limit = 100
        query_messages = build_messages(
            model=self.chatgpt_model,
            system_prompt=self.query_prompt_template,
            tools=tools,
            few_shots=self.query_prompt_few_shots,
            past_messages=messages[:-1],
            new_user_content=user_query_request,
            max_tokens=self.chatgpt_token_limit - query_response_token_limit,
            fallback_to_default=self.ALLOW_NON_GPT_MODELS,
        )

        chat_completion: ChatCompletion = await self.openai_client.chat.completions.create(
            messages=query_messages,  # type: ignore
            # Azure OpenAI takes the deployment name as the model name
            model=self.chatgpt_deployment if self.chatgpt_deployment else self.chatgpt_model,
            temperature=0.01,  # Minimize creativity for search query generation
            max_tokens=query_response_token_limit,  # Setting too low risks malformed JSON, setting too high may affect performance
            n=1,
            tools=tools,
            seed=seed,
        )

        query_text = self.get_search_query(chat_completion, original_user_query)

        # STEP 2: Retrieve relevant documents from the search index with the GPT optimized query

        # If retrieval mode includes vectors, compute an embedding for the query
        vectors: list[VectorQuery] = []
        if use_vector_search:
            vectors.append(await self.compute_text_embedding(query_text))

        results = await self.search(
            top,
            query_text,
            filter,
            vectors,
            use_text_search,
            use_vector_search,
            use_semantic_ranker,
            use_semantic_captions,
            minimum_search_score,
            minimum_reranker_score,
        )

        sources_content = self.get_sources_content(results, use_semantic_captions, use_image_citation=False)
        content = "\n".join(sources_content)

        # STEP 3: Generate a contextual and content specific answer using the search results and chat history

        # Allow client to replace the entire prompt, or to inject into the exiting prompt using >>>
        system_message = self.get_system_prompt(
            overrides.get("prompt_template"),
            self.follow_up_questions_prompt_content if overrides.get("suggest_followup_questions") else "",
        )

        response_token_limit = 1024
        messages = build_messages(
            model=self.chatgpt_model,
            system_prompt=system_message,
            past_messages=messages[:-1],
            # Model does not handle lengthy system messages well. Moving sources to latest user conversation to solve follow up questions prompt.
            new_user_content=original_user_query + "\n\nSources:\n" + content,
            max_tokens=self.chatgpt_token_limit - response_token_limit,
            fallback_to_default=self.ALLOW_NON_GPT_MODELS,
        )

        data_points = {"text": sources_content}

        extra_info = {
            "data_points": data_points,
            "thoughts": [
                ThoughtStep(
                    "Prompt to generate search query",
                    query_messages,
                    (
                        {"model": self.chatgpt_model, "deployment": self.chatgpt_deployment}
                        if self.chatgpt_deployment
                        else {"model": self.chatgpt_model}
                    ),
                ),
                ThoughtStep(
                    "Search using generated search query",
                    query_text,
                    {
                        "use_semantic_captions": use_semantic_captions,
                        "use_semantic_ranker": use_semantic_ranker,
                        "top": top,
                        "filter": filter,
                        "use_vector_search": use_vector_search,
                        "use_text_search": use_text_search,
                    },
                ),
                ThoughtStep(
                    "Search results",
                    [result.serialize_for_results() for result in results],
                ),
                ThoughtStep(
                    "Prompt to generate answer",
                    messages,
                    (
                        {"model": self.chatgpt_model, "deployment": self.chatgpt_deployment}
                        if self.chatgpt_deployment
                        else {"model": self.chatgpt_model}
                    ),
                ),
            ],
        }

        chat_coroutine = self.openai_client.chat.completions.create(
            # Azure OpenAI takes the deployment name as the model name
            model=self.chatgpt_deployment if self.chatgpt_deployment else self.chatgpt_model,
            messages=messages,
            temperature=overrides.get("temperature", 0.01),
            max_tokens=response_token_limit,
            n=1,
            stream=True,
            stream_options={"include_usage": True},
            seed=seed,
        )
        return (extra_info, chat_coroutine)
