import os
import uuid
import requests
import time
import logging
import re
from PIL import Image
from io import BytesIO

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Константы из документации GigaChat ---
OAUTH_URL = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
CHAT_API_URL = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'
FILES_API_URL_TEMPLATE = 'https://gigachat.devices.sberbank.ru/api/v1/files/{file_id}/content'
SCOPE = 'GIGACHAT_API_PERS'

# --- Переменные для кэширования токена ---
_cached_token = None
_token_expires_at = 0

def get_access_token():
    """
    Получает токен доступа GigaChat, кэшируя его для повторного использования.
    Если токен истек или отсутствует, запрашивает новый.
    """
    global _cached_token, _token_expires_at

    if _cached_token and time.time() < _token_expires_at - 60:
        logger.info("Используется кэшированный токен GigaChat.")
        return _cached_token

    logger.info("Запрос нового токена доступа GigaChat...")
    auth_key = os.getenv('GIGACHAT_AUTHORIZATION_KEY')
    if not auth_key:
        logger.error("Ключ авторизации GigaChat не найден!")
        raise ValueError("GIGACHAT_AUTHORIZATION_KEY не установлен.")

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {auth_key}'
    }
    data = {'scope': SCOPE}

    try:
        # Отключаем проверку SSL-сертификата, как это часто требуется для корпоративных сред
        response = requests.post(OAUTH_URL, headers=headers, data=data, verify=False)
        response.raise_for_status()
        token_data = response.json()
        _cached_token = token_data['access_token']
        _token_expires_at = token_data.get('expires_at', 0) / 1000
        logger.info("Новый токен GigaChat успешно получен.")
        return _cached_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе токена GigaChat: {e}")
        _cached_token = None
        _token_expires_at = 0
        return None

def _download_image(file_id: str, access_token: str) -> Image.Image | None:
    """Вспомогательная функция для скачивания изображения по file_id."""
    logger.info(f"Скачивание изображения с file_id: {file_id}")
    headers = {
        'Accept': 'application/octet-stream',
        'Authorization': f'Bearer {access_token}'
    }
    url = FILES_API_URL_TEMPLATE.format(file_id=file_id)
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        logger.info("Изображение успешно скачано и обработано.")
        return image
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при скачивании изображения: {e}")
    except IOError as e:
        logger.error(f"Ошибка при обработке изображения: {e}")
    return None

def generate_image_with_gigachat(prompt: str) -> Image.Image | None:
    """
    Основная функция. Генерирует изображение с помощью GigaChat по текстовому промпту.
    """
    access_token = get_access_token()
    if not access_token:
        return None

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": f"Нарисуй: {prompt}"
            }
        ],
        "function_call": "auto"
    }

    try:
        logger.info(f"Отправка запроса на генерацию изображения с промптом: '{prompt}'")
        response = requests.post(CHAT_API_URL, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        logger.info(f"Получен ответ от GigaChat: {content}")

        # Ищем file_id в ответе. Пример ответа: <img src="ID" fuse="true"/>
        match = re.search(r'<img src="([^"]+)"', content)
        if match:
            file_id = match.group(1)
            logger.info(f"Найден file_id изображения: {file_id}")
            return _download_image(file_id, access_token)
        else:
            logger.error("В ответе GigaChat не найден file_id изображения.")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе на генерацию изображения: {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"Ошибка при разборе ответа от GigaChat: {e}")
    return None

def generate_text_with_gigachat(prompt: str) -> str | None:
    """
    Генерирует короткий текст (историю) с помощью GigaChat по текстовому промпту.
    """
    access_token = get_access_token()
    if not access_token:
        return None

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    # Промпт для генерации истории
    story_prompt = f"Напиши короткую, загадочную историю в одном абзаце на тему: '{prompt}'"
    
    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": story_prompt
            }
        ],
        "temperature": 0.85, # Добавим немного креативности
        "max_tokens": 200,
    }

    try:
        logger.info(f"Отправка запроса на генерацию текста с промптом: '{story_prompt}'")
        response = requests.post(CHAT_API_URL, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        logger.info(f"GigaChat сгенерировал историю: {content[:100]}...")
        return content

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе на генерацию текста: {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"Ошибка при разборе ответа от GigaChat: {e}")
    return None
