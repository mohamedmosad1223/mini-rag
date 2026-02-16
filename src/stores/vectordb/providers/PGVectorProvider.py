from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import (DistanceMethodeEnums,
                             PgvectorDistanceMethodeEnums,
                             PgvectorTableSchemaEnum,
                             PgvectorIndexTypeEnum)

import logging
from typing import List
from models.db_schemes import RetrievedContent
from sqlalchemy.sql import text as sql_text

import json

class PGVectorProvider(VectorDBInterface):
    def __init__(self,db_client,default_vector_size:int=786,
                 distanse_methode:str=None,index_threshold:int =100):
        
        self.db_client=db_client
        self.default_vector_size=default_vector_size
        
        self.index_threshold=index_threshold

        if distanse_methode==DistanceMethodeEnums.COSINE.value:
            distanse_methode=PgvectorDistanceMethodeEnums.COSINE.value
        elif distanse_methode==DistanceMethodeEnums.DOT.value:
            distanse_methode=PgvectorDistanceMethodeEnums.DOT.value

        self.distanse_methode=distanse_methode
        self.pgvector_table_prefix=PgvectorTableSchemaEnum._PREFIX.value
        self.logger=logging.getLogger("uvicorn")
        self.default_index_name= lambda collection_name: f"{collection_name}_vector_idx"

    # async def get_pgvector_index_name(self,collection_name:str) -> str:
    #     return f"{collection_name}_vector_idx"

    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                ))
                await session.commit()
    async def disconnect(self):
        pass

    async def is_collection_exists(self, collection_name:str) -> bool:
        record=None
        async with self.db_client() as session:
            async with session.begin():
                list_tbl=sql_text(f"SELECT * FROM pg_tables WHERE tablename= :collection_name ")
                results=await session.execute(list_tbl,{"collection_name":collection_name})
                record=results.scalar_one_or_none()
        return record
    
    async def list_all_collections(self) -> List[str]:
        records=[]
        async with self.db_client() as session:
            async with session.begin():
                list_tbl=sql_text("SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix")
                results=await session.execute(list_tbl,{"prefix":self.pgvector_table_prefix})
                records=results.scalars().all()

        return records
    
    
    
    async def get_collection_info(self, collection_name:str) -> dict:
        async with self.db_client() as session:
            async with session.begin():
                table_info_sql=sql_text(f'''
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                    FROM pg_tables
                    WHERE tablename = :collection_name
                    ''' )
                count_sql=sql_text(f"SELECT COUNT(*) FROM {collection_name}") 

                table_info=await session.execute(table_info_sql,{"collection_name":collection_name})
                record_count_res=await session.execute(count_sql) 

                table_data=table_info.fetchone() 
                if not table_data:
                    return None
                return {
                    "Table_Data_Information":dict(table_data._mapping), 
                    "Record_Count":record_count_res.scalar() 
                }

    
    
    async def delete_collection(self, collection_name:str) -> bool:
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f"Deleting collection : {collection_name}")
                delet_sql=sql_text(f"DROP TABLE IF EXISTS {collection_name}") 
                await session.execute(delet_sql)
                session.commit()
        return True
    

    
    async def create_collection(self, 
                          collection_name: str,
                           embedding_size:int,
                           do_reset: bool = False) -> bool:
        if do_reset:
            _=await self.delete_collection(collection_name=collection_name)
        is_collection_existed=await self.is_collection_exists(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Creating new PGVector collection {collection_name}")
            async with self.db_client() as session:
                async with session.begin():
                    create_sql=sql_text(f"CREATE TABLE {collection_name} (" 
                    f"{PgvectorTableSchemaEnum.ID.value} bigserial PRIMARY KEY,"
                    f"{PgvectorTableSchemaEnum.TEXT.value} text,"
                    f"{PgvectorTableSchemaEnum.VECTOR.value} vector({embedding_size}), "
                    f"{PgvectorTableSchemaEnum.METADATA.value} jsonb DEFAULT '{{}}', "
                    f"{PgvectorTableSchemaEnum.CHUNK_ID.value} integer REFERENCES \"Chunks\"(chunk_id) ON DELETE CASCADE"
                    f")"
                    )
                    await session.execute(create_sql)
                    await session.commit()
            return True
        return False


    
    async def is_index_existed(self,collection_name:str):
        index_name=self.default_index_name(collection_name=collection_name)
        async with self.db_client() as session:
                async with session.begin():
                    check_sql=sql_text(f"""
                                       SELECT 1
                                       FROM pg_indexes
                                       WHERE tablename = :collection_name
                                       AND indexname = :index_name
                                       """)
                    results=await session.execute(check_sql,{"index_name":index_name, "collection_name":collection_name})
                    return bool(results.scalar_one_or_none())
                
    
    
    async def create_vector_index(self,collection_name:str, 
                                  index_type:str =PgvectorIndexTypeEnum.HNSW.value):
        is_index_existed=await self.is_index_existed(collection_name=collection_name)
        if is_index_existed :
            return False
        
        async with self.db_client() as session:
                async with session.begin():
                    count_sql=sql_text(f"SELECT COUNT(*) FROM {collection_name}")
                    results=await session.execute(count_sql)
                    records_counts=results.scalar_one()   
                    if records_counts < self.index_threshold:
                        False
                    self.logger.info(f"Creating Vector Index for collection {collection_name}")     
                    
                    index_name=self.default_index_name(collection_name=collection_name)
                    create_index_sql=sql_text(
                        f"CREATE INDEX {index_name} ON {collection_name} "
                        f"USING {index_type} ({PgvectorTableSchemaEnum.VECTOR.value} {self.distanse_methode})"
                    )
                    await session.execute(create_index_sql)
                    
                    self.logger.info(f"End: Created vector index for collection {collection_name}")

    
    async def reset_vector_index(self,collection_name:str, 
                                  index_type:str =PgvectorIndexTypeEnum.HNSW.value) -> bool:
        index_name=self.default_index_name(collection_name=collection_name)
        async with self.db_client() as session:
                async with session.begin():
                    drop_index=sql_text(f"DROP INDEX IF EXISTS {index_name}")
                    await session.execute(drop_index)

        return await self.create_vector_index(collection_name=collection_name,index_type=index_type,)



    async def insert_one(self,
                   collection_name: str,
                   embedding: List[float],
                   text: str,
                   vector:list,
                   metadata: dict,
                   record_id: str) -> bool:
        is_collection_existed=await self.is_collection_exists(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not insert new record no collectiona : {collection_name}")
            return False
        if not record_id:
            self.logger.error(f"Can not insert new record without chunk id : {collection_name}")
            return False            
        async with self.db_client() as session:
                async with session.begin():
                    insert_sql=sql_text(f"INSERT INTO {collection_name} "
                                        f"({PgvectorTableSchemaEnum.TEXT.value},{PgvectorTableSchemaEnum.VECTOR.value},{PgvectorTableSchemaEnum.METADATA.value},{PgvectorTableSchemaEnum.CHUNK_ID.value})"
                                        'VALUES (:text, :vector, :metadata, :chunk_id)'
                                        )
                    meta_json= json.dumps(metadata,ensure_ascii=False) if metadata is not None else "{}"

                    await session.execute(insert_sql,{
                   "text": text,
                   "vector":"[" + ",".join([ str(v) for v in vector]) + "]",
                   "metadata": meta_json,
                   "chunk_id": record_id
                    })
                    await session.commit()
                    await self.create_vector_index(collection_name=collection_name)

        return True


    async def insert_many(self,
                collection_name: str,
                texts: List,
                vectors:list,
                metadata:list = None,
                record_ids: List = None,
                batch_size: int = 50,
    ) -> List[dict]:
        is_collection_existed=await self.is_collection_exists(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not insert new record no collectiona : {collection_name}")
            return False

        if len(vectors) != len(record_ids):
            self.logger.error(f" Invalid data for {collection_name}")
            return False
        
        if not metadata or len(metadata)==0:
            metadata= [None]* len(texts)


        async with self.db_client() as session:
                async with session.begin():
                    for i in range (0,len(texts),batch_size):
                        batch_text=texts[i:i+batch_size] 
                        batch_vectors=vectors[i:i+batch_size]
                        batch_metadat=metadata[i:i+batch_size]
                        batch_record_ids=record_ids[i:i+batch_size]

                        values=[]
                        for _text, _vector, _metadata, _record_id in zip(batch_text,batch_vectors,batch_metadat,batch_record_ids):
                            meta_json= json.dumps(_metadata ,ensure_ascii=False) if _metadata is not None else "{}"
                            values.append({
                               "text": _text,
                                "vector":"[" + ",".join([ str(v) for v in _vector]) + "]",
                                "metadata": meta_json,
                                "chunk_id": _record_id 
                            })

                        batch_insert_sql=sql_text(f"INSERT INTO {collection_name} "
                                        f"({PgvectorTableSchemaEnum.TEXT.value},"
                                        f"{PgvectorTableSchemaEnum.VECTOR.value},"
                                        f"{PgvectorTableSchemaEnum.METADATA.value},"
                                        f"{PgvectorTableSchemaEnum.CHUNK_ID.value})"
                                        f'VALUES (:text, :vector, :metadata, :chunk_id)'
                                        )
                        await session.execute(batch_insert_sql,values)
        await self.create_vector_index(collection_name=collection_name)
        return True

    async def search_by_vector(self,
                          collection_name: str,
                          vector: list,
                          limit: int       
    ) -> List[RetrievedContent]:
        
        is_collection_existed = await self.is_collection_exists(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not search for record no collection: {collection_name}")
            return []

        if isinstance(vector, (float, int)):
            self.logger.warning(f"Vector received as {type(vector)}, converting to list.")
            vector = [vector]
        
        try:
            vector_str = "[" + ",".join([str(v) for v in vector]) + "]"
        except TypeError:
            self.logger.error(f"Failed to iterate over vector of type: {type(vector)}")
            return []

        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(f"""
                    SELECT {PgvectorTableSchemaEnum.TEXT.value} as text, 
                           1 - ({PgvectorTableSchemaEnum.VECTOR.value} <=> :vector) as score 
                    FROM {collection_name} 
                    ORDER BY score DESC 
                    LIMIT {limit}
                """)
                
                result = await session.execute(search_sql, {"vector": vector_str})
                records = result.fetchall()

                return [
                    RetrievedContent(
                        text=record.text,
                        score=record.score
                    )
                    for record in records
                ]

        
               

            