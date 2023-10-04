import requests
from environs import Env
import logging
import telegram
from time import sleep


def send_text_telegram(token, chat_id, text):

    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chat_id, text=text, timeout=300, parse_mode=telegram.ParseMode.HTML)


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(level=logging.INFO)

    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        "Authorization": env.str('DVMN_TOKEN')
    }

    params = {
            "timestamp": '1695561487'
        }

    token = env.str('TELEGRAM_TOKEN')
    chat_id = env.str('CHAT_ID')

    while True:

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_dict = response.json()
            if response_dict['status'] == 'timeout':
                logging.info(f'Нет новых сообщений: {response_dict["timestamp_to_request"]}')
            else:

                logging.info('Сообщение получено')
                params['timestamp'] = response_dict['last_attempt_timestamp']

                for new_attempt in response_dict['new_attempts']:
                    text = f'Проверка работы <b>{new_attempt["lesson_title"]}</b> завершена'
                    if new_attempt['is_negative']:
                        text += '<i>\n\nПреподователю всем понравилось!</i>'
                    else:
                        text += '<i>\n\nВ работе нашлись ошибки!!!</i>'
                    send_text_telegram(token, chat_id, text)
                    sleep(1)

        except requests.exceptions.ReadTimeout:
            logging.info('Время соединения истекло')

        except ConnectionError:
            logging.info('Ошибка соединения')


if __name__ == '__main__':
    main()
