"""Este módulo define una clase base para los repositorios, que proporciona métodos genéricos para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) en la base de datos."""

from typing import Any, Sequence, Type
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel

# 1. Definimos los "comodines" (Generics)
type ModelType[T: SQLModel] = T
type CreateSchemaType[T: BaseModel] = T # pylint: disable=invalid-name
type UpdateSchemaType[T: BaseModel] = T # pylint: disable=invalid-name

class BaseRepository[M: SQLModel, C: BaseModel, U: BaseModel]:
    def __init__(self, model: Type[M], session: AsyncSession):
        """
        Al inicializar, le decimos qué modelo de BD va a usar y le pasamos la sesión.
        Args:
        - model: El modelo de SQLModel que representa la tabla de la base de datos.
        - session: La sesión de base de datos para ejecutar las operaciones.
        """
        self.model = model
        self.session = session

    async def get(self, obj_id: int) -> M | None:
        """Busca un registro por su ID."""
        query = select(self.model).where(getattr(self.model, "id") == obj_id)
        result = await self.session.exec(query)
        return result.first()

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[M]:
        """Obtiene todos los registros de la tabla."""
        sort_field = getattr(self.model, "created_at", getattr(self.model, "id", None))
        query = select(self.model)

        if sort_field is not None:
            query = query.order_by(sort_field.desc())
        query = query.offset(skip).limit(limit)
        result = await self.session.exec(query)
        return result.all()

    async def create(self, obj_in: C) -> M:
        """Crea un registro automáticamente a partir del esquema Pydantic."""
        db_obj = self.model(**obj_in.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: M, obj_in: U | dict[str, Any]) -> M:
        """Actualiza un registro existente."""
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, obj_id: int) -> M | None:
        """Elimina un registro."""
        db_obj = await self.get(obj_id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.commit()
        return db_obj
