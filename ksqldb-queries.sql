-- 1) Создание исходного потока из топика messages
CREATE STREAM IF NOT EXISTS messages_stream (
    sender_id VARCHAR,
    recipient_id VARCHAR,
    text VARCHAR,
    timestamp BIGINT
) WITH (
    KAFKA_TOPIC='messages',
    VALUE_FORMAT='JSON'
);

-- 2) Таблица для агрегирования данных по каждому пользователю за сутки
-- CREATE TABLE IF NOT EXISTS user_statistics AS
--     SELECT
--         sender_id,
--         COUNT(*) as messages_sent,
--         COUNT_DISTINCT(recipient_id) as recipients_amount,
--         COLLECT_LIST(text) as all_messages
--     FROM messages_stream
--     GROUP BY sender_id
--     EMIT CHANGES;

CREATE TABLE IF NOT EXISTS user_day_statistics AS
    SELECT
        sender_id,
        COUNT(*) as messages_sent,
        COUNT_DISTINCT(recipient_id) as recipients_amount,
        COLLECT_LIST(text) as all_messages
    FROM messages_stream
    WINDOW TUMBLING (SIZE 24 HOUR)
    GROUP BY sender_id
    EMIT CHANGES;

-- 3) Общее количество отправленных сообщений
SELECT SUM(messages_sent) AS total_messages
FROM user_day_statistics
EMIT CHANGES;

-- 4) Число уникальных отправителей (количество пользователей)
SELECT COUNT(*) as total_unique_senders
FROM user_day_statistics
EMIT CHANGES;

-- 5) Количество сообщений, отправленных каждым пользователем
SELECT sender_id, messages_sent
FROM user_day_statistics
EMIT CHANGES;

-- 6) Полная статистика по конкретному пользователю
SELECT sender_id, messages_sent, recipients_amount, all_messages
FROM user_day_statistics
WHERE sender_id = '1'
EMIT CHANGES;

