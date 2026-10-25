from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.sql import func
from src.core.database import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def create(self, **kwargs) -> ModelType:
        """Create a new entity."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters,
    ) -> List[ModelType]:
        """Get all entities with pagination and filters."""
        query = select(self.model)
        
        # Apply filters
        for key, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_count(self, **filters) -> int:
        """Get count of entities with filters."""
        query = select(func.count()).select_from(self.model)
        
        for key, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return result.scalar()
    
    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        """Update an entity."""
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs, updated_at=func.now())
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, id: UUID) -> bool:
        """Delete an entity."""
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
    
    async def exists(self, **filters) -> bool:
        """Check if entity exists with filters."""
        query = select(func.count()).select_from(self.model)
        
        for key, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return result.scalar() > 0