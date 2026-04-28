import os
import csv
from pathlib import Path

def count_files_in_dir(directory: str) -> int:
    """
    Подсчитывает количество именно файлов (не подпапок) в указанной директории.
    """
    try:
        entries = os.listdir(directory)
        files = [f for f in entries if os.path.isfile(os.path.join(directory, f))]
        return len(files)
    except FileNotFoundError:
        print(f"Ошибка: папка '{directory}' не найдена.")
        return -1
    except PermissionError:
        print(f"Ошибка: нет доступа к папке '{directory}'.")
        return -1

def read_data(filepath: str) -> list[dict]:
    """
    Читает CSV-файл и возвращает список словарей.
    Поле entry преобразуется в bool (True/False).
    Поле № -> int.
    """
    data = []
    try:
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['№'] = int(row['№'])
                val = row['entry'].strip().lower()
                if val in ('true', '1', 'yes'):
                    row['entry'] = True
                else:
                    row['entry'] = False
                data.append(row)
    except FileNotFoundError:
        print(f"Файл '{filepath}' не найден. Будет использован пустой список.")
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
    return data

def print_data(data: list[dict], caption: str):
    """Вспомогательная функция для красивого вывода списка записей."""
    print(f"\n--- {caption} ---")
    if not data:
        print("(нет данных)")
        return
    print(f"{'№':<5} {'Дата и время':<20} {'Вход/Выход':<12} {'Пол'}")
    for rec in data:
        entry_str = "вход" if rec['entry'] else "выход"
        print(f"{rec['№']:<5} {rec['datetime']:<20} {entry_str:<12} {rec['gender']}")

def sort_by_gender(data: list[dict]) -> list[dict]:
    return sorted(data, key=lambda x: x['gender'])

def sort_by_number(data: list[dict]) -> list[dict]:
    return sorted(data, key=lambda x: x['№'])

def filter_by_entry(data: list[dict], entry_flag: bool = True) -> list[dict]:
    return [rec for rec in data if rec['entry'] == entry_flag]

def save_new_record(filepath: str, record: dict):
    """
    Добавляет одну новую запись в CSV-файл.
    Если файла нет, создаст с заголовками.
    """
    headers = ['№', 'datetime', 'entry', 'gender']
    file_exists = os.path.isfile(filepath)
    try:
        with open(filepath, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)
        print("Запись успешно сохранена.")
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")

def input_new_record() -> dict:
    """Запрашивает у пользователя данные для новой записи."""
    print("\nДобавление новой записи:")
    while True:
        try:
            num = int(input("Введите номер (№): "))
            break
        except ValueError:
            print("Номер должен быть целым числом.")
    dt = input("Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ): ")
    entry_input = input("Признак входа (вход/выход): ").strip().lower()
    entry = entry_input in ('вход', 'true', '1', 'yes')
    gender = input("Пол (муж/жен): ").strip().lower()
    # Нормализуем пол
    if gender not in ('муж', 'жен'):
        gender = 'неизвестно'
    return {
        '№': num,
        'datetime': dt,
        'entry': entry,
        'gender': gender
    }

def main():
    folder = input("Введите путь к папке для подсчёта файлов: ").strip()
    if folder:
        cnt = count_files_in_dir(folder)
        if cnt >= 0:
            print(f"Количество файлов в папке '{folder}': {cnt}")

    csv_file = "data.csv"
    data = read_data(csv_file)

    print_data(data, "Исходные данные")

    sorted_by_gender = sort_by_gender(data)
    print_data(sorted_by_gender, "Сортировка по полу (строка)")

    sorted_by_num = sort_by_number(data)
    print_data(sorted_by_num, "Сортировка по номеру (число)")

    entered = filter_by_entry(data, True)
    print_data(entered, "Посетители, которые вошли (entry = True)")

    choice = input("\nХотите добавить новую запись? (да/нет): ").strip().lower()
    if choice in ('да', 'yes', 'y'):
        new_rec = input_new_record()
        save_new_record(csv_file, new_rec)
        data = read_data(csv_file)
        print_data(data, "Обновлённые данные после добавления")

if __name__ == "__main__":
    main()