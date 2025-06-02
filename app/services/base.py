from abc import ABC
from fastapi import HTTPException
from typing import Type, TypeVar, Generic
from pydantic import BaseModel, ValidationError

from app.logger_config import logger

CreateObjSchema = TypeVar('CreateObjSchema', bound=BaseModel)
ReturnObjSchema = TypeVar('ReturnObjSchema', bound=BaseModel)
UpdateObjSchema = TypeVar('UpdateObjSchema', bound=BaseModel)
QueryParams = TypeVar('QueryParams', bound=BaseModel)

class BaseService(ABC, Generic[CreateObjSchema, ReturnObjSchema, UpdateObjSchema, QueryParams]):
    crud_class: Type
    return_schema_class: Type[ReturnObjSchema]

    def __new__(cls, *args, **kwargs):
        raise TypeError(f'Cannot instantiate class {cls.__name__}')

    @classmethod
    async def _get_object_or_404(cls, obj_id: str) -> dict:
        obj = await cls.crud_class.get_by_id(obj_id)
        if not obj:
            raise HTTPException(404, f'{cls.__name__} not found')
        return obj
    
    @classmethod
    async def create(cls, data: CreateObjSchema) -> ReturnObjSchema:
        result = await cls.crud_class.create(data.model_dump())
        if not result.inserted_id:
            raise HTTPException(500, f'Failed to insert new {cls.__name__}')
        
        new_data = await cls._get_object_or_404(result.inserted_id)
        return cls.return_schema_class(**new_data)
    
    @classmethod
    async def get_by_id(cls, obj_id: str) -> ReturnObjSchema:
        obj = await cls._get_object_or_404(obj_id)
        return cls.return_schema_class(**obj)
    
    @classmethod
    async def get_by_params(cls, params: QueryParams) -> list[ReturnObjSchema]:
        query = params.model_dump(exclude=['limit', 'skip'], exclude_none=True)
        result = await cls.crud_class.get(query, params.limit, params.skip)
        objects = []
        for obj in result:
            try:
                objects.append(cls.return_schema_class(**obj))
            except ValidationError as e:
                logger.warning(f'Validation error. Skip the document with id: {obj["_id"]}', exc_info=True)
                continue
        return objects
    
    @classmethod
    async def count(cls) -> int:
        return await cls.crud_class.get_count()
    
    @classmethod
    async def update_full(cls, obj_id: str, update_data: CreateObjSchema) -> ReturnObjSchema:
        result = await cls.crud_class.update_full(obj_id, update_data.model_dump())
        if result.matched_count == 0:
            raise HTTPException(404, detail='{cls.__name__} not found')
        
        updated_object = await cls.crud_class.get_by_id(obj_id)
        if not updated_object:
            raise HTTPException(500, detail='Failed to fetch updated {cls.__name__}')
        return cls.return_schema_class(**updated_object)
    
    @classmethod
    async def update_partial(cls, obj_id: str, update_data: UpdateObjSchema) -> ReturnObjSchema:
        data = {k: v for k, v in update_data.model_dump().items() if v not in (None, [], {})}
        result = await cls.crud_class.update_partial(obj_id, data)
        if result.matched_count == 0:
            raise HTTPException(404, detail='{cls.__name__} not found')
        
        updated_object = await cls._get_object_or_404(obj_id)
        return cls.return_schema_class(**updated_object)

    @classmethod
    async def delete(cls, obj_id: str) -> None:
        result = await cls.crud_class.delete_by_id(obj_id)
        if result.deleted_count == 0:
            raise HTTPException(404, f'{cls.__name__} not found')
        