import requests
from environs import Env
import logging
import telegram
from time import sleep


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(level=logging.INFO)

    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        "Authorization": env.str('DVMN_TOKEN')
    }

    params = {}

    bot = telegram.Bot(token=env.str('TELEGRAM_TOKEN'))

    chat_id = env.str('TELEGRAM_CHAT_ID')

    while True:

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            dvmn_response = response.json()

            if dvmn_response['status'] == 'timeout':
                logging.info(f'Нет новых сообщений: {dvmn_response["timestamp_to_request"]}')

            else:
                logging.info('Сообщение получено')
                params['timestamp'] = dvmn_response['last_attempt_timestamp']

                for new_attempt in dvmn_response['new_attempts']:
                    text = f'Проверка работы <b>{new_attempt["lesson_title"]}</b> завершена'
                    if new_attempt['is_negative']:
                        text += '<i>\n\nПреподователю всем понравилось!</i>'
                    else:
                        text += '<i>\n\nВ работе нашлись ошибки!!!</i>'
                    bot.send_message(chat_id=chat_id, text=text, timeout=300, parse_mode=telegram.ParseMode.HTML)

        except requests.exceptions.ReadTimeout:
            logging.info('Время соединения истекло')

        except ConnectionError:
            logging.info('Ошибка соединения')
            sleep(60)


if __name__ == '__main__':
    main()
