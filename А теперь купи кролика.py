from flask import Flask, request
import logging
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'animal': 'слон'
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    good_answers = ['ладно', 'куплю', 'покупаю', 'хорошо', 'я куплю', 'я покупаю']
    answer = req['request']['original_utterance'].lower()
    if answer in good_answers:
        if sessionStorage[user_id]['animal'] == 'кролик':
            res['response']['text'] = 'Кролика тоже можно найти на Яндекс.Маркете!'
            res['response']['end_session'] = True
        else:
            res['response']['text'] = 'Слона можно найти на Яндекс.Маркете! А теперь купи кролика!'
            res['response']['end_session'] = True
            sessionStorage[user_id]['suggests'] = [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
            sessionStorage[user_id]['animal'] = 'кролик'
        return

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {sessionStorage[user_id]['animal'] + 'а'}!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={sessionStorage[user_id]['animal']}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()