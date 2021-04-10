import socket
import threading
import queue
import time
import re
import json
import sys
import kafka

from loguru import logger
from rich.console import Console
from kafka import KafkaProducer

console = Console()

config = {
    "handlers": [
        {"sink": sys.stdout, "level": "INFO"}   # , format="{time:YYYY-MM-DD at HH:mm:ss} [{level}] {message}"},
    ]
}
logger.configure(**config)

TMP_DIR = '/tmp/kafka.api/'
PREFIX_TMP_NAME = 'kfk-'
KAFKA_TOPIC = 'proxy.py'


class InvalidRequest(Exception):
    pass


def HTTP_parser(raw):
    temp = [i.strip() for i in raw.splitlines()]

    if -1 == temp[0].find('HTTP'):
        raise InvalidRequest('Incorrect Protocol')

    method, path, protocol = [i.strip() for i in temp[0].split()]
    headers = {}
    if ('GET' == method) or ('POST' == method):
        raw_headers = list(
            filter(
                lambda h: re.findall(r"[\w+|-]{1,20}:(.*)", h),
                temp[1:-1]
            )
        )
        for k, v in [i.split(':', 1) for i in raw_headers]:
            headers[k.strip()] = v.strip()
    else:
        raise InvalidRequest('Only accepts GET requests')

    try:
        body = json.loads(temp[-1])
    except json.JSONDecoder:
        body = temp[-1]

    return method, path, protocol, headers, body


class WEBServer:

    def __init__(
            self, 
            host='0.0.0.0',
            port=8000,
            bootstrap_servers: list or str = None) -> None:
        self.host = host
        self.port = port
        self.socket = None
        self.q = queue.Queue(maxsize=100)
        self.bootstrap_servers = bootstrap_servers if bootstrap_servers is not None else ['kafka:9092']
        self.kafka_enable = False

        self.CONNECTION_COUNT = 100
        self.PACKET_SIZE = 1024

    def up(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((self.host, self.port))
            logger.info("server started at -- {0}:{1}".format(self.host, self.port))
        except Exception as err:
            logger.critical(err)
            exit(1)

        threading.Thread(target=self.__worker).start()

        self.__listen()

    def __worker(self):
        time.sleep(30)
        logger.info('worker is running...')
        try:
            producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        except kafka.errors.NoBrokersAvailable as err:
            logger.critical('No Broker Available in %s' % self.bootstrap_servers)
            return
        else:
            self.kafka_enable = True

        while True:
            try:
                body = self.q.get(timeout=3)
            except queue.Empty:
                time.sleep(1)
            else:
                try:
                    future = producer.send(KAFKA_TOPIC, json.dumps(body).encode())
                    record_metadata = future.get(timeout=10)
                except kafka.errors.KafkaTimeoutError as err:
                    logger.critical('[%s] %s' % (body, err))
                except kafka.errors.KafkaError as err:
                    logger.critical('ERR:%s:%s' % (err, body))
                else:
                    logger.info('successful [%s]' % body)

    def __listen(self):
        self.socket.listen(self.CONNECTION_COUNT)
        while True:
            try:
                sock_cli, sock_addr = self.socket.accept()
                sock_cli.settimeout(10)
                threading.Thread(target=self.__handleClient, args=(sock_cli, sock_addr)).start()
            except KeyboardInterrupt:
                logger.info('shutdown... bye bye')

    def __handleClient(self, socket_cli, socket_address):
        while True:
            # raw_data = socket_cli.recv(self.PACKET_SIZE).decode()
            buff_size = 4096
            raw_data = b''
            while True:
                part = socket_cli.recv(buff_size)
                raw_data += part
                if len(part) < buff_size:
                    break
            if not raw_data:
                break

            raw_data = raw_data.decode('utf-8', errors='ignore')

            try:
                response = ("HTTP/1.1 200 OK\n"
                            "Content-Type: text/html\n"
                            "Server: Python\n"
                            "Connection: close\n\n"
                            "{\"code\": 200}")

                parser = HTTP_parser(raw_data)

                body = parser[-1]
                body = {} if not isinstance(body, dict) else body

                logger.info(
                    '%s%s "%s %s%s %s %d" "-" "%s"' % (
                        '' if not body.get('ip') else '%s|' % (
                                body.get('ip')[0] if len(body.get('ip')) > 1 else body.get('ip')
                            ),
                        socket_address[0],
                        parser[0] if not body.get('method') else body.get('method'),
                        '' if not body.get('host') else body.get('host'),
                        parser[1] if not body.get('path') else body.get('path'), parser[2],
                        len(raw_data),
                        parser[3].get('User-Agent')
                    )
                )

                if self.kafka_enable:
                    self.q.put(parser[-1])

                socket_cli.send(response.encode())
            except Exception as err:
                logger.error('handler client: %s' % err)

            socket_cli.close()
            break

    def shutdown(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
