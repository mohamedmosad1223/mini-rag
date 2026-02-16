from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "Qdrant"
    PGVECTOR="PGVECTOR"

class DistanceMethodeEnums(Enum):
    COSINE = "Cosine"
    DOT = "Dot"

class PgvectorTableSchemaEnum(Enum):
    ID="id"
    TEXT="text"
    VECTOR="vector"
    CHUNK_ID="chunk_id"
    METADATA="metadata"
    _PREFIX="pgvector"

class PgvectorDistanceMethodeEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class PgvectorIndexTypeEnum(Enum):
    HNSW="hnsw"
    IVFFLAT="ivfflat"