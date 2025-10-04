import numpy as np
import re

def convert_spring_mathcha_to_tikz(mathcha_path):
    # Шаг 1: Извлечение всех точек из пути
    points = []
    pattern = r'\(([\d.]+),([\d.]+)\)'
    matches = re.findall(pattern, mathcha_path)
    for match in matches:
        x = float(match[0])
        y = float(match[1])
        points.append((x, y))
    
    if len(points) < 4:
        raise ValueError("Недостаточно точек для определения пружины")
    
    # Преобразование в массив NumPy
    points_arr = np.array(points)
    
    # Шаг 2: Вычисление PCA для определения главной оси
    centroid = np.mean(points_arr, axis=0)
    centered = points_arr - centroid
    
    # Ковариационная матрица
    cov = np.cov(centered.T)
    
    # Собственные значения и векторы
    eigenvalues, eigenvectors = np.linalg.eig(cov)
    
    # Главный вектор (с наибольшим собственным значением)
    main_axis = eigenvectors[:, np.argmax(eigenvalues)]
    
    # Шаг 3: Проецирование точек на главную ось
    projections = np.dot(centered, main_axis)
    min_proj = np.min(projections)
    max_proj = np.max(projections)
    
    # Начало и конец оси пружины
    start_point = centroid + min_proj * main_axis
    end_point = centroid + max_proj * main_axis
    
    # Шаг 4: Вычисление амплитуды
    # Перпендикулярный вектор
    perp_axis = np.array([-main_axis[1], main_axis[0]])
    amplitudes = np.abs(np.dot(centered, perp_axis))
    amplitude = np.max(amplitudes)
    
    # Шаг 5: Расчет параметров пружины
    # Длина оси
    axis_length = np.linalg.norm(end_point - start_point)
    
    # Количество кривых Безье
    n_curves = (len(points) - 1) // 3
    
    # Количество сегментов (1 виток = 2 кривым Безье)
    n_segments = n_curves
    segment_length = axis_length / n_segments if n_segments > 0 else 0
    
    # Шаг 6: Генерация TikZ-кода
    tikz_code = (
        f"\\draw[decoration={{\n"
        f"    coil,\n"
        f"    segment length={segment_length:.2f},\n"
        f"    amplitude={amplitude:.2f},\n"
        f"    aspect=0.5,\n"
        f"    pre length=0pt,\n"
        f"    post length=0pt\n"
        f"}}, decorate] ({start_point[0]:.2f},{start_point[1]:.2f}) -- ({end_point[0]:.2f},{end_point[1]:.2f});"
    )
    
    return tikz_code

# Пример использования
mathcha_example = r"""
\draw   (114.15,187.76) .. controls (112.59,185.77) and (111.62,183.15) .. (113.34,181.33) .. controls (116.77,177.69) and (124.05,184.55) .. (122.67,186) .. controls (121.3,187.46) and (114.02,180.6) .. (117.45,176.96) .. controls (120.88,173.32) and (128.16,180.18) .. (126.79,181.63) .. controls (125.42,183.09) and (118.14,176.23) .. (121.56,172.59) .. controls (124.99,168.95) and (132.27,175.81) .. (130.9,177.27) .. controls (129.53,178.72) and (122.25,171.87) .. (125.68,168.23) .. controls (129.11,164.59) and (136.39,171.44) .. (135.01,172.9) .. controls (133.64,174.35) and (126.36,167.5) .. (129.79,163.86) .. controls (133.22,160.22) and (140.5,167.07) .. (139.13,168.53) .. controls (137.76,169.99) and (130.48,163.13) .. (133.9,159.49) .. controls (137.33,155.85) and (144.61,162.7) .. (143.24,164.16) .. controls (141.87,165.62) and (134.59,158.76) .. (138.02,155.12) .. controls (141.45,151.48) and (148.73,158.34) .. (147.35,159.79) .. controls (145.98,161.25) and (138.7,154.39) .. (142.13,150.75) .. controls (145.56,147.11) and (152.84,153.97) .. (151.47,155.42) .. controls (150.1,156.88) and (142.82,150.03) .. (146.24,146.39) .. controls (149.67,142.75) and (156.95,149.6) .. (155.58,151.06) .. controls (154.21,152.51) and (146.93,145.66) .. (150.36,142.02) .. controls (153.79,138.38) and (161.07,145.23) .. (159.69,146.69) .. controls (158.32,148.14) and (151.04,141.29) .. (154.47,137.65) .. controls (157.9,134.01) and (165.18,140.86) .. (163.81,142.32) .. controls (162.44,143.78) and (155.16,136.92) .. (158.58,133.28) .. controls (162.01,129.64) and (169.29,136.5) .. (167.92,137.95) .. controls (166.55,139.41) and (159.27,132.55) .. (162.7,128.91) .. controls (166.13,125.27) and (173.41,132.13) .. (172.03,133.58) .. controls (170.66,135.04) and (163.38,128.18) .. (166.81,124.54) .. controls (170.24,120.9) and (177.52,127.76) .. (176.15,129.22) .. controls (174.78,130.67) and (167.5,123.82) .. (170.92,120.18) .. controls (171.42,119.65) and (172,119.34) .. (172.63,119.21) ;
"""

try:
    tikz_output = convert_spring_mathcha_to_tikz(mathcha_example)
    print("Сгенерированный TikZ-код:")
    print(tikz_output)
except ValueError as e:
    print(f"Ошибка: {e}")