"""Основные функции для работы с таблицами и данными."""

from .constants import ID_COLUMN, TYPE_INT, VALID_TYPES
from .decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

select_cache = create_cacher()


def get_schema(metadata, table_name):
    """Возвращает схему указанной таблицы."""

    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    return metadata[table_name]


def _check_value_type(value, type_name):
    """Возвращает True, если тип значения совпадает с типом в схеме."""

    expected_type = VALID_TYPES[type_name]
    return type(value) is expected_type


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу и автоматически добавляет столбец ID:int."""

    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    schema = {ID_COLUMN: TYPE_INT}

    for column_name, type_name in columns:
        if type_name not in VALID_TYPES:
            raise ValueError(
                f"Некорректное значение: {type_name}. Попробуйте снова."
            )

        if column_name == ID_COLUMN:
            if type_name != TYPE_INT:
                raise ValueError("ID должен иметь тип int.")
            continue

        if column_name in schema:
            raise ValueError(
                f"Некорректное значение: {column_name}. "
                "Столбец уже существует."
            )

        schema[column_name] = type_name

    metadata[table_name] = schema
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет существующую таблицу из метаданных."""

    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Добавляет одну запись после проверки её по схеме таблицы."""

    schema = get_schema(metadata, table_name)
    columns = [column for column in schema if column != ID_COLUMN]

    if len(values) != len(columns):
        raise ValueError(
            "Некорректное количество значений. "
            f"Ожидалось: {len(columns)}, получено: {len(values)}."
        )

    for column, value in zip(columns, values):
        type_name = schema[column]

        if not _check_value_type(value, type_name):
            raise ValueError(
                f"Столбец {column} ожидает значение типа {type_name}."
            )

    ids = [row[ID_COLUMN] for row in table_data]
    new_id = max(ids) + 1 if ids else 1

    row = {ID_COLUMN: new_id}

    for column, value in zip(columns, values):
        row[column] = value

    table_data.append(row)
    return table_data


@handle_db_errors
@log_time
def select(table_name, table_data, where_clause=None):
    """Возвращает все записи или записи, подходящие под условие WHERE."""

    key = (table_name, repr(table_data), repr(where_clause))

    def get_result():
        if where_clause is None:
            return [row.copy() for row in table_data]

        column, value = next(iter(where_clause.items()))

        return [
            row.copy()
            for row in table_data
            if row.get(column) == value
        ]

    return select_cache(key, get_result)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи, подходящие под условие WHERE."""

    where_column, where_value = next(iter(where_clause.items()))

    for row in table_data:
        if row.get(where_column) == where_value:
            for column, value in set_clause.items():
                row[column] = value

    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет записи, подходящие под условие WHERE."""

    column, value = next(iter(where_clause.items()))

    return [
        row
        for row in table_data
        if row.get(column) != value
    ]
