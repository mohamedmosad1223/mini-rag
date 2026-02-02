from abc import ABC, abstractmethod
from typing import List
class VectorDBInterface(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass
  
    @abstractmethod
    def is_collection_exists(self, collection_name:str) -> bool:
        pass
   
    @abstractmethod
    def list_all_collections(self) -> List[str]:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name:str) -> dict:
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name:str) -> bool:
        pass

    @abstractmethod
    def create_collection(self, 
                          collection_name: str,
                           embedding_size:int,
                           do_reset: bool = False) -> bool:
        pass

    @abstractmethod
    def insert_one(self,
                   collection_name: str,
                   embedding: List[float],
                   text: str,
                   vector:list,
                   metadata: dict,
                   record_id: str) -> bool:
        pass

    @abstractmethod
    def insert_many(self,
                collection_name: str,
                texts: List,
                vectors:list,
                metadata:list = None,
                record_ids: List = None,
                batch_size: int = 50,
    ) -> List[dict]:
        pass

    @abstractmethod
    def search_by_vector(self,
                         collection_name: str,
                         vector:list,
                         limit:int       
    ) -> List[dict]:
        pass