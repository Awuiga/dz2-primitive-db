# Primitive Database
## Возможности

- создание таблиц;
- автоматическое добавление `ID:int`;
- удаление таблиц с подтверждением;
- просмотр списка таблиц;
- `INSERT`, `SELECT`, `UPDATE`, `DELETE`;
- фильтрация через `WHERE`;
- изменение значений через `SET`;
- типы `int`, `str`, `bool`;
- отдельный JSON-файл для данных каждой таблицы;
- PrettyTable для вывода результатов;
- обработка ошибок через декоратор;
- замер времени выполнения операций;
- кэширование одинаковых `SELECT`-запросов через замыкание.

## Структура проекта

```text
src/primitive_db/
├── __init__.py
├── main.py
├── engine.py
├── core.py
├── utils.py
├── parser.py
├── decorators.py
└── constants.py
```

Назначение модулей:

- `main.py` — точка входа;
- `engine.py` — основной цикл программы и обработка команд;
- `core.py` — основные операции с таблицами и записями;
- `utils.py` — чтение и запись JSON;
- `parser.py` — разбор сложных команд;
- `decorators.py` — декораторы и кэш через замыкание;
- `constants.py` — константы.

## Установка

Требуется Python 3.12+ и `uv`.

```bash
uv sync
```

## Запуск

```bash
uv run database
```

или:

```bash
make run
```

## Проверка кода

```bash
uv run ruff check .
```

или:

```bash
make lint
```

## Сборка

```bash
uv build
```

или:

```bash
make build
```

## Управление таблицами

Создание:

```text
create_table users name:str age:int is_active:bool
```

Пример результата:

```text
Таблица "users" успешно создана со столбцами:
ID:int, name:str, age:int, is_active:bool
```

Список таблиц:

```text
list_tables
```

Удаление таблицы:

```text
drop_table users
```

Перед удалением программа запросит подтверждение:

```text
Вы уверены, что хотите выполнить "удаление таблицы"? [y/n]:
```

## CRUD-операции

Добавить запись:

```text
insert into users values ("Sergei", 28, true)
```

Прочитать все записи:

```text
select from users
```

Фильтрация:

```text
select from users where age = 28
select from users where name = "Sergei"
```

Обновление:

```text
update users set age = 29 where name = "Sergei"
```

Удаление:

```text
delete from users where ID = 1
```

Удаление записи также требует подтверждения.

Информация о таблице:

```text
info users
```

## Поддерживаемые типы

- `int`
- `str`
- `bool`

Строковые значения в командах необходимо писать в кавычках:

```text
"Sergei"
```

Логические значения:

```text
true
false
```

## Полный сценарий для asciinema

Для финальной демонстрации рекомендуется выполнить:

```text
uv sync
uv run database
create_table users name:str age:int is_active:bool
list_tables
insert into users values ("Sergei", 28, true)
insert into users values ("Anna", 22, false)
select from users
select from users where name = "Sergei"
update users set age = 29 where name = "Sergei"
select from users
delete from users where ID = 2
y
info users
drop_table users
y
list_tables
exit
```

## Демонстрация работы

Запись показывает создание таблицы, CRUD-операции,
работу подтверждения действий и удаление таблицы.

[![asciicast](https://asciinema.org/a/qCWHGUy8rQqzogKf.svg)](https://asciinema.org/a/qCWHGUy8rQqzogKf)

## Команды Makefile

```text
make install
make run
make lint
make format
make build
```
