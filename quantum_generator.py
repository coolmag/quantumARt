# -*- coding: utf-8 -*-
# quantum_generator.py

from qiskit import QuantumCircuit
from qiskit_aer import Aer
import logging

logger = logging.getLogger(__name__)

# --- Параметры ---
NUM_QUBITS = 32 # Максимум кубитов для максимальной энтропии

# --- Функции для получения квантовой случайности ---
def create_art_circuit(n_qubits: int) -> QuantumCircuit:
    circuit = QuantumCircuit(n_qubits)
    circuit.h(range(n_qubits))
    circuit.barrier()
    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            if (i + j) % 2 == 0:
                circuit.cx(i, j)
    circuit.barrier()
    circuit.measure_all()
    return circuit

def get_quantum_bits(circuit: QuantumCircuit) -> str:
    simulator = Aer.get_backend('qasm_simulator')
    result = simulator.run(circuit, shots=1).result()
    counts = result.get_counts()
    return list(counts.keys())[0]

# --- "ВСЕЛЕННАЯ" СЛОВ ДЛЯ ОРАКУЛА ---

# --- Категория 1: ЭПИЧЕСКОЕ ИСКУССТВО ---
ART_SUBJECTS = ["галактический левиафан", "забытая цитадель в облаках", "механический ангел", "кристаллический лес", "трон из застывшего времени", "космический корабль-собор", "город на спине гигантской черепахи", "библиотека снов", "кузница звезд", "оракул из сингулярности", "призрачный самурай", "королева киборгов"]
ART_ACTIONS = ["охраняет древний артефакт", "путешествует сквозь туманность", "пробуждается ото сна длиной в тысячелетие", "собирает звездную пыль", "смотрит на рождение новой галактики", "кует меч из света кометы", "читает манускрипт о будущем Вселенной"]
ART_DETAILS = ["сложная гравировка на броне", "геометрические узоры света", "голографические проекции", "парящие в воздухе руны", "частицы энергии", "фрактальные структуры", "жидкий металл", "невозможная геометрия"]

# --- Категория 2: МЕМЫ ---
MEME_SUBJECTS = ["Капибара", "Сиба-ину Доге", "Гарольд, скрывающий боль", "Женщина, кричащая на кота", "Неверный парень", "Кот за столом", "Лягушонок Пепе", "Дрейк в оранжевой куртке"]
MEME_CONTEXTS = ["в офисе", "на пляже", "в космосе", "на встрече выпускников", "в библиотеке", "на рок-концерте", "во время интервью", "в суде", "объясняет квантовую физику", "пытается собрать мебель из IKEA"]

# --- Категория 3: КОТЫ ---
CAT_BREEDS = ["мейн-кун", "сфинкс", "бенгальский кот", "рэгдолл", "шотландский вислоухий", "просто пушистый кот", "дворовый харизматичный кот"]
CAT_ROLES = ["король", "астронавт", "детектив", "волшебник", "повар", "пират", "художник", "ученый", "ниндзя"]
CAT_SETTINGS = ["на троне из подушек", "в космическом корабле", "в нуарном городе под дождем", "в магической библиотеке", "на кухне, полной рыбы", "на палубе пиратского судна", "в художественной студии", "в лаборатории с колбами"]

# --- ОБЩИЕ МОДИФИКАТОРЫ (СЛОЙ АРТ-ДИРЕКТОРА) ---
ARTISTS = ["Грег Рутковски", "Арториас", "Альфонс Муха", "Иван Айвазовский", "Г.Р. Гигер", "Zdzisław Beksiński", "Хаяо Миядзаки", "Сид Мид"]
STYLES = ["цифровая живопись", "концепт-арт", "масло на холсте", "детальная акварель", "скульптура", "аниме-стиль студии Ghibli", "стимпанк", "киберпанк", "биопанк"]
LIGHTING = ["кинематографическое освещение", "объемный свет", "неоновое свечение", "драматические тени", "золотой час", "лунный свет", "биолюминесценция", "мягкий рассеянный свет"]
COMPOSITION = ["широкоугольный кадр", "снято на 85mm объектив", "правило третей", "динамичная композиция", "симметрия", "вид сверху", "голландский угол"]
DETAILS = ["ультра-детализированный", "8k", "разрешение 4k", "сложная детализация", "фотореалистичный", "тренд на Artstation", "Unreal Engine 5", "Octane Render", "V-Ray", "мастерпис"]

# --- ШАБЛОНЫ "ОРАКУЛА" ---
PROMPT_TEMPLATES = [
    lambda p: f"{p['subject']}, {p['action']}, {p['style1']}, в стиле {p['artist1']}, {p['lighting1']}, {p['composition']}, {p['details1']}, {p['details2']}",
    lambda p: f"{p['style2']}: {p['subject']}, {p['action']}, вдохновлено творчеством {p['artist1']} и {p['artist2']}, {p['lighting1']}, {p['lighting2']}, {p['details1']}",
    lambda p: f"Эпичная сцена: {p['subject']} {p['action']}. {p['composition']}, {p['lighting1']}. {p['style1']}, {p['details1']}, {p['details2']}.",
    lambda p: f"{p['subject']}. {p['action']}. {p['style1']}. {p['style2']}. {p['lighting1']}. {p['lighting2']}. {p['composition']}. {p['details1']}. В стиле {p['artist1']}."
]

def _get_parts(seed, parts_map):
    selected_parts = {}
    shift = 0
    for key, arr in parts_map.items():
        selected_parts[key] = arr[(seed >> shift) % len(arr)]
        shift = (shift + 5) % NUM_QUBITS # Используем сдвиг побольше и с зацикливанием
    return selected_parts

def generate_quantum_text_prompt(category: str = 'art') -> (str, str):
    circuit = create_art_circuit(NUM_QUBITS)
    bit_string = get_quantum_bits(circuit)
    seed = int(bit_string, 2)
    logger.info(f"Квантовое семя Оракула: {seed}, категория: {category}")

    prompt = ""
    # Собираем общий пул модификаторов
    director_parts_map = {
        'artist1': ARTISTS, 'artist2': ARTISTS,
        'style1': STYLES, 'style2': STYLES,
        'lighting1': LIGHTING, 'lighting2': LIGHTING,
        'composition': COMPOSITION,
        'details1': DETAILS, 'details2': DETAILS
    }

    if category == 'meme':
        subject_parts_map = {'subject': MEME_SUBJECTS, 'action': MEME_CONTEXTS}
    elif category == 'cat':
        subject_parts_map = {'subject': CAT_BREEDS, 'action': CAT_SETTINGS, 'role': CAT_ROLES}
        # Для котов можно сделать более специфичные шаблоны
        cat_adj = CAT_ADJECTIVES[seed % len(CAT_ADJECTIVES)]
        cat_role = CAT_ROLES[(seed >> 2) % len(CAT_ROLES)]
        cat_setting = CAT_SETTINGS[(seed >> 4) % len(CAT_SETTINGS)]
        director_parts = _get_parts(seed, director_parts_map)
        prompt = f"Портрет кота: {cat_adj} {cat_role} {cat_setting}, {director_parts['style1']}, в стиле {director_parts['artist1']}, {director_parts['lighting1']}, {director_parts['details1']}"
    else: # 'art'
        subject_parts_map = {'subject': ART_SUBJECTS, 'action': ART_ACTIONS}

    if not prompt: # Если это не кот
        all_parts_map = {**subject_parts_map, **director_parts_map}
        parts = _get_parts(seed, all_parts_map)
        template = PROMPT_TEMPLATES[seed % len(PROMPT_TEMPLATES)]
        prompt = template(parts)

    # Убираем дубликаты стилей/художников, если они случайно совпали
    prompt = prompt.replace(parts.get('artist1', ''), parts.get('artist1', '') + ' ' + parts.get('artist2', ''), 1) if parts.get('artist1') == parts.get('artist2') else prompt
    prompt = prompt.replace(parts.get('style1', ''), parts.get('style1', '') + ' ' + parts.get('style2', ''), 1) if parts.get('style1') == parts.get('style2') else prompt

    final_prompt = ", ".join(dict.fromkeys(prompt.split(", "))) # Убираем полные дубликаты секций

    logger.info(f"Сгенерирован промпт Оракула: '{final_prompt}'")
    return final_prompt, bit_string
