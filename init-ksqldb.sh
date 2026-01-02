#!/bin/bash

echo 'Waiting for ksqlDB server...'
while ! curl -s http://ksqldb-server:8088/info > /dev/null; do 
    sleep 2
done
echo 'Creating stream...'
echo "CREATE STREAM IF NOT EXISTS messages_stream (
    sender_id VARCHAR,
    recipient_id VARCHAR,
    text VARCHAR,
    timestamp BIGINT
) WITH (
    KAFKA_TOPIC='messages',
    VALUE_FORMAT='JSON'
);" | ksql http://ksqldb-server:8088
sleep 3
echo 'Creating table...'
echo "CREATE TABLE IF NOT EXISTS user_day_statistics AS
    SELECT
        sender_id,
        COUNT(*) as messages_sent,
        COUNT_DISTINCT(recipient_id) as recipients_amount,
        COLLECT_LIST(text) as all_messages
    FROM messages_stream
    WINDOW TUMBLING (SIZE 24 HOUR)
    GROUP BY sender_id
    EMIT CHANGES;" | ksql http://ksqldb-server:8088
echo 'Done!'