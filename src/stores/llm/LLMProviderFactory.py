from .LLMEnum import LLMEnum
from .providers import OpenAIProvider, CohereProvider
import logging
class LLMProviderFactory:
    def __init__(self,config:dict):
        self.config = config

    def create(self,provider:str):
        if provider == LLMEnum.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.IMPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )
        elif provider == LLMEnum.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.IMPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )

        else:
            logger = logging.getLogger(__name__)
            logger.error(f"Unsupported LLM provider: {provider}")

        
        