from .providers import QdrantDBProvider
from .providers.QdrantDBProvider import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums
import logging
from controllers.BaseController import BaseController
class VectorDBProviderFactory:
    def __init__(self,config):
        self.config = config
        self.base_controller = BaseController()

    def create(self,provider:str):
        if provider == VectorDBEnums.QDRANT.value:
            db_path=self.base_controller.get_database_path(db_name=self.config.VECTORE_DB_PATH)
            return QdrantDBProvider(
                db_path=db_path,
                distance_methode=self.config.VECTORE_DB_DISTANCE_METHODE
                )
        return None