import requests
from bs4 import BeautifulSoup
import re
import os

# Получаем абсолютный путь к директории, где находится текущий скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))

def to_camel_case(name):
    """Преобразует название цвета в CamelCase формате"""
    cleaned = re.sub(r'[^a-zA-Z\s]', ' ', name)
    words = cleaned.split()
    return ''.join(word.capitalize() for word in words)

def fetch_color_definitions():
    """Получает определения цветов с сайта"""
    url = "https://latexcolor.com/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Попробуем найти таблицу разными способами
        table = soup.find('table', class_='colors-table')  # Старый вариант
        if not table:
            table = soup.find('table')  # Просто первая таблица на странице
        
        if not table:
            # Если таблица не найдена, выведем часть HTML для диагностики
            print("Диагностика: первые 1000 символов HTML:")
            print(response.text[:1000])
            raise RuntimeError("Не удалось найти таблицу цветов на странице")
        
        colors = {}
        
        for row in table.find_all('tr')[1:]:  # Пропускаем заголовок
            cells = row.find_all('td')
            if len(cells) < 5:
                continue
                
            color_name = cells[1].get_text(strip=True)
            hex_value = cells[2].get_text(strip=True)
            
            if not re.match(r'^#?[0-9A-Fa-f]{6}$', hex_value):
                continue
                
            hex_value = hex_value.lstrip('#').upper()
            
            # Конвертация HEX в RGB (0-1)
            r = int(hex_value[0:2], 16) / 255.0
            g = int(hex_value[2:4], 16) / 255.0
            b = int(hex_value[4:6], 16) / 255.0
            
            # Форматирование с 4 знаками после запятой
            r_fmt = f"{r:.4f}"
            g_fmt = f"{g:.4f}"
            b_fmt = f"{b:.4f}"
            
            camel_name = to_camel_case(color_name)
            latex_cmd = fr"\definecolor{{{camel_name}}}{{rgb}}{{{r_fmt}, {g_fmt}, {b_fmt}}}"
            colors[camel_name] = latex_cmd
            
        return colors
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
        return {}

def load_existing_colors(filename):
    """Загружает существующие цвета из базы данных"""
    existing_colors = {}
    if not os.path.exists(filename):
        return existing_colors
        
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            match = re.match(r'^\s*"([^"]+)": r"([^"]+)",?$', line)
            if match:
                color_name = match.group(1)
                latex_cmd = match.group(2)
                existing_colors[color_name] = latex_cmd
    return existing_colors

def update_database(filename, existing_colors, new_colors):
    """Обновляет базу данных новыми цветами"""
    added = False
    with open(filename, 'a', encoding='utf-8') as f:
        for color_name, latex_cmd in new_colors.items():
            if color_name not in existing_colors:
                f.write(f'    "{color_name}": r"{latex_cmd}",\n')
                print(f"Добавлен новый цвет: {color_name}")
                added = True
    return added

def main():
    DB_FILE = os.path.join(script_dir, "color_base.py")      
    existing_colors = load_existing_colors(DB_FILE)
    print(f"В базе уже существует цветов: {len(existing_colors)}")
    
    new_colors = fetch_color_definitions()
    if not new_colors:
        print("Не удалось загрузить цвета с сайта")
        return
    
    print(f"На сайте найдено цветов: {len(new_colors)}")
    
    actual_new_colors = {
        name: cmd 
        for name, cmd in new_colors.items() 
        if name not in existing_colors
    }
    
    if not actual_new_colors:
        print("Новых цветов не обнаружено")
        return
        
    print(f"Найдено новых цветов: {len(actual_new_colors)}")
    
    # Создаем файл, если его нет
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            f.write("COLOR_DEFINITIONS = {\n")
    
    # Добавляем новые цвета
    added = update_database(DB_FILE, existing_colors, actual_new_colors)
    
    # Завершаем файл, если он был изменен
    if added and os.path.exists(DB_FILE):
        with open(DB_FILE, 'r+', encoding='utf-8') as f:
            content = f.read()
            if not content.endswith("}\n"):
                f.seek(0, os.SEEK_END)
                f.write("}\n")

if __name__ == "__main__":
    main()