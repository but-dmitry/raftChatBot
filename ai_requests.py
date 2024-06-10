import requests

prompt_to_film_sample = {
    "modelUri": "gpt://b1gi3q08i2uc7fmcok97/yandexgpt-lite",
    "completionOptions": {
        "stream": False,
        "temperature": 0.6,
        "maxTokens": "2000"
    },
    "messages": [
        {
            "role": "system",
            "text": "ТЫ ПИШЕШЬ ТОЛЬКО СПИСОК НАЗВАНИЙ КНИГ И НЕЛЬЗЯ ПИСАТЬ НИЧЕГО КРОМЕ НАЗВАНИЙ КНИГ И КОЛИЧЕСТВО КНИГ ПЯТЬ!"
        },
        {
            "role": "user",
            "text": "Подбери схожие книги. "
        }
    ]
}

prompt_correct_essay = {
    "modelUri": "gpt://b1gi3q08i2uc7fmcok97/yandexgpt/latest",
    "completionOptions": {
        "stream": False,
        "temperature": 0,
        "maxTokens": "2000"
    },
    "messages": [
        {
            "role": "system",
            "text": "Исправь грамматические, орфографические и пунктуационные ошибки в тексте. Сохраняй исходный порядок слов. Писать комментарии не нужно."
        },
        {
            "role": "user",
            "text": ""
        }
    ]
}

url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Api-Key AQVNzfs91wVI6-p4WLPsYtiFEmyM1_bRKPj_Tx21"
}

def film_advice(fav_films: str = "", req_genre: str = "", req_country: str = ""):
    prompt_to_film = prompt_to_film_sample
    if fav_films != "":
        prompt_to_film['messages'][1]['text'] += "Мои любимые фильмы это " + fav_films + "."
    if req_genre != "":
        prompt_to_film['messages'][1]['text'] += " Я хочу фильм жанра " + req_genre + "."
    if req_country != "":
        prompt_to_film['messages'][1]['text'] += " Я хочу фильм жанра " + req_genre + "."
    response = requests.post(url, headers=headers, json=prompt_to_film)
    return response.json()["result"]['alternatives'][0]['message']['text']

def check_essay(essay_text: str = ""):
    prompt = prompt_correct_essay
    prompt['messages'][1]['text'] = essay_text
    response = requests.post(url, headers=headers, json=prompt)
    return response.json()["result"]['alternatives'][0]['message']['text']


