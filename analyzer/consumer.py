import os
import time

from kafka import KafkaConsumer
from rich import pretty
from contextlib import contextmanager
from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.measure import Measurement
from rich.table import Table
from rich.text import Text

BEAT_TIME = 0.04

pretty.install()

console = Console()
"""
console.clear()


@contextmanager
def beat(length: int = 1) -> None:
	yield
	time.sleep(length * BEAT_TIME)


def tableView():
	with Live(table_centered, console=console, screen=False, refresh_per_second=20):
		pass
"""
if __name__ == '__main__':
	print('run')
	# To consume latest messages and auto-commit offsets
	consumer = KafkaConsumer('proxy.py',
							 bootstrap_servers=['kafka:9092'])
	for message in consumer:
		# message value and key are raw bytes -- decode if necessary!
		# e.g., for unicode: `message.value.decode('utf-8')`
		console.print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
											  message.offset, message.key,
											  message.value))
