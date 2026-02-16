from .providers import QdrantDBProvider
from .providers.QdrantDBProvider import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums
import logging
from controllers.BaseController import BaseController
from sqlalchemy.orm import sessionmaker
from .providers import PGVectorProvider,QdrantDBProvider
class VectorDBProviderFactory:
    def __init__(self,config,db_client :sessionmaker=None):
        self.config = config
        self.base_controller = BaseController()
        self.db_client=db_client

    def create(self,provider:str):
        if provider == VectorDBEnums.QDRANT.value:
            qdrant_db_client=self.base_controller.get_database_path(db_name=self.config.VECTORE_DB_PATH)
            return QdrantDBProvider(
                db_client=qdrant_db_client,
                distance_methode=self.config.VECTORE_DB_DISTANCE_METHODE,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTORE_DB_PGVEC_INDEX_THREASHOLD
                )
        if provider == VectorDBEnums.PGVECTOR.value:
            return PGVectorProvider(
                db_client=self.db_client,
                distanse_methode=self.config.VECTORE_DB_DISTANCE_METHODE,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTORE_DB_PGVEC_INDEX_THREASHOLD

            )
        return None