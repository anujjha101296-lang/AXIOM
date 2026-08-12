from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from axiom.core.models import User, Project, Document

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)
        # Flush to get the ID without committing the transaction yet
        await self.session.flush()
        return user

    async def get(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, owner_id: str, name: str, description: Optional[str] = None) -> Project:
        project = Project(owner_id=owner_id, name=name, description=description)
        self.session.add(project)
        await self.session.flush()
        return project

    async def get(self, project_id: str) -> Optional[Project]:
        result = await self.session.execute(select(Project).where(Project.id == project_id))
        return result.scalars().first()

    async def list_for_user(self, owner_id: str) -> List[Project]:
        result = await self.session.execute(select(Project).where(Project.owner_id == owner_id))
        return list(result.scalars().all())

    async def delete(self, project_id: str) -> bool:
        project = await self.get(project_id)
        if project:
            await self.session.delete(project)
            await self.session.flush()
            return True
        return False


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project_id: str, title: str) -> Document:
        document = Document(project_id=project_id, title=title)
        self.session.add(document)
        await self.session.flush()
        return document

    async def get(self, document_id: str) -> Optional[Document]:
        result = await self.session.execute(select(Document).where(Document.id == document_id))
        return result.scalars().first()

    async def list_for_project(self, project_id: str) -> List[Document]:
        result = await self.session.execute(select(Document).where(Document.project_id == project_id))
        return list(result.scalars().all())

    async def update_status(self, document_id: str, status: str) -> Optional[Document]:
        document = await self.get(document_id)
        if document:
            document.status = status
            await self.session.flush()
        return document

    async def delete(self, document_id: str) -> bool:
        document = await self.get(document_id)
        if document:
            await self.session.delete(document)
            await self.session.flush()
            return True
        return False
