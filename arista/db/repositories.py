from datetime import datetime
from typing import Generic, TypeVar

from pandas import DataFrame
from sqlalchemy import and_, delete, func, select
from sqlmodel import SQLModel

from arista.db.session import get_session
from arista.exceptions import ItemNotFoundException

Model = TypeVar("Model", bound=SQLModel)


class BaseRepository(Generic[Model]):
    """Generic repository template for all repositories that interact with a table in the database.
    Supports classic CRUD operations as well as custom queries."""

    _model: type[Model]
    timestamp_col: str
    STRFTIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        """Initialize the repository with a database session."""
        self._session = get_session()

    def create(self, obj: Model) -> Model:
        """Create an object in the table.

        Args:
            obj (Model): The model object to create.

        Returns:
            Model: The created model object with an updated ID.
        """
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
        """Delete an object from the table by its ID.

        Args:
            object_id (int): The ID of the object to delete.

        Raises:
            ItemNotFoundException: If the object with the specified ID does not exist.
        """
        obj = self._session.get(self._model, object_id)
        if not obj:
            raise ItemNotFoundException()
        self._session.delete(obj)
        self._session.commit()

    def delete_where(self, attr: str, value: str) -> None:
        """Delete all objects from the table where an attribute matches a given value.

        Args:
            attr (str): The name of the attribute to filter by.
            value (str): The value that the attribute should match.
        """
        statement = delete(self._model).where(getattr(self._model, attr) == value)
        self._session.execute(statement)
        self._session.commit()

    def read(self, object_id: int) -> Model | None:
        """Read an object from the table by its ID.

        Args:
            object_id (int): The ID of the object to retrieve.

        Returns:
            Model | None: The retrieved model object, or None if it does not exist.

        Raises:
            ItemNotFoundException: If the object with the specified ID does not exist.
        """
        obj = self._session.get(self._model, object_id)
        if not obj:
            raise ItemNotFoundException()
        return obj

    def max_timestamp(
        self, col: str = None, filters: list[tuple[str, str]] = None
    ) -> datetime | None:
        """Get the object with the maximum timestamp in a specified column, optionally filtered.

        Args:
            col (str, optional): The name of the timestamp column. Defaults to `self.timestamp_col`.
            filters (list[tuple[str, str]], optional): A list of filters to apply.

        Returns:
            datetime | None: The maximum timestamp, or None if no objects match.
        """
        timestamp_col = col or self.timestamp_col
        max_t = self.max(timestamp_col, filters)

        # convert timestamp to datetime
        if type(max_t) in [float, int]:
            return datetime.utcfromtimestamp(max_t) if max_t else None
        return max_t

    def max(self, col: str, filters: list[tuple[str, str]]) -> float | None:
        """Get the maximum value of a column, optionally with filters.

        Args:
            col (str): The column to find the maximum value in.
            filters (list[tuple[str, str]]): A list of filters to apply.

        Returns:
            float | None: The maximum value, or None if no objects match.
        """
        expr = and_(*self._construct_filter(filters))
        stmt = select(func.max(getattr(self._model, col))).where(expr)
        result = self._session.execute(stmt)
        return result.scalar()

    def min_timestamp(
        self, col: str = None, filters: list[tuple[str, str]] = None
    ) -> datetime | None:
        """Get the object with the minimum timestamp in a specified column, optionally filtered.

        Args:
            col (str, optional): The name of the timestamp column. Defaults to `self.timestamp_col`.
            filters (list[tuple[str, str]], optional): A list of filters to apply.

        Returns:
            datetime | None: The minimum timestamp, or None if no objects match.
        """
        timestamp_col = col or self.timestamp_col
        min_t = self.min(timestamp_col, filters)

        # convert timestamp to datetime
        if type(min_t) in [float, int]:
            return datetime.utcfromtimestamp(min_t) if min_t else None
        return min_t

    def min(self, col: str, filters: list[tuple[str, str]]) -> float | None:
        """Get the minimum value of a column, optionally with filters.

        Args:
            col (str): The column to find the minimum value in.
            filters (list[tuple[str, str]]): A list of filters to apply.

        Returns:
            float | None: The minimum value, or None if no objects match.
        """
        expr = and_(*self._construct_filter(filters))
        stmt = select(func.min(getattr(self._model, col))).where(expr)
        result = self._session.execute(stmt)
        return result.scalar()

    def read_all(self, as_df: bool = False) -> list[Model] | None:
        """Read all objects from the table.

        Args:
            as_df (bool): whether to return the results as dataframe. Else
                return as scalar.

        Returns:
            list[Model] | None: A list of all model objects, or None if none exist.
        """
        stmt = select(self._model)
        result = self._session.execute(stmt).scalars().all()
        if as_df:
            return DataFrame([x.model_dump() for x in result])
        return result

    def update(self, object_id: int, obj: Model) -> Model:
        """Update an object in the table by its ID.

        Args:
            object_id (int): The ID of the object to update.
            obj (Model): The updated model object.

        Returns:
            Model: The updated model object.

        Raises:
            ItemNotFoundException: If the object with the specified ID does not exist.
        """
        db_object = self._session.get(self._model, object_id)
        if not db_object:
            raise ItemNotFoundException()

        obj_data = obj.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_object, key, value)

        self._session.commit()
        self._session.refresh(db_object)
        return db_object

    def where(self, filters: list[tuple[str, str]]) -> list[Model] | None:
        """Filter table by one or more columns where all filters need to be met (AND).

        Args:
            filters (list[tuple[str, str]]): A list of filters to apply.

        Returns:
            list[Model] | None: A list of objects that match all filters, or None if no objects match.
        """
        expr = and_(*self._construct_filter(filters))
        stmt = select(self._model).where(expr)
        result = self._session.execute(stmt)
        return result.scalars().all()

    def where_in(self, attr: str, values: list[str]) -> list[Model] | None:
        """Filter table by an attribute where the attribute value is in a list of values.

        Args:
            attr (str): The attribute to filter by.
            values (list[str]): A list of values to filter by.

        Returns:
            list[Model] | None: A list of objects that match the filter, or None if no objects match.
        """
        stmt = select(self._model).where(getattr(self._model, attr).in_(values))
        result = self._session.execute(stmt)
        return result.scalars().all()

    def query(self, query: str) -> list[Model]:
        """Execute a custom query.

        Args:
            query (str): The raw SQL query to execute.

        Returns:
            list[Model]: The results of the query.
        """
        result = self._session.execute(query)
        return result.scalars().all()

    def _construct_filter(self, filters: list[tuple[str, str]]) -> list:
        """Construct a filter list from tuples of attribute-value pairs.

        Args:
            filters (list[tuple[str, str]]): A list of tuples where each tuple contains an
                attribute and the value to filter by. E.g., [("name", "John"), ("age", 25)].

        Returns:
            list: A list of SQLAlchemy filter expressions.
        """
        filter_list = []
        if filters:
            for expr in filters:
                if expr[1] is not None:
                    filter_list.append(getattr(self._model, expr[0]) == expr[1])
        return filter_list
