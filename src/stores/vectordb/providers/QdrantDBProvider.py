from qdrant_client import QdrantClient, models
from ..VectorDBInterface import VectorDBInterface
import logging
from ..VectorDBEnums import VectorDBEnums, DistanceMethodeEnums
from typing import List
from models.db_schemes import RetrievedContent

class QdrantDBProvider(VectorDBInterface):
    def __init__(self,
                 db_client:str,
                 distance_methode:str,
                 default_vector_size:int=786,
                 index_threshold:int =100,
    ):
        self.default_vector_size=default_vector_size

        self.client=None
        self.db_client=db_client
        self.distance_methode=None
        if distance_methode==DistanceMethodeEnums.COSINE.value:
            self.distance_methode=models.Distance.COSINE

        elif distance_methode==DistanceMethodeEnums.DOT.value:
            self.distance_methode=models.Distance.DOT

        self.logger = logging.getLogger('uvicorn')
    async def connect(self):
        self.client = QdrantClient(path=self.db_client)
        self.logger.info("Connected to QdrantDB at %s", self.db_client)

    async def disconnect(self):
        self.client=None
        self.logger.info("Disconnected from QdrantDB")

    async def is_collection_exists(self, collection_name:str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    async def list_all_collections(self) -> List[str]:
        return self.client.get_collections()
    
    async def get_collection_info(self, collection_name:str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    async def delete_collection(self, collection_name:str) -> bool:
        if self.is_collection_exists(collection_name):
            self.logger.info(f"Dleating collection {collection_name}")
            return self.client.delete_collection(collection_name=collection_name)
        
    async def create_collection(self, 
                          collection_name: str,
                           embedding_size:int,
                           do_reset: bool = False) -> bool:

        if do_reset :
            _=self.delete_collection(collection_name)

        if not self.is_collection_exists(collection_name):
            self.logger.info(f"Creating new Qdrant collection {collection_name}")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_methode
                )
            )
            return True
        return False
    
    async def insert_one(self,
                   collection_name: str,
                   embedding: List[float],
                   text: str,
                   vector:list,
                   metadata: dict,
                   record_id: str) -> bool:
        
        if not self.is_collection_exists(collection_name):
            self.logger.error("Collection %s does not exist.", collection_name)
            return False
        try:
            _=self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=[record_id],
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error("Error uploading record to QdrantDB: %s", e)
            return False
        return True
    
    async def insert_many(self,
                collection_name: str,
                texts: List,
                vectors:list,
                metadata:list = None,
                record_ids: List = None,
                batch_size: int = 50,
    ) -> List[dict]:
        
        if metadata is None:
            metadata=[None]*len(texts)
        if record_ids is None:
            record_ids=list(range(0,len(texts)))
        for i in range(0, len(texts), batch_size):
            batch_end=i + batch_size

            batch_texts = texts[i: batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_id=record_ids[i:batch_end]

            batch_records=[
                models.Record(
                    id=batch_record_id[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x]
                    }
                )
                
                for x in range(len(batch_texts))
            ]
            try:
                self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except Exception as e:
                self.logger.error("Error uploading batch to QdrantDB: %s", e)
                return False
        return True


        
        
    async def search_by_vector(self,
                         collection_name: str,
                         vector:list,
                         limit:int =5      
    ) -> List[dict]:
        results= self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )
        if not results or len(results)==0:
            return None
        return [
        RetrievedContent(**{
            "score": result.score,
            "text": (result.payload or {}).get("text", "")
        })
        for result in results
    ]

        

       

      