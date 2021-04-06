from kafka import KafkaConsumer

if __name__ == '__main__':
    # To consume latest messages and auto-commit offsets
    consumer = KafkaConsumer('proxy',
                             bootstrap_servers=['localhost:9092'],
                             auto_offset_reset='earliest')
    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                              message.offset, message.key,
                                              message.value))
