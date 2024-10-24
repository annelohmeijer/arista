from datetime import datetime
from typing import Generic, TypeVar

from sqlalchemy import and_, delete, func, select
from sqlmodel import Session, SQLModel

from arista.db.session import get_session
from arista.exceptions import ItemNotFoundException

Model = TypeVar("Model", bound=SQLModel)


class BaseRepository(Generic[Model]):
    """Generic repository template metaclass for all repositories that
    interact with a table in the database. Supports all classic CRUD
    operations as well as custom queries."""

    _model: type[Model]
    timestamp_col: str
    STRFTIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        """Initialize the repository with a database session."""
        self._session: Session = get_session()

    def create(self, obj: Model) -> Model:
        """Create an object in the table."""
        new_obj = self._model.model_validate(obj)
        self._session.add(new_obj)
        self._session.commit()
        self._session.refresh(new_obj)
        return new_obj

    def bulk_create(self, objs: list[Model]):
        """Create multiple objects in the table."""
        self._session.bulk_insert_mappings(self._model, objs)
        self._session.commit()

    def delete(self, object_id: int) -> None:
        """Delete an object from the table."""
        obj = self._session.get(self._model, object_id)
        if not obj:
            raise ItemNotFoundException()
        self._session.delete(obj)
        self._session.commit()

    def delete_where(self, attr: str, value: str) -> None:
        """Delete all objects by an attribute matching a value."""
        statement = delete(self._model).where(getattr(self._model, attr) == value)
        self._session.exec(statement)
        self._session.commit()

    def read(self, object_id: int) -> Model | None:
        """Read an object from the table."""
        obj = self._session.get(self._model, object_id)
        if not obj:
            raise ItemNotFoundException()
        return obj

    def max_timestamp(
        self, col: str = None, filters: list[tuple[str, str]] = None
    ) -> datetime | None:
        """Get the object with the maximum timestamp."""
        timestamp_col = col or self.timestamp_col
        max_t = self.max(timestamp_col, filters)
        return datetime.utcfromtimestamp(max_t) if max_t else None

    def max(self, col: str, filters: list[tuple[str, str]]) -> float | None:
        """Get the max value of a column,
        optionally with a where clause."""
        expr = and_(*self._construct_filter(filters))
        stmt = select(func.max(getattr(self._model, col))).where(and_(expr))
        max_t = self._session.exec(stmt).scalar()
        return max_t

    def min_timestamp(
        self, col: str = None, filters: list[tuple[str, str]] = None
    ) -> datetime | None:
        """Get the object with the minimum timestamp."""
        timestamp_col = col or self.timestamp_col
        min_t = self.min(timestamp_col, filters)
        return datetime.utcfromtimestamp(min_t) if min_t else None

    def min(self, col: str, filters: list[tuple[str, str]]) -> float | None:
        """Get the min value of a column,
        optionally with a where clause."""
        expr = and_(*self._construct_filter(filters))
        stmt = select(func.min(getattr(self._model, col))).where(and_(expr))
        min_t = self._session.exec(stmt).scalar()
        return min_t

    def read_all(self) -> list[Model] | None:
        """Read all objects from the table."""
        objects = self._session.query(self._model).all()
        return objects

    def update(self, object_id: int, obj: Model) -> Model:
        """Update an object in the table."""
        db_object = self._session.get(self._model, object_id)
        if not db_object:
            raise ItemNotFoundException()

        obj_data = obj.model_dump(exclude_unset=True)
        db_object.sqlmodel_update(obj_data)
        self._session.add(db_object)
        self._session.commit()
        self._session.refresh(db_object)
        return db_object

    def where(self, filters: list[tuple[str, str]]) -> list[Model] | None:
        """Filter table by one or more columns where all filters need to be met (AND).

        Args:
            filters (list[tuple[str, str]]): A list of tuples where each tuple contains
            the column name and the value to filter by. E.g. [("name", "John"), ("age", 25)].

        Returns:
            list[Model]: A list of objects that meet all the filters.
        """
        expr = and_(*self._construct_filter(filters))
        return self._session.query(self._model).where(and_(expr)).all()

    def where_in(self, attr: str, values: list[str]) -> list[Model] | None:
        """Filter table by an attribute where the attribute value is in a list of values.
        Args:
            attr (str): The attribute to filter by.
            values (list[str]): A list of values to filter by.
        Returns:
            list[Model]: A list of objects that meet the filter.
        """
        return (
            self._session.query(self._model)
            .filter(getattr(self._model, attr).in_(values))
            .all()
        )

    def query(self, query: str) -> list[Model]:
        """Execute a custom query."""
        objects = self._session.exec(query)
        return objects

    def _construct_filter(self, filters: list[tuple[str, str]]) -> list:
        """Construct a filter from a list of tuples where each tuple
        contains the attribute and the value to filter by.

        Args:
            filters (list[tuple[str, str]]): A list of tuples where each tuple
                contains the attribute and the value to filter by. E.g.
                [("name", "John"), ("age", 25)].
        """
        filter_list = []
        for expr in filters:
            if expr[1] is not None:
                filter_list.append(getattr(self._model, expr[0]) == expr[1])
        return filter_list
