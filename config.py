import logging
import os
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_USERNAME = 'root'
ROOT_PASSWORD = 'Arse@1990'
Avalai_API = "aa-4xhO0hL9vzi7m8fCOLZqY5G02fcsfCyWL2jbmC9nzUlJkprC"
Talkbot_API = "sk-69a9bec33dedd7311f91cb78d60d849c"
#IoType_API = "eKM0yz0On7nJkTrWhhmXxiAjYGi14Kty"

log_file_path = os.path.join(PATH, "logs", "debug.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logger = logging.getLogger('agi_logger')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setStream(open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False))

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)