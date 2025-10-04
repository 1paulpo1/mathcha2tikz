import numpy as np
import re

def convert_wave_mathcha_to_tikz(mathcha_path):
    # Шаг 1: Извлечение всех точек из пути
    points = []
    pattern = r'\(([\d.]+),([\d.]+)\)'
    matches = re.findall(pattern, mathcha_path)
    for match in matches:
        x = float(match[0])
        y = float(match[1])
        points.append((x, y))
    
    if len(points) < 4:
        raise ValueError("Недостаточно точек для определения волны")
    
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
    
    # Начало и конец оси волны
    start_point = centroid + min_proj * main_axis
    end_point = centroid + max_proj * main_axis
    
    # Шаг 4: Вычисление амплитуды
    # Перпендикулярный вектор
    perp_axis = np.array([-main_axis[1], main_axis[0]])
    amplitudes = np.abs(np.dot(centered, perp_axis))
    amplitude = np.max(amplitudes) 
    
    # Шаг 5: Расчет параметров волны
    # Длина оси
    axis_length = np.linalg.norm(end_point - start_point)
    
    # Количество кривых Безье
    n_curves = (len(points) - 1) // 3
    
    # Длина сегмента (в пикселях)
    # Для волны каждый "период" состоит из двух кривых Безье
    # Поэтому длина сегмента = общая длина оси / количество кривых
    segment_length = axis_length / n_curves * 2
    
    # Шаг 6: Генерация TikZ-кода для wave
    tikz_code = (
        f"\\draw[decoration={{\n"
        f"    snake,\n"
        f"    segment length={segment_length:.2f},\n"
        f"    amplitude={amplitude:.2f},\n"
        f"    aspect=0.5,\n"
        f"    pre length=0pt,\n"
        f"    post length=0pt\n"
        f"}}, decorate] ({start_point[0]:.2f},{start_point[1]:.2f}) -- ({end_point[0]:.2f},{end_point[1]:.2f});"
    )
    
    return tikz_code

# Пример использования
wave_example = r"""
\draw   (50,105) .. controls (50.82,107.56) and (51.6,110) .. (52.5,110) .. controls (53.4,110) and (54.18,107.56) .. (55,105) .. controls (55.82,102.44) and (56.6,100) .. (57.5,100) .. controls (58.4,100) and (59.18,102.44) .. (60,105) .. controls (60.82,107.56) and (61.6,110) .. (62.5,110) .. controls (63.4,110) and (64.18,107.56) .. (65,105) .. controls (65.82,102.44) and (66.6,100) .. (67.5,100) .. controls (68.4,100) and (69.18,102.44) .. (70,105) .. controls (70.82,107.56) and (71.6,110) .. (72.5,110) .. controls (73.4,110) and (74.18,107.56) .. (75,105) .. controls (75.82,102.44) and (76.6,100) .. (77.5,100) .. controls (78.4,100) and (79.18,102.44) .. (80,105) .. controls (80.82,107.56) and (81.6,110) .. (82.5,110) .. controls (83.4,110) and (84.18,107.56) .. (85,105) .. controls (85.82,102.44) and (86.6,100) .. (87.5,100) .. controls (88.4,100) and (89.18,102.44) .. (90,105) .. controls (90.82,107.56) and (91.6,110) .. (92.5,110) .. controls (93.4,110) and (94.18,107.56) .. (95,105) .. controls (95.82,102.44) and (96.6,100) .. (97.5,100) .. controls (98.4,100) and (99.18,102.44) .. (100,105) .. controls (100.82,107.56) and (101.6,110) .. (102.5,110) .. controls (103.4,110) and (104.18,107.56) .. (105,105) .. controls (105.82,102.44) and (106.6,100) .. (107.5,100) .. controls (108.4,100) and (109.18,102.44) .. (110,105) .. controls (110.82,107.56) and (111.6,110) .. (112.5,110) .. controls (113.4,110) and (114.18,107.56) .. (115,105) .. controls (115.82,102.44) and (116.6,100) .. (117.5,100) .. controls (118.4,100) and (119.18,102.44) .. (120,105) .. controls (120.82,107.56) and (121.6,110) .. (122.5,110) .. controls (123.4,110) and (124.18,107.56) .. (125,105) .. controls (125.82,102.44) and (126.6,100) .. (127.5,100) .. controls (128.4,100) and (129.18,102.44) .. (130,105) .. controls (130.82,107.56) and (131.6,110) .. (132.5,110) .. controls (133.4,110) and (134.18,107.56) .. (135,105) .. controls (135.82,102.44) and (136.6,100) .. (137.5,100) .. controls (138.4,100) and (139.18,102.44) .. (140,105) .. controls (140.82,107.56) and (141.6,110) .. (142.5,110) .. controls (143.4,110) and (144.18,107.56) .. (145,105) .. controls (145.82,102.44) and (146.6,100) .. (147.5,100) .. controls (148.4,100) and (149.18,102.44) .. (150,105) .. controls (150.82,107.56) and (151.6,110) .. (152.5,110) .. controls (153.4,110) and (154.18,107.56) .. (155,105) .. controls (155.82,102.44) and (156.6,100) .. (157.5,100) .. controls (158.4,100) and (159.18,102.44) .. (160,105) .. controls (160.82,107.56) and (161.6,110) .. (162.5,110) .. controls (163.4,110) and (164.18,107.56) .. (165,105) .. controls (165.82,102.44) and (166.6,100) .. (167.5,100) .. controls (168.4,100) and (169.18,102.44) .. (170,105) .. controls (170.82,107.56) and (171.6,110) .. (172.5,110) .. controls (173.4,110) and (174.18,107.56) .. (175,105) .. controls (175.82,102.44) and (176.6,100) .. (177.5,100) .. controls (178.4,100) and (179.18,102.44) .. (180,105) .. controls (180.82,107.56) and (181.6,110) .. (182.5,110) .. controls (183.4,110) and (184.18,107.56) .. (185,105) .. controls (185.82,102.44) and (186.6,100) .. (187.5,100) .. controls (188.4,100) and (189.18,102.44) .. (190,105) .. controls (190.82,107.56) and (191.6,110) .. (192.5,110) .. controls (193.4,110) and (194.18,107.56) .. (195,105) .. controls (195.82,102.44) and (196.6,100) .. (197.5,100) .. controls (198.4,100) and (199.18,102.44) .. (200,105) ;
"""

try:
    tikz_wave_output = convert_wave_mathcha_to_tikz(wave_example)
    print("Сгенерированный TikZ-код для wave:")
    print(tikz_wave_output)
except ValueError as e:
    print(f"Ошибка: {e}")