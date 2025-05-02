from flexbase_client.client import FlexBaseClient
import uuid

# Инициализация клиента (можно также задать FLEXBASE_API_KEY через переменную окружения)
client = FlexBaseClient(api_key="your_super_secret_key")

collection = "users"

# 1. Создание коллекции
print("\n[1] Создание коллекции")
try:
    response = client.create_collection(collection)
    print("✔️ Коллекция создана:", response)
except Exception as e:
    print("⚠️ Ошибка при создании коллекции:", e)

# 2. Вставка документа
print("\n[2] Вставка документа")
document_data = {
    "name": "Alice",
    "age": 30,
    "active": True
}
try:
    response = client.insert_document(collection, document_data)
    print("✔️ Документ вставлен:", response)
except Exception as e:
    print("⚠️ Ошибка при вставке документа:", e)

doc_id = ''

# 3. Получение всех документов
print("\n[3] Получение всех документов")
try:
    documents = client.get_documents(collection)
    print(f"✔️ Получено {len(documents)} документов:")
    doc_id = documents[0]["_id"]
    for doc in documents:
        print(doc)
except Exception as e:
    print("⚠️ Ошибка при получении документов:", e)

# 4. Поиск документа по ID
print("\n[4] Поиск документа по ID")
try:
    print(doc_id)
    doc = client.get_document_by_id(collection, doc_id)
    print("✔️ Найден документ:", doc)
except Exception as e:
    print("⚠️ Ошибка при поиске документа:", e)

# 5. Обновление документа
print("\n[5] Обновление документа")
try:
    update = {
        "age": 31,
        "name": "Alice Updated"
    }
    response = client.update_document(collection, doc_id, update)
    print("✔️ Документ обновлён:", response)
except Exception as e:
    print("⚠️ Ошибка при обновлении документа:", e)

# 6. Поиск по фильтру
print("\n[6] Поиск по фильтру")
try:
    result = client.search_documents(collection, filters={"name:~": "Alice"})
    print("✔️ Найдено документов:", result["total"])
    for d in result["data"]:
        print(d)
except Exception as e:
    print("⚠️ Ошибка при поиске документов:", e)

# 7. Удаление документа
print("\n[7] Удаление документа")
try:
    client.delete_document(collection, doc_id)
    print("✔️ Документ удалён")
except Exception as e:
    print("⚠️ Ошибка при удалении документа:", e)
