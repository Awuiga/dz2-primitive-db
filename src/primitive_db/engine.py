"""Обработка команд, которые вводит пользователь."""

import shlex

from prettytable import PrettyTable

from .constants import (
    COMMAND_CREATE_TABLE,
    COMMAND_DELETE,
    COMMAND_DROP_TABLE,
    COMMAND_EXIT,
    COMMAND_HELP,
    COMMAND_INFO,
    COMMAND_INSERT,
    COMMAND_LIST_TABLES,
    COMMAND_SELECT,
    COMMAND_UPDATE,
    ID_COLUMN,
    META_FILE,
    PROMPT_TEXT,
    VALID_TYPES,
)
from .core import (
    create_table,
    delete,
    drop_table,
    get_schema,
    insert,
    select,
    update,
)
from .parser import (
    parse_columns,
    parse_delete_command,
    parse_insert_command,
    parse_select_command,
    parse_update_command,
)
from .utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит список команд, поддерживаемых программой."""

    print("\n***База данных***")
    print("\nУправление таблицами:")
    print(
        "create_table <имя_таблицы> <столбец:тип> ... "
        "- создать таблицу"
    )
    print("list_tables - показать список всех таблиц")
    print("drop_table <имя_таблицы> - удалить таблицу")

    print("\nОперации с данными:")
    print(
        "insert into <таблица> values (<значение1>, ...) "
        "- создать запись"
    )
    print("select from <таблица> - прочитать все записи")
    print(
        "select from <таблица> where <столбец> = <значение> "
        "- прочитать записи по условию"
    )
    print(
        "update <таблица> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить записи"
    )
    print(
        "delete from <таблица> where <столбец> = <значение> "
        "- удалить записи"
    )
    print("info <таблица> - вывести информацию о таблице")

    print("\nОбщие команды:")
    print("help - справочная информация")
    print("exit - выход из программы\n")


def _validate_clause(schema, clause):
    """Проверяет столбцы и значения в условиях WHERE и SET."""

    for column, value in clause.items():
        if column not in schema:
            raise ValueError(f'Столбец "{column}" не существует.')

        type_name = schema[column]
        expected_type = VALID_TYPES[type_name]

        if type(value) is not expected_type:
            raise ValueError(
                f"Столбец {column} ожидает тип {type_name}."
            )


def _print_table(schema, rows):
    """Выводит записи в виде таблицы с помощью PrettyTable."""

    table = PrettyTable()
    columns = list(schema.keys())
    table.field_names = columns

    for row in rows:
        table.add_row([row.get(column) for column in columns])

    print(table)


def _create_table(metadata, args):
    """Обрабатывает команду create_table."""

    if len(args) < 3:
        raise ValueError(
            "Некорректное значение: не указаны таблица или столбцы."
        )

    table_name = args[1]
    columns = parse_columns(args[2:])
    result = create_table(metadata, table_name, columns)

    if result is None:
        return

    save_metadata(META_FILE, result)
    save_table_data(table_name, [])

    schema = result[table_name]
    schema_text = ", ".join(
        f"{name}:{type_name}"
        for name, type_name in schema.items()
    )

    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {schema_text}"
    )


def _drop_table(metadata, args):
    """Обрабатывает команду drop_table."""

    if len(args) != 2:
        raise ValueError("Некорректное значение команды drop_table.")

    table_name = args[1]

    # Проверяем существование до confirm_action, чтобы не спрашивать
    # подтверждение для таблицы, которой нет.
    get_schema(metadata, table_name)

    result = drop_table(metadata, table_name)

    if result is None:
        return

    save_metadata(META_FILE, result)
    delete_table_data(table_name)

    print(f'Таблица "{table_name}" успешно удалена.')


def _list_tables(metadata):
    """Выводит названия всех таблиц."""

    if not metadata:
        print("Таблиц нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


def _insert(metadata, command):
    """Обрабатывает команду INSERT."""

    table_name, values = parse_insert_command(command)
    get_schema(metadata, table_name)
    table_data = load_table_data(table_name)

    result = insert(metadata, table_name, values, table_data)

    if result is None:
        return

    save_table_data(table_name, result)
    new_id = result[-1][ID_COLUMN]

    print(
        f"Запись с ID={new_id} успешно добавлена "
        f'в таблицу "{table_name}".'
    )


def _select(metadata, command):
    """Обрабатывает команду SELECT."""

    table_name, where_clause = parse_select_command(command)
    schema = get_schema(metadata, table_name)

    if where_clause is not None:
        _validate_clause(schema, where_clause)

    table_data = load_table_data(table_name)
    result = select(table_name, table_data, where_clause)

    if result is not None:
        _print_table(schema, result)


def _update(metadata, command):
    """Обрабатывает команду UPDATE."""

    table_name, set_clause, where_clause = parse_update_command(command)
    schema = get_schema(metadata, table_name)

    _validate_clause(schema, set_clause)
    _validate_clause(schema, where_clause)

    table_data = load_table_data(table_name)
    where_column, where_value = next(iter(where_clause.items()))

    updated_ids = [
        row[ID_COLUMN]
        for row in table_data
        if row.get(where_column) == where_value
    ]

    result = update(table_data, set_clause, where_clause)

    if result is None:
        return

    save_table_data(table_name, result)

    if not updated_ids:
        print("Подходящие записи не найдены.")
    elif len(updated_ids) == 1:
        print(
            f"Запись с ID={updated_ids[0]} "
            f'в таблице "{table_name}" успешно обновлена.'
        )
    else:
        print(f"Обновлено записей: {len(updated_ids)}.")


def _delete(metadata, command):
    """Обрабатывает команду DELETE."""

    table_name, where_clause = parse_delete_command(command)
    schema = get_schema(metadata, table_name)
    _validate_clause(schema, where_clause)

    table_data = load_table_data(table_name)
    column, value = next(iter(where_clause.items()))

    deleted_ids = [
        row[ID_COLUMN]
        for row in table_data
        if row.get(column) == value
    ]

    result = delete(table_data, where_clause)

    if result is None:
        return

    save_table_data(table_name, result)

    if not deleted_ids:
        print("Подходящие записи не найдены.")
    elif len(deleted_ids) == 1:
        print(
            f"Запись с ID={deleted_ids[0]} успешно удалена "
            f'из таблицы "{table_name}".'
        )
    else:
        print(f"Удалено записей: {len(deleted_ids)}.")


def _info(metadata, args):
    """Обрабатывает команду info."""

    if len(args) != 2:
        raise ValueError("Некорректное значение команды info.")

    table_name = args[1]
    schema = get_schema(metadata, table_name)
    table_data = load_table_data(table_name)

    schema_text = ", ".join(
        f"{name}:{type_name}"
        for name, type_name in schema.items()
    )

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {schema_text}")
    print(f"Количество записей: {len(table_data)}")


def run():
    """Запускает интерактивный цикл обработки команд."""

    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = input(PROMPT_TEXT).strip()

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)

            if not args:
                continue

            command = args[0]

            if command == COMMAND_CREATE_TABLE:
                _create_table(metadata, args)
            elif command == COMMAND_DROP_TABLE:
                _drop_table(metadata, args)
            elif command == COMMAND_LIST_TABLES:
                _list_tables(metadata)
            elif command == COMMAND_INSERT:
                _insert(metadata, user_input)
            elif command == COMMAND_SELECT:
                _select(metadata, user_input)
            elif command == COMMAND_UPDATE:
                _update(metadata, user_input)
            elif command == COMMAND_DELETE:
                _delete(metadata, user_input)
            elif command == COMMAND_INFO:
                _info(metadata, args)
            elif command == COMMAND_HELP:
                print_help()
            elif command == COMMAND_EXIT:
                print("Выход из программы.")
                break
            else:
                print(f"Функции {command} нет. Попробуйте снова.")
        except ValueError as error:
            print(error)
