from enum import Enum

class LLMEnum(str, Enum):
    OPENAI="OPENAI"
    COHERE="COHERE"

class OpenAiModelsEnum(str, Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"
