import os
import time
import logging

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_URL = 'https://praktikum.yandex.ru/'
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log',
    filemode='w'
)

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    """Определяется статус домашней работы."""
    try:
        homework_name = homework['homework_name']
        status = homework['status']
        if status == 'reviewing':
            return 'Работа взята в ревью.'
        elif status == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
            return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
        elif status == 'approved':
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
            return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
        else:
            return 'Статус домашней работы не определен.'

    except KeyError as error:
        logging.error(error)
        return 'Не верный ответ сервера.'


def get_homeworks(current_timestamp):
    """Запрос к API сервиса Практикум.Домашка."""
    if current_timestamp is None:
        current_timestamp = int(time.time())
    try:
        homework_statuses = requests.get(
            f'{PRAKTIKUM_URL}api/user_api/homework_statuses/',
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
            params={'from_date': current_timestamp})
        return homework_statuses.json()
    except ValueError as error:
        logging.exception(f'Не верно переданное значение {error}')
        return {}
    except requests.exceptions.RequestException as error:
        logging.exception(f'В запросе ошибка {error}')
        return {}


def send_message(message):
    """Отправка сообщения."""
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())
    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    logger.debug('Бот запустился!')

    while True:
        try:
            new_homework = get_homeworks(current_timestamp)
            if new_homework.get('homeworks'):
                logger.info(new_homework.get('homeworks')[0])
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(5 * 60)

        except Exception as e:
            logging.exception(f'Бот сломался с ошибкой: {e}')
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
