from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from models.enums.ProcessingEnum import ProcessingEnum
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from dataclasses import dataclass

@dataclass
class Document:
    page_content:str
    metadata:dict
    
class ProcessController(BaseController):
    def __init__(self, project_id: str):
        
        super().__init__()

        self.project_id=project_id

        self.project_path=ProjectController().get_project_path(project_id)


    def get_file_extention(self, file_id: str):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self, file_id: str):
        file_extention=self.get_file_extention(file_id)
        file_path= os.path.join(
            self.project_path,
            file_id
        )
        if not os.path.exists(file_path):
            return None

        if file_extention==ProcessingEnum.PDF.value :
            return PyMuPDFLoader(file_path)
            
        elif file_extention==ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding='utf-8')
        else:
            return None
        
    def get_file_content(self, file_id: str):
        loader=self.get_file_loader(file_id)
        if loader is not None:
            return loader.load() # give me list of documents {page_content, metadata}
        else:
            return None
        
    def process_file_content(self, file_id:str,file_content :list,chunk_size: int=100,overlap_size:int=20):
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                   chunk_overlap=overlap_size,
                                                   length_function=len
                                                  )

        file_content_text=[
            rec.page_content
            for rec in file_content

        ]
        file_content_metadata=[
            rec.metadata
            for rec in file_content
        ]

        # chunk= splitter.create_documents(
        #     file_content_text,
        #     metadatas=file_content_metadata
        # )
        chunk= self.process_simpler_spliter(texts=file_content_text,
                                            metadata=file_content_metadata,
                                           chunk_size= chunk_size
                                           )

        return chunk
    def process_simpler_spliter(self,texts:List[str],
                                metadata:List[dict],chunk_size:int,splitter_tag:str ="\n"):
        full_text= " ".join(texts)

        #split by splitter
        lines=[ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) >1 ]

        chunks=[]
        current_chunk="" 
        for line in lines:
            current_chunk +=line +splitter_tag

            if len(current_chunk) >=chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))
                current_chunk=""
        if len(current_chunk) >=0:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))

        return chunks