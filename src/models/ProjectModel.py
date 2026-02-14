from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy.future import select
from sqlalchemy import func


class ProjectModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)

        # self.collection=self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value] in monogo
        self.db_client=db_client
        # inint must be async but thats cant do so we do static fn call   init_collection
    @classmethod
    async def create_instance(cls, db_client):
        instance=cls(db_client)
        # await instance.init_collection()
        return instance
    ###########in mongo #############
# when it init create indexes
    # async def init_collection(self):
    #     all_collectiona=await self.db_client.list_collection_names()
    #     if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collectiona:
    #         await self.db_client.create_collection(DataBaseEnum.COLLECTION_PROJECT_NAME.value)

    #         indexes= Project.get_indexes()
    #         for index in indexes:
    #             await self.collection.create_index(
    #                 index["key"],
    #                 name=index["name"],
    #                 unique=index["unique"]
    #             )
                
    async def create_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        return project

    #     result = await self.collection.insert_one(project.dict(by_alias=True,exclude_unset=True))
    #     project.project_id = result.inserted_id
    #     return project
    
    async def get_project_or_create_one(self, project_id: str):
        async with self.db_client() as session:
            async with session.begin():
                query=select(Project).where(Project.project_id==project_id)
                result=await session.execute(query)
                project=result.scalar_one_or_none()
                
                if project is None:
                    project_rec=Project(
                        project_id=project_id
                    )

                    project=await self.create_project(project=project_rec)
                    return project
                else:
                    return project
                

            
    #     record= await self.collection.find_one(
    #         {"project_id": project_id})
    #     if record is None:
    #         project=Project(project_id=project_id)
    #         project= await self.create_project(project)
    #         return project
    #     return Project(**record) # to convert dict to pydantic model
    
    async def get_all_projects(self,page:int=1,page_size:int=10):
        async with self.db_client() as session:
            async with session.begin():
                total_documents=await session.execute(select(
                    func.count(Project.project_id)
                ))
                total_documents=total_documents.scalar_one()
                total_page= total_documents //page_size
                if total_documents % page_size >0:
                   total_page +=1

                query=select(Project).offset((page-1)*page_size).limit(page_size)
                projects=await session.execute(query).scalars().all()
                return projects,total_page


        # total_documents= await self.collection.count_documents({})

        # total_page= total_documents //page_size
        # if total_documents % page_size >0:
        #     total_page +=1

        # cursor=self.collection.find().skip((page-1)*page_size).limit(page_size) #return cursor
        # projects=[]
        # async for document in cursor:
        #     projects.append(Project(**document))

        # return projects, total_page
        
