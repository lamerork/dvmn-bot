import requests
from environs import Env
import logging
import telegram
from time import sleep

logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    env = Env()
    env.read_env()

    logger_bot = telegram.Bot(token=env.str('TELEGRAM_LOG_TOKEN'))
    chat_id = env.str('TELEGRAM_CHAT_ID')

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(logger_bot, chat_id))

    logger.info('Бот запущен')

    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        "Authorization": env.str('DVMN_TOKEN')
    }

    bot = telegram.Bot(token=env.str('TELEGRAM_TOKEN'))

    params = {}

    while True:

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            dvmn_check_list = response.json()

            if dvmn_check_list['status'] == 'timeout':
                logger.info(f'Нет новых сообщений: {dvmn_check_list["timestamp_to_request"]}')
                params['timestamp'] = dvmn_check_list['timestamp_to_request']

            else:
                logger.info('Сообщение получено')
                params['timestamp'] = dvmn_check_list['last_attempt_timestamp']

                for new_attempt in dvmn_check_list['new_attempts']:
                    text = f'Проверка работы <b>{new_attempt["lesson_title"]}</b> завершена'
                    if new_attempt['is_negative']:
                        text += '<i>\n\nПреподователю всем понравилось!</i>'
                    else:
                        text += '<i>\n\nВ работе нашлись ошибки!!!</i>'
                    bot.send_message(chat_id=chat_id, text=text, timeout=300, parse_mode=telegram.ParseMode.HTML)

        except requests.exceptions.ReadTimeout:
            logger.warning('Время соединения истекло')

        except ConnectionError:
            logger.warning('Ошибка соединения')
            sleep(60)
        except Exception as err:
            logger.exception(err)


if __name__ == '__main__':
    main()
