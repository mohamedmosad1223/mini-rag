from .LLMEnum import LLMEnum
from .providers import CoHereProvider,OpenAiProvider,MmBertEmbedProvider


import logging
class LLMProviderFactory:
    def __init__(self,config:dict):
        self.config = config

    def create(self,provider:str):
        if provider == LLMEnum.OPENAI.value:
            return OpenAiProvider(
                api_key=self.config.OPENAI_API_KEY,
                base_url=self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )
        elif provider == LLMEnum.COHERE.value:
            return CoHereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )

        elif provider == LLMEnum.MMBERT.value:
            # embedding-only provider
            return MmBertEmbedProvider(
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
                default_max_seq_length=getattr(self.config, "EMBEDDING_MAX_SEQ_LENGTH", 2048),
                cache_folder=getattr(self.config, "HF_CACHE_FOLDER", None),
            )
        else:
            logger = logging.getLogger(__name__)
            logger.error(f"Unsupported LLM provider: {provider}")

        
        