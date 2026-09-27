"""Функции для чтения и сохранения JSON-файлов."""

import json
import os

from .constants import DATA_DIR


def load_metadata(filepath):
    """Загружает метаданные базы данных из JSON-файла."""

    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные базы данных в JSON-файл."""

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def _table_filepath(table_name):
    """Возвращает путь к JSON-файлу с данными таблицы."""

    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Загружает записи таблицы из её JSON-файла."""

    filepath = _table_filepath(table_name)

    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в её JSON-файл."""

    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = _table_filepath(table_name)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Удаляет JSON-файл, в котором хранятся записи таблицы."""

    filepath = _table_filepath(table_name)

    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
