from enum import Enum

class LLMEnum(str, Enum):
    OPENAI="OPENAI"
    COHERE="COHERE"

class OpenAiModelsEnum(str, Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"

class CohereModelsEnum(str, Enum):
    SYSTEM="SYSTEM"
    USER="USER"
    ASSISTANT="CHATBOT"
    DOCUMENT= "search_document"
    QUERY="search_query"

class DocumentTypeEnum(str, Enum):
    DOCUMENT="document"
    QUERY="query"
    
