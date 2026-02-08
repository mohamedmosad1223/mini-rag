from ..LLMInterface import LLMInterface
import logging
from sentence_transformers import SentenceTransformer


class MmBertEmbedProvider(LLMInterface):
    def __init__(
        self,
        api_key: str = None,              
        api_url: str = None,              
        default_input_max_characters: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
        default_max_seq_length: int = 2048,     
        cache_folder: str = None               
    ):
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.default_max_seq_length = default_max_seq_length
        self.cache_folder = cache_folder

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = None 
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = int(embedding_size) if embedding_size is not None else None

        try:
            self.client = SentenceTransformer(
                model_id,
                device="cpu",                 
                cache_folder=self.cache_folder
            )
            
            self.client.max_seq_length = self.default_max_seq_length
        except Exception as e:
            self.logger.error(f"Failed to load model '{model_id}': {e}")
            self.client = None

    def process_text(self, text: str):
        return text[: self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list = None, max_output_tokens: int = None, temperature: float = None):
        self.logger.error("MmBertEmbedProvider does not support text generation (embedding-only model).")
        return None

    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("Embedding model is not initialized. Call set_embedding_model first.")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None
        if not isinstance(text, str) or not text.strip():
            self.logger.error("Empty text provided for embedding.")
            return None

        processed = self.process_text(text)

       
        if document_type == "query":
            processed = f"query: {processed}"
        else:
            processed = f"passage: {processed}"


        try:
            emb = self.client.encode(processed)  

            if self.embedding_size and 0 < self.embedding_size < len(emb):
                emb = emb[: self.embedding_size]


            norm = (sum((x * x) for x in emb) ** 0.5)
            if norm > 0:
                emb = [float(x / norm) for x in emb]
            else:
                emb = [float(x) for x in emb]

            return emb
        except Exception as e:
            self.logger.error(f"Embedding failed: {e}")
            return None

    def construct_prompt(self, prompt: str, role: str):
        return [
            {
                "role": role,
                "text": self.process_text(prompt)
            }
        ]
