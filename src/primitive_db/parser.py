"""Разбор команд, введённых пользователем."""

import shlex


def parse_columns(column_args):
    """Разбирает описания столбцов, например name:str и age:int."""

    columns = []

    for column in column_args:
        if ":" not in column:
            raise ValueError(
                f"Некорректное значение: {column}. Попробуйте снова."
            )

        name, data_type = column.split(":", 1)
        name = name.strip()
        data_type = data_type.strip()

        if not name or not data_type:
            raise ValueError(
                f"Некорректное значение: {column}. Попробуйте снова."
            )

        columns.append((name, data_type))

    return columns


def parse_value(value):
    """Преобразует текстовое значение в int, str или bool."""

    value = value.strip()

    if not value:
        raise ValueError(
            "Некорректное значение: пустое значение. Попробуйте снова."
        )

    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in ('"', "'")
    ):
        return value[1:-1]

    lower_value = value.lower()

    if lower_value == "true":
        return True

    if lower_value == "false":
        return False

    try:
        return int(value)
    except ValueError as error:
        raise ValueError(
            f"Некорректное значение: {value}. "
            "Строковые значения пишите в кавычках."
        ) from error


def split_values(text):
    """Разделяет значения по запятым с учётом кавычек."""

    result = []
    current = []
    quote = None

    for char in text:
        if char in ('"', "'"):
            if quote is None:
                quote = char
            elif quote == char:
                quote = None

            current.append(char)
        elif char == "," and quote is None:
            value = "".join(current).strip()

            if not value:
                raise ValueError("Некорректное значение: пустое значение.")

            result.append(value)
            current = []
        else:
            current.append(char)

    if quote is not None:
        raise ValueError("Некорректное значение: незакрытая кавычка.")

    value = "".join(current).strip()

    if value:
        result.append(value)

    return result


def parse_values(text):
    """Разбирает значения команды, разделённые запятыми."""

    return [parse_value(value) for value in split_values(text)]


def parse_condition(text):
    """Разбирает условие, например age = 28."""

    if "=" not in text:
        raise ValueError(
            f"Некорректное значение: {text}. Ожидался знак =."
        )

    column, value = text.split("=", 1)
    column = column.strip()

    if not column:
        raise ValueError(f"Некорректное значение: {text}.")

    return {column: parse_value(value)}


def parse_set_clause(text):
    """Разбирает присваивания после ключевого слова SET."""

    result = {}

    for assignment in split_values(text):
        result.update(parse_condition(assignment))

    return result


def parse_insert_command(command):
    """Разбирает команду INSERT."""

    command_head, separator, values_part = command.partition(" values ")

    if not separator:
        raise ValueError(f"Некорректное значение: {command}.")

    head_args = shlex.split(command_head)

    if (
        len(head_args) != 3
        or head_args[0] != "insert"
        or head_args[1] != "into"
    ):
        raise ValueError(f"Некорректное значение: {command}.")

    table_name = head_args[2]
    values_part = values_part.strip()

    if not (
        values_part.startswith("(")
        and values_part.endswith(")")
    ):
        raise ValueError(f"Некорректное значение: {values_part}.")

    values = parse_values(values_part[1:-1])

    return table_name, values


def parse_select_command(command):
    """Разбирает команду SELECT."""

    main_part, separator, where_part = command.partition(" where ")
    args = shlex.split(main_part)

    if (
        len(args) != 3
        or args[0] != "select"
        or args[1] != "from"
    ):
        raise ValueError(f"Некорректное значение: {command}.")

    table_name = args[2]
    where_clause = parse_condition(where_part) if separator else None

    return table_name, where_clause


def parse_update_command(command):
    """Разбирает команду UPDATE."""

    before_where, where_separator, where_text = command.partition(" where ")

    if not where_separator:
        raise ValueError(f"Некорректное значение: {command}.")

    before_set, set_separator, set_text = before_where.partition(" set ")

    if not set_separator:
        raise ValueError(f"Некорректное значение: {command}.")

    args = shlex.split(before_set)

    if len(args) != 2 or args[0] != "update":
        raise ValueError(f"Некорректное значение: {command}.")

    table_name = args[1]
    set_clause = parse_set_clause(set_text)
    where_clause = parse_condition(where_text)

    return table_name, set_clause, where_clause


def parse_delete_command(command):
    """Разбирает команду DELETE."""

    before_where, separator, where_text = command.partition(" where ")

    if not separator:
        raise ValueError(f"Некорректное значение: {command}.")

    args = shlex.split(before_where)

    if (
        len(args) != 3
        or args[0] != "delete"
        or args[1] != "from"
    ):
        raise ValueError(f"Некорректное значение: {command}.")

    table_name = args[2]
    where_clause = parse_condition(where_text)

    return table_name, where_clause
