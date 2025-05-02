# Sphere FlexBase Client

Python-клиент для взаимодействия с FlexBase HTTP API. Предоставляет удобный интерфейс для работы с документами и коллекциями.

## Установка

```bash
pip install sphere-flexbase
```

## Быстрый старт

```python
from flexbase_client import FlexBaseClient

# Инициализация клиента
client = FlexBaseClient(api_key="your_super_secret_key")
# Или через переменную окружения FLEXBASE_API_KEY
# export FLEXBASE_API_KEY=your_super_secret_key
# client = FlexBaseClient()

# Создание коллекции
response = client.create_collection("users")
print("Коллекция создана:", response)

# Вставка документа
doc = {
    "name": "Alice",
    "age": 30,
    "active": True
}
result = client.insert_document("users", doc)
print("Документ добавлен:", result)

# Получение всех документов
documents = client.get_documents("users")
for doc in documents:
    print(doc)

# Получение документа по ID
doc = client.get_document_by_id("users", "document_id")
print("Документ:", doc)

# Обновление документа
update = {
    "age": 31,
    "name": "Alice Updated"
}
result = client.update_document("users", "document_id", update)
print("Документ обновлен:", result)

# Поиск по фильтру
result = client.search_documents("users", filters={"name:~": "Alice"})
print("Найдено документов:", result["total"])
for doc in result["data"]:
    print(doc)

# Удаление документа
client.delete_document("users", "document_id")
```

## API Методы

### Коллекции

- `create_collection(name: str) -> Dict` - Создание новой коллекции
- `get_documents(collection: str) -> List[Dict]` - Получение всех документов коллекции

### Документы

- `insert_document(collection: str, data: Dict) -> Dict` - Вставка нового документа
- `get_document_by_id(collection: str, doc_id: str) -> Dict` - Получение документа по ID
- `update_document(collection: str, doc_id: str, changes: Dict) -> Dict` - Обновление документа
- `delete_document(collection: str, doc_id: str) -> None` - Удаление документа
- `search_documents(collection: str, filters: Dict) -> Dict` - Поиск документов по фильтру

## Обработка ошибок

Клиент предоставляет следующие типы исключений:

```python
from flexbase_client.exceptions import (
    FlexBaseError,        # Базовое исключение
    UnauthorizedError,    # Ошибка авторизации (401)
    BadRequestError,      # Неверный запрос (400)
    NotFoundError,        # Ресурс не найден (404)
    ConnectionError,      # Ошибка соединения
    TimeoutError         # Таймаут запроса
)
```

Пример обработки ошибок:

```python
try:
    client.create_collection("users")
except UnauthorizedError:
    print("Ошибка авторизации. Проверьте API ключ")
except BadRequestError as e:
    print(f"Ошибка в запросе: {e}")
except NotFoundError:
    print("Ресурс не найден")
except Exception as e:
    print(f"Неизвестная ошибка: {e}")
```

## Примеры использования с Flask

```python
from flask import Flask, jsonify, request
from flexbase_client import FlexBaseClient

app = Flask(__name__)
db = FlexBaseClient()

@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = db.get_documents("users")
        return jsonify(users)
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/users", methods=["POST"])
def create_user():
    try:
        user = db.insert_document("users", request.json)
        return jsonify(user), 201
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = db.get_document_by_id("users", user_id)
        return jsonify(user)
    except NotFoundError:
        return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 400

if __name__ == "__main__":
    app.run(debug=True)
```

## Поиск документов

Поддерживаются следующие операторы фильтрации:

```python
# Точное совпадение
filters = {"name": "Alice"}

# Частичное совпадение (like)
filters = {"name:~": "Ali"}

# Сравнение
filters = {
    "age:>": 25,    # больше
    "age:>=": 25,   # больше или равно
    "age:<": 30,    # меньше
    "age:<=": 30    # меньше или равно
}

# Комбинация фильтров
filters = {
    "name:~": "Ali",
    "age:>=": 25,
    "active": True
}
```

## Лицензия

MIT # python-sphere-flexbase
# python-sphere-flexbase
