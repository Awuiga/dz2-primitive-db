"""Константы проекта."""

META_FILE = "db_meta.json"
DATA_DIR = "data"

ID_COLUMN = "ID"

TYPE_INT = "int"
TYPE_STR = "str"
TYPE_BOOL = "bool"

VALID_TYPES = {
    TYPE_INT: int,
    TYPE_STR: str,
    TYPE_BOOL: bool,
}

COMMAND_CREATE_TABLE = "create_table"
COMMAND_DROP_TABLE = "drop_table"
COMMAND_LIST_TABLES = "list_tables"
COMMAND_INSERT = "insert"
COMMAND_SELECT = "select"
COMMAND_UPDATE = "update"
COMMAND_DELETE = "delete"
COMMAND_INFO = "info"
COMMAND_HELP = "help"
COMMAND_EXIT = "exit"

PROMPT_TEXT = ">>>Введите команду: "
