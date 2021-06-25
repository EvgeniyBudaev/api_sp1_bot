import os
import time
import requests
import logging
import telegram
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HOMEWORK_STATUSES = {
    'reviewing': 'Работа взята в ревью.',
    'rejected': 'В работе есть ошибки, нужно поправить.',
    'approved': 'Ревью успешно пройдено.'}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log',
    filemode='w'
)
# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status is None or status not in HOMEWORK_STATUSES:
        return 'Cтатус неизвестен или нет такого домашнего задания.'
    if status == 'reviewing':
        return f'Работа "{homework_name}" взята в ревью.'
    if status == 'rejected':
        return f'К сожалению, в работе "{homework_name}" нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    """Запрос к API сервиса Практикум.Домашка."""
    if current_timestamp is None:
        current_timestamp = int(time.time())
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_URL,
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
    current_timestamp = int(time.time())  # Начальное значение timestamp
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
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            logging.exception(f'Бот сломался с ошибкой: {e}')
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
