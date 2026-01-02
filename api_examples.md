## HTTP API приложения Faust

### Управление запрещенными словами

**GET /banned_words/** - Получение списка запрещенных слов
```bash
curl http://localhost:6066/banned_words/
```

**POST /banned_words/** - Добавление/удаление запрещенных слов
```bash
# добавление слова/списка слов
curl -X POST http://localhost:6066/banned_words/ \
  -H "Content-Type: application/json" \
  -d '{
    "words": ["badword", "spam", "forbidden"],
    "operation_type": "add"
  }'

# удаление слова/списка слов
curl -X POST http://localhost:6066/banned_words/ \
  -H "Content-Type: application/json" \
  -d '{
    "words": ["badword"],
    "operation_type": "remove"
  }'
```
** В случае доступности api, статус ответа - <b>202 (Accepted)</b>, в логах приложения faust можно увидеть результат выполнения операций


### Управление блокировками пользователей

**GET /users/** - Получение списка всех пользователей с блокировками
```bash
curl http://localhost:6066/users/
```

**GET /users/{user_id}/** - Получение блокировок конкретного пользователя (пользователей, которых он заблокировал с указанием причин, объявленных при блокировке)
```bash
curl http://localhost:6066/users/1/
```

**POST /block_user/** - Заблокировать пользователя
```bash
curl -X POST http://localhost:6066/block_user/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1",
    "blocked_id": "5",
    "comment": "Spam messages",
    "operation_type": "add"
  }'
```
** В случае доступности api, статус ответа - <b>202 (Accepted)</b>, в логах приложения faust можно увидеть результат выполнения операции блокировки


### Отправка и получение сообщений

**POST /messages/** - Отправить сообщение
```bash
curl -X POST http://localhost:6066/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "1",
    "recipient_id": "2",
    "text": "test_message"
  }'
```

**GET /messages/?user_id={id}** - Получение сообщений пользователя в пределах суток
```bash
# Получить последние 50 сообщений (по умолчанию)
curl "http://localhost:6066/messages/?user_id=2"

# С пагинацией
curl "http://localhost:6066/messages/?user_id=2&limit=10&offset=0"
```

**Параметры GET /messages/:**
- `user_id` (обязательный) - ID получателя сообщений
- `limit` (опциональный, по умолчанию 50, макс 100) - количество сообщений
- `offset` (опциональный, по умолчанию 0) - сдвиг для пагинации

## Тестирование API

### 1: Цензура сообщений
```bash
# 1. Добавить запрещенное слово
curl -X POST http://localhost:6066/banned_words/ \
  -H "Content-Type: application/json" \
  -d '{"words": ["badword"], "operation_type": "add"}'

# 2. Отправить сообщение с запрещенным словом
curl -X POST http://localhost:6066/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "11",
    "recipient_id": "12",
    "text": "This contains badword in message"
  }'

# 3. Проверить, что слово заменено на ***
curl "http://localhost:6066/messages/?user_id=12"
# Ожидаемый результат: "This contains *** in message"
```
** для тестирования цензуры сообщений лучше использовать id пользователей больше 9 (пользователи с идентификаторами 1-9 используются для тестовой передачи сообщений)

### 2: Блокировка пользователя
```bash
# 1. Заблокировать пользователя 5 для пользователя 2
curl -X POST http://localhost:6066/block_user/ \
  -H "Content-Type: application/json" \
  -d '{
     "user_id": "2",
     "blocked_id": "5",
     "comment": "Unwanted messages",
     "operation_type": "add"
  }'

** для разблокировки пользователя необходимый тип операции - "remove"

# 2. Попробовать отправить сообщение от заблокированного пользователя
curl -X POST http://localhost:6066/messages/ \
  -H "Content-Type: application/json" \
  -d '{"sender_id": "5", "recipient_id": "2", "text": "Test message"}'
# Ожидаемый результат: HTTP 403 Forbidden

# 3. Проверить список блокировок
curl http://localhost:6066/users/2/
```
** можно заблокировать от пользователя с id 1-9 других тестовых пользователей, сообщение отправлено не будет, что также будет отражено в логах приложения

### 3: Валидация данных
```bash
# Попытка заблокировать самого себя
curl -X POST http://localhost:6066/block_user/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1",
    "blocked_id": "1",
    "comment": "Test",
    "operation_type": "add"
  }'
# Ожидаемый результат: HTTP 400 Bad Request с ошибкой валидации

# Пустой список слов
curl -X POST http://localhost:6066/banned_words/ \
  -H "Content-Type: application/json" \
  -d '{"words": [], "operation_type": "add"}'
# Ожидаемый результат: HTTP 400 Bad Request
```