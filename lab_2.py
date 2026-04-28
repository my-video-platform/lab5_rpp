import numpy as np

def generate_matrix(n: int, m: int) -> np.ndarray:
    """
    Генерирует прямоугольную матрицу случайных чисел размера n вx m.
    Используется равномерное распределение на интервале [0, 10).
    
    Параметры:
        n (int): количество строк
        m (int): количество столбцов
        
    Возвращает:
        np.ndarray: сгенерированная матрица
    """
    matrix = np.random.uniform(0, 10, (n, m))
    matrix = np.round(matrix, 2)
    return matrix

def normalize_columns(matrix: np.ndarray) -> np.ndarray:
    """
    Нормализует каждый столбец матрицы, деля все его элементы на максимальный элемент столбца.
    Если максимальный элемент столбца равен нулю, столбец остается без изменений,
    и выводится предупреждение.
    
    Параметры:
        matrix (np.ndarray): исходная матрица
        
    Возвращает:
        np.ndarray: новая матрица с нормализованными столбцами
    """
    normalized = matrix.copy()
    max_vals = np.max(normalized, axis=0)
    
    for j in range(normalized.shape[1]):
        if max_vals[j] != 0:
            # Деление столбца на его максимум
            normalized[:, j] /= max_vals[j]
        else:
            print(f"Предупреждение: столбец {j} содержит только нули, деление пропущено.")
    
    return normalized

def save_to_file(filename: str, original: np.ndarray, processed: np.ndarray) -> None:
    """
    Сохраняет исходную и обработанную матрицы в текстовый файл.
    
    Параметры:
        filename (str): имя файла для сохранения
        original (np.ndarray): исходная матрица
        processed (np.ndarray): обработанная матрица
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Исходная матрица:\n")
        f.write(str(original))
        f.write("\n\nОбработанная матрица (деление каждого столбца на его максимум):\n")
        f.write(str(processed))
        f.write("\n")

def main() -> None:
    """
    Основная функция программы:
    - запрашивает размеры матрицы у пользователя
    - генерирует матрицу
    - выполняет нормализацию по столбцам
    - сохраняет результаты в файл
    """
    try:
        n = int(input("Введите количество строк N: "))
        m = int(input("Введите количество столбцов M: "))
        
        if n <= 0 or m <= 0:
            print("Размеры матрицы должны быть положительными числами.")
            return
        
        # Генерация исходной матрицы
        original_matrix = generate_matrix(n, m)
        print("Сгенерирована исходная матрица:\n", original_matrix)
        
        processed_matrix = normalize_columns(original_matrix)
        print("Обработанная матрица:\n", processed_matrix)

        filename = "result.txt"
        save_to_file(filename, original_matrix, processed_matrix)
        print(f"Результаты сохранены в файл '{filename}'.")
        
    except ValueError:
        print("Ошибка ввода: необходимо ввести целые числа.")

if __name__ == "__main__":
    main()