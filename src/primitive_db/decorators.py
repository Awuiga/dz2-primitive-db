"""Декораторы и простой кэш для базы данных."""

import time
from functools import wraps


def handle_db_errors(func):
    """Обрабатывает основные ошибки базы данных в одном месте."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            message = error.args[0]
            print(f"Ошибка: {message}")
        except ValueError as error:
            print(f"Ошибка: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")

        return None

    return wrapper


def confirm_action(action_name):
    """Возвращает декоратор, который запрашивает подтверждение действия."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )

            if answer.lower() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Выводит время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start_time
            print(
                f"Функция {func.__name__} выполнилась "
                f"за {elapsed:.3f} секунд"
            )

    return wrapper


def create_cacher():
    """Создаёт замыкание, которое кэширует значения по ключу."""

    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result
