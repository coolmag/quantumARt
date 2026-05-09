# -*- coding: utf-8 -*-
import os
import datetime
import hashlib
from flask import Flask, render_template, url_for, redirect, request
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Импортируем наших генераторов
from quantum_generator import generate_quantum_text_prompt
from gigachat_client import generate_image_with_gigachat, generate_text_with_gigachat

app = Flask(__name__)

# Убедимся, что папка для сохранения изображений существует
STATIC_FOLDER = 'static'
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

@app.route('/')
def index():
    """
    Главная страница. Отображает последнее сгенерированное изображение, ошибки и доп. информацию.
    """
    image_name = request.args.get('image')
    error = request.args.get('error')
    generated_prompt = request.args.get('generated_prompt')
    story = request.args.get('story')
    quantum_seed = request.args.get('quantum_seed')
    timestamp = request.args.get('timestamp')
    image_path = url_for('static', filename=image_name) if image_name else None
    
    return render_template('index.html', 
                           image_path=image_path, 
                           image_name=image_name,
                           error=error, 
                           generated_prompt=generated_prompt, 
                           story=story,
                           quantum_seed=quantum_seed,
                           timestamp=timestamp)

@app.route('/generate')
def generate_new_art():
    """
    Запускает процесс генерации нового контента и перенаправляет на главную страницу.
    """
    style = request.args.get('style', 'art')
    user_prompt = request.args.get('prompt', None)
    
    final_prompt = ""
    generated_prompt_for_redirect = None
    generated_story_for_redirect = None
    quantum_seed_for_redirect = None

    print(f"[SERVER] Запрос на генерацию. Стиль: {style}")

    if style == 'gigachat':
        if not user_prompt:
            return redirect(url_for('index', error="Для этого режима необходимо ввести свой текстовый запрос."))
        final_prompt = user_prompt
        print(f"[SERVER] Используется промпт пользователя: '{final_prompt}'")
    
    elif style == 'story_weaver':
        final_prompt, quantum_seed = generate_quantum_text_prompt(category='art')
        generated_prompt_for_redirect = final_prompt
        quantum_seed_for_redirect = quantum_seed
        generated_story_for_redirect = generate_text_with_gigachat(final_prompt)

    else: # 'art', 'meme', 'cat'
        category = style
        final_prompt, quantum_seed = generate_quantum_text_prompt(category=category)
        generated_prompt_for_redirect = final_prompt
        quantum_seed_for_redirect = quantum_seed
    
    if not final_prompt:
        return redirect(url_for('index', error="Не удалось создать промпт для генерации."))

    image_to_save = generate_image_with_gigachat(final_prompt)
    
    if image_to_save:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{style}_{timestamp}.png"
        filepath = os.path.join(STATIC_FOLDER, filename)
        image_to_save.save(filepath)
        print(f"[SERVER] Изображение сохранено: {filepath}")
        return redirect(url_for('index', 
                                image=filename, 
                                generated_prompt=generated_prompt_for_redirect,
                                story=generated_story_for_redirect,
                                quantum_seed=quantum_seed_for_redirect,
                                timestamp=timestamp))

    error_message = "GigaChat не смог сгенерировать запрошенный контент. Попробуйте еще раз."
    return redirect(url_for('index', error=error_message))

@app.route('/certificate')
def certificate():
    """
    Отображает страницу сертификата для сгенерированного произведения.
    """
    image_filename = request.args.get('image_filename')
    prompt = request.args.get('prompt')
    seed = request.args.get('seed')
    timestamp_str = request.args.get('timestamp')
    
    try:
        dt_object = datetime.datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
        formatted_timestamp = dt_object.strftime('%H:%M:%S %d-%m-%Y')
    except (ValueError, TypeError):
        formatted_timestamp = "неизвестно"

    if seed and image_filename:
        unique_id = hashlib.sha256((seed + image_filename).encode()).hexdigest()[:16].upper()
    else:
        unique_id = "N/A"

    return render_template('certificate.html',
                           image_filename=image_filename,
                           prompt=prompt,
                           seed=seed,
                           timestamp=formatted_timestamp,
                           unique_id=unique_id)

if __name__ == '__main__':
    print("--- Квантово-Нейросетевой Генератор 'Аврора' ---")
    print("--- Веб-сервер запущен ---")
    print(f"Откройте в браузере: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
