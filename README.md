# Sphere FlexBase Client

Python-клиент для взаимодействия с FlexBase HTTP API. Предоставляет удобный интерфейс для работы с документами, коллекциями и расширенным поиском.

## Установка

```bash
pip install sphere-flexbase
```

## Быстрый старт

```python
from flexbase_client import FlexBaseClient, SearchQuery

# Инициализация клиента
client = FlexBaseClient(api_key="your_super_secret_key")
# Или через переменную окружения FLEXBASE_API_KEY
# export FLEXBASE_API_KEY=your_super_secret_key
# client = FlexBaseClient()

# Создание коллекции
client.create_collection("products")

# Вставка документа
product = {
    "name": "iPhone 15 Pro",
    "price": 999,
    "category": "electronics",
    "in_stock": True
}
result = client.insert_document("products", product)
print(f"Добавлен: {result['_id']}")

# Простой поиск
results = client.search_documents("products", filters={"category": "electronics"})
print(f"Найдено: {results['total']} товаров")
```

---

## Содержание

- [Основные операции](#основные-операции)
- [Простой поиск](#простой-поиск)
- [Расширенный поиск с SearchQuery](#расширенный-поиск-с-searchquery)
- [Операторы поиска](#операторы-поиска)
- [Полнотекстовый поиск (FTS)](#полнотекстовый-поиск-fts)
- [Асинхронный поиск](#асинхронный-поиск)
- [Сортировка и пагинация](#сортировка-и-пагинация)
- [Обработка ошибок](#обработка-ошибок)
- [Примеры использования](#примеры-использования)

---

## Основные операции

### Коллекции

```python
# Создать коллекцию
client.create_collection("users")

# Получить все документы
docs = client.get_documents("users")
```

### Документы

```python
# Вставить документ
doc = {"name": "Alice", "age": 30, "email": "alice@example.com"}
result = client.insert_document("users", doc)
doc_id = result["_id"]

# Получить документ по ID
doc = client.get_document_by_id("users", doc_id)

# Обновить документ
client.update_document("users", doc_id, {"age": 31})

# Удалить документ
client.delete_document("users", doc_id)
```

---

## Простой поиск

Метод `search_documents()` поддерживает фильтры через параметры URL:

```python
# Точное совпадение
results = client.search_documents("products", filters={"category": "electronics"})

# Подстрока (регистронезависимо)
results = client.search_documents("users", filters={"name:~": "alice"})

# Сравнение чисел
results = client.search_documents("products", 
    filters={"price:>=": 100, "price:<=": 1000}
)

# IN список
results = client.search_documents("orders", 
    filters={"status:in": "pending,processing,shipped"}
)

# BETWEEN диапазон
results = client.search_documents("products", 
    filters={"price:between": "500,2000"}
)

# Regex
results = client.search_documents("users", 
    filters={"email:regex": ".*@gmail\\.com"}
)

# С сортировкой
results = client.search_documents("products",
    filters={"category": "electronics"},
    sort="price",
    order="desc",
    page=1,
    per_page=20
)
```

---

## Расширенный поиск с SearchQuery

Для сложных запросов используйте билдер `SearchQuery`:

```python
from flexbase_client import SearchQuery

# Создание запроса
query = SearchQuery()\
    .contains("name", "phone")\
    .between("price", 100, 1000)\
    .in_list("category", ["electronics", "gadgets"])\
    .ne("status", "deleted")\
    .sort("price", "desc")\
    .page(1).per_page(20)

# Выполнение
results = client.search("products", query)
print(f"Найдено: {results['total']}")
for product in results['data']:
    print(f"{product['name']}: ${product['price']}")
```

---

## Операторы поиска

### Методы SearchQuery

| Метод | Описание | Пример |
|-------|----------|--------|
| `eq(field, value)` | Точное совпадение | `.eq("status", "active")` |
| `ne(field, value)` | Не равно | `.ne("status", "deleted")` |
| `gt(field, value)` | Больше | `.gt("age", 18)` |
| `gte(field, value)` | Больше или равно | `.gte("price", 100)` |
| `lt(field, value)` | Меньше | `.lt("age", 65)` |
| `lte(field, value)` | Меньше или равно | `.lte("price", 1000)` |
| `contains(field, value)` | Подстрока | `.contains("name", "phone")` |
| `in_list(field, values)` | В списке | `.in_list("status", ["active", "pending"])` |
| `between(field, min, max)` | В диапазоне | `.between("price", 100, 500)` |
| `regex(field, pattern)` | Regex | `.regex("email", ".*@gmail\\.com")` |
| `fuzzy(field, value, distance)` | Нечёткий поиск | `.fuzzy("name", "iPhon", 2)` |
| `exists(field)` | Поле существует | `.exists("photo")` |
| `not_exists(field)` | Поле отсутствует | `.not_exists("deleted_at")` |
| `fts(query, fields)` | Полнотекстовый поиск | `.fts("iPhone Pro", ["name", "description"])` |
| `sort(field, order)` | Сортировка | `.sort("created_at", "desc")` |
| `page(n)` | Номер страницы | `.page(2)` |
| `per_page(n)` | Элементов на странице | `.per_page(50)` |

### Примеры операторов

**1. Точное совпадение**
```python
query = SearchQuery().eq("category", "electronics")
```

**2. Диапазон чисел**
```python
query = SearchQuery()\
    .gte("price", 100)\
    .lte("price", 1000)
```

**3. Подстрока (регистронезависимо)**
```python
query = SearchQuery().contains("name", "phone")
# Найдёт: "iPhone", "Phone", "smartphone"
```

**4. IN список**
```python
query = SearchQuery().in_list("status", ["active", "pending", "review"])
```

**5. BETWEEN**
```python
query = SearchQuery().between("price", 500, 2000)
```

**6. Regex**
```python
query = SearchQuery().regex("email", r".*@(gmail|yahoo)\.com")
```

**7. Fuzzy поиск (опечатки)**
```python
query = SearchQuery().fuzzy("name", "iPhon", distance=2)
# Найдёт: "iPhone", "iPhon", "iPhone15" (до 2 символов отличия)
```

**8. Поле существует**
```python
query = SearchQuery().exists("photo")
# Только документы с полем photo
```

**9. Поле отсутствует**
```python
query = SearchQuery().not_exists("deleted_at")
# Только не удалённые документы
```

**10. Комбинация условий (AND)**
```python
query = SearchQuery()\
    .eq("category", "electronics")\
    .gte("price", 100)\
    .lte("price", 1000)\
    .eq("in_stock", True)
# Все условия должны совпасть (AND)
```

---

## Полнотекстовый поиск (FTS)

FlexBase автоматически индексирует поля: `name`, `title`, `description`, `content`, `brand`, `category`.

### Простой FTS

```python
# Поиск по всем проиндексированным полям
results = client.fts_search("products", "iPhone Pro Max")

# С пагинацией
results = client.fts_search("products", 
    query="беспроводные наушники",
    page=1,
    per_page=20
)
```

### FTS по конкретным полям

```python
results = client.fts_search("products",
    query="смартфон",
    fields=["name", "description"]
)
```

### FTS с SearchQuery

```python
query = SearchQuery()\
    .fts("iPhone Pro", fields=["name", "description"])\
    .gte("price", 500)\
    .eq("in_stock", True)

results = client.search("products", query)
```

**Особенности:**
- Ранжирование по алгоритму BM25
- Регистронезависимый поиск
- Автоматическая индексация при вставке

---

## Асинхронный поиск

Для больших коллекций используйте асинхронный поиск:

```python
import time

# Запустить задачу
job_id = client.search_async("products", 
    filters={"category": "electronics"}
)
print(f"Job started: {job_id}")

# Ожидание результата
while True:
    status = client.get_search_job(job_id)
    
    if status["status"] == "done":
        print(f"Найдено: {status['result']['total']}")
        for doc in status['result']['data']:
            print(doc['name'])
        break
    elif status["status"] == "error":
        print(f"Ошибка: {status.get('error')}")
        break
    
    print("Ожидание...")
    time.sleep(0.5)
```

**Статусы:**
- `queued` — в очереди
- `running` — выполняется
- `done` — завершено
- `error` — ошибка

**Автоочистка:** Завершённые задачи удаляются через 5 минут.

---

## Сортировка и пагинация

### С search_documents()

```python
results = client.search_documents("products",
    filters={"category": "electronics"},
    sort="price",
    order="asc",  # или "desc"
    page=2,
    per_page=50
)

print(f"Страница {results['page']} из {results['total_pages']}")
print(f"Всего: {results['total']} товаров")
```

### С SearchQuery

```python
query = SearchQuery()\
    .eq("category", "electronics")\
    .sort("price", "desc")\
    .page(1)\
    .per_page(20)

results = client.search("products", query)
```

### Навигация по страницам

```python
def get_all_pages(client, collection, query):
    """Получить все страницы результатов"""
    page = 1
    all_docs = []
    
    while True:
        query.page(page)
        results = client.search(collection, query)
        
        all_docs.extend(results['data'])
        
        if page >= results['total_pages']:
            break
        
        page += 1
    
    return all_docs

# Использование
query = SearchQuery().eq("category", "electronics").per_page(100)
all_products = get_all_pages(client, "products", query)
print(f"Всего загружено: {len(all_products)}")
```

---

## Обработка ошибок

```python
from flexbase_client import (
    FlexBaseError,        # Базовое исключение
    UnauthorizedError,    # Ошибка авторизации (401)
    BadRequestError,      # Неверный запрос (400)
    NotFoundError,        # Ресурс не найден (404)
    ConnectionError,      # Ошибка соединения
    TimeoutError         # Таймаут запроса
)

try:
    results = client.search_documents("products", 
        filters={"price:>=": "invalid"}
    )
except UnauthorizedError:
    print("Проверьте API ключ")
except BadRequestError as e:
    print(f"Неверный запрос: {e}")
except NotFoundError:
    print("Коллекция не найдена")
except ConnectionError:
    print("Не удалось подключиться к серверу")
except FlexBaseError as e:
    print(f"Ошибка FlexBase: {e}")
```

---

## Примеры использования

### E-commerce: поиск товаров

```python
from flexbase_client import FlexBaseClient, SearchQuery

client = FlexBaseClient()

# Поиск смартфонов в диапазоне цен
query = SearchQuery()\
    .contains("name", "phone")\
    .between("price", 500, 1500)\
    .eq("in_stock", True)\
    .sort("price", "asc")\
    .per_page(20)

results = client.search("products", query)

for product in results['data']:
    print(f"{product['name']}: ${product['price']}")
```

### CRM: поиск клиентов

```python
# Активные клиенты из Москвы старше 25 лет
query = SearchQuery()\
    .eq("status", "active")\
    .eq("city", "Москва")\
    .gte("age", 25)\
    .exists("email")\
    .sort("created_at", "desc")

clients = client.search("clients", query)
```

### Полнотекстовый поиск по статьям

```python
# Поиск статей о Python
results = client.fts_search("articles",
    query="Python программирование",
    fields=["title", "content"],
    page=1,
    per_page=10
)

for article in results['data']:
    print(f"{article['title']} (релевантность: {article.get('_score', 0)})")
```

### Fuzzy поиск пользователей

```python
# Поиск с учётом опечаток
query = SearchQuery()\
    .fuzzy("name", "Alise", distance=2)\
    .exists("email")

# Найдёт: Alice, Alise, Elise
users = client.search("users", query)
```

### Сложный запрос с множеством условий

```python
query = SearchQuery()\
    .contains("description", "wireless")\
    .in_list("brand", ["Apple", "Samsung", "Sony"])\
    .between("price", 100, 500)\
    .gte("rating", 4.0)\
    .eq("in_stock", True)\
    .not_exists("discontinued")\
    .sort("rating", "desc")\
    .page(1).per_page(50)

products = client.search("products", query)
print(f"Найдено {products['total']} товаров")
```

### Flask API с поиском

```python
from flask import Flask, request, jsonify
from flexbase_client import FlexBaseClient, SearchQuery

app = Flask(__name__)
db = FlexBaseClient()

@app.route("/api/products/search", methods=["POST"])
def search_products():
    data = request.json
    query = SearchQuery()
    
    # Полнотекстовый поиск
    if "q" in data:
        query.fts(data["q"], ["name", "description"])
    
    # Фильтры
    if "category" in data:
        query.eq("category", data["category"])
    if "min_price" in data and "max_price" in data:
        query.between("price", data["min_price"], data["max_price"])
    if "in_stock" in data:
        query.eq("in_stock", data["in_stock"])
    
    # Сортировка и пагинация
    query.sort(data.get("sort", "created_at"), data.get("order", "desc"))
    query.page(data.get("page", 1)).per_page(data.get("per_page", 20))
    
    try:
        results = db.search("products", query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
```

---

## API Методы

### Коллекции
- `create_collection(name: str) -> Dict`

### Документы
- `insert_document(collection: str, data: Dict) -> Dict`
- `get_documents(collection: str) -> List[Dict]`
- `get_document_by_id(collection: str, doc_id: str) -> Dict`
- `update_document(collection: str, doc_id: str, changes: Dict) -> Dict`
- `delete_document(collection: str, doc_id: str) -> None`

### Поиск
- `search_documents(collection, filters, page, per_page, sort, order) -> Dict`
- `search(collection, query: SearchQuery) -> Dict`
- `fts_search(collection, query, fields, page, per_page) -> Dict`
- `search_async(collection, filters, page, per_page) -> str`
- `get_search_job(job_id: str) -> Dict`

---

## Лицензия

MIT
