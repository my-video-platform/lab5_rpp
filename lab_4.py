import os
import csv
from typing import List, Iterator, Optional, Any


class Record:
    """
    Класс, представляющий одну запись о входе/выходе.
    Реализует перегрузку __repr__ и контроль установки атрибутов через __setattr__.
    """

    def __init__(self, number: int, datetime: str, entry: bool, gender: str):
        # Используем __setattr__ для инициализации
        self.number = number
        self.datetime = datetime
        self.entry = entry
        self.gender = gender

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Переопределение __setattr__ для валидации значений свойств.
        """
        if name == "number":
            if not isinstance(value, int) or value <= 0:
                raise AttributeError("Номер должен быть положительным целым числом")
        elif name == "datetime":
            if not isinstance(value, str) or len(value.strip()) == 0:
                raise AttributeError("Дата и время должны быть непустой строкой")
            # Простейшая проверка формата (можно расширить)
            if " " not in value:
                raise AttributeError("Дата и время должны содержать пробел (ГГГГ-ММ-ДД ЧЧ:ММ)")
        elif name == "entry":
            if not isinstance(value, bool):
                raise AttributeError("Поле entry должно быть булевым значением")
        elif name == "gender":
            if value not in ("муж", "жен"):
                raise AttributeError("Пол должен быть 'муж' или 'жен'")
        # Вызов родительского метода для фактической установки атрибута
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        """Перегрузка repr для удобного вывода записи."""
        entry_str = "вход" if self.entry else "выход"
        return f"Record(№{self.number}, {self.datetime}, {entry_str}, {self.gender})"

    def to_dict(self) -> dict:
        """Преобразует запись в словарь для сохранения в CSV."""
        return {
            '№': self.number,
            'datetime': self.datetime,
            'entry': self.entry,
            'gender': self.gender
        }


class NamedRecord(Record):
    """
    Дочерний класс, добавляющий поле name.
    Демонстрирует наследование, переопределение __setattr__ и __repr__.
    """

    def __init__(self, number: int, datetime: str, entry: bool, gender: str, name: str):
        super().__init__(number, datetime, entry, gender)
        self.name = name

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "name":
            if not isinstance(value, str) or len(value.strip()) == 0:
                raise AttributeError("Имя не может быть пустым")
        # Для остальных полей вызываем родительскую валидацию
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        entry_str = "вход" if self.entry else "выход"
        return (f"NamedRecord(№{self.number}, {self.datetime}, {entry_str}, "
                f"{self.gender}, имя='{self.name}')")


class RecordCollection:
    """
    Класс-контейнер для коллекции записей.
    Реализует:
        - итератор (через внутренний класс Iterator)
        - доступ по индексу (__getitem__)
        - статические методы для работы с CSV
        - генераторы для фильтрации
    """

    # ---------- Внутренний класс итератора ----------
    class Iterator:
        """Итератор для RecordCollection."""
        def __init__(self, records: List[Record]):
            self._records = records
            self._index = 0

        def __iter__(self):
            return self

        def __next__(self) -> Record:
            if self._index < len(self._records):
                result = self._records[self._index]
                self._index += 1
                return result
            raise StopIteration

    # ---------- Основные методы коллекции ----------
    def __init__(self, records: Optional[List[Record]] = None):
        self._records = records if records is not None else []

    def __iter__(self) -> Iterator:
        """Возвращает итератор."""
        return RecordCollection.Iterator(self._records)

    def __getitem__(self, index: int) -> Record:
        """Доступ к записи по индексу."""
        return self._records[index]

    def __len__(self) -> int:
        return len(self._records)

    def __repr__(self) -> str:
        return f"RecordCollection({len(self._records)} записей)"

    def add_record(self, record: Record) -> None:
        """Добавляет запись в коллекцию."""
        self._records.append(record)

    # ---------- Генераторы ----------
    def filter_by_entry(self, entry_flag: bool = True) -> Iterator[Record]:
        """Генератор, возвращающий записи с заданным признаком входа."""
        for rec in self._records:
            if rec.entry == entry_flag:
                yield rec

    def filter_by_gender(self, gender: str) -> Iterator[Record]:
        """Генератор, возвращающий записи с заданным полом."""
        for rec in self._records:
            if rec.gender == gender:
                yield rec

    # ---------- Методы сортировки (возвращают новые коллекции) ----------
    def sort_by_number(self) -> 'RecordCollection':
        """Возвращает новую коллекцию, отсортированную по номеру."""
        sorted_records = sorted(self._records, key=lambda r: r.number)
        return RecordCollection(sorted_records)

    def sort_by_gender(self) -> 'RecordCollection':
        """Возвращает новую коллекцию, отсортированную по полу."""
        sorted_records = sorted(self._records, key=lambda r: r.gender)
        return RecordCollection(sorted_records)

    # ---------- Статические методы для работы с CSV ----------
    @staticmethod
    def load_from_csv(filepath: str) -> 'RecordCollection':
        """
        Статический метод: читает CSV-файл и возвращает RecordCollection.
        """
        records = []
        try:
            with open(filepath, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    number = int(row['№'])
                    dt = row['datetime']
                    # Преобразование entry в bool
                    val = row['entry'].strip().lower()
                    entry = val in ('true', '1', 'yes')
                    gender = row['gender'].strip().lower()
                    # Создаём объект Record
                    rec = Record(number, dt, entry, gender)
                    records.append(rec)
        except FileNotFoundError:
            print(f"Файл '{filepath}' не найден. Создана пустая коллекция.")
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
        return RecordCollection(records)

    @staticmethod
    def save_to_csv(filepath: str, collection: 'RecordCollection') -> None:
        """
        Статический метод: сохраняет коллекцию в CSV-файл.
        """
        headers = ['№', 'datetime', 'entry', 'gender']
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for rec in collection:
                    writer.writerow(rec.to_dict())
            print(f"Данные сохранены в {filepath}")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")


# ---------- Вспомогательные функции (из лабораторной №3) ----------
def count_files_in_dir(directory: str) -> int:
    """Подсчитывает количество файлов в указанной директории."""
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


def input_new_record() -> Record:
    """Запрашивает у пользователя данные и возвращает объект Record."""
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
    if gender not in ('муж', 'жен'):
        gender = 'неизвестно'
    return Record(num, dt, entry, gender)


def print_collection(collection: RecordCollection, caption: str):
    """Удобный вывод коллекции записей."""
    print(f"\n--- {caption} ---")
    if len(collection) == 0:
        print("(нет данных)")
        return
    print(f"{'№':<5} {'Дата и время':<20} {'Вход/Выход':<12} {'Пол'}")
    for rec in collection:
        entry_str = "вход" if rec.entry else "выход"
        print(f"{rec.number:<5} {rec.datetime:<20} {entry_str:<12} {rec.gender}")


def main():
    # 1. Подсчёт файлов в папке
    folder = input("Введите путь к папке для подсчёта файлов: ").strip()
    if folder:
        cnt = count_files_in_dir(folder)
        if cnt >= 0:
            print(f"Количество файлов в папке '{folder}': {cnt}")

    # 2. Загрузка данных из CSV
    csv_file = "data.csv"
    collection = RecordCollection.load_from_csv(csv_file)

    # 3. Демонстрация __getitem__ и итератора
    print("\n--- Демонстрация __getitem__ ---")
    if len(collection) > 0:
        print(f"Первый элемент коллекции: {collection[0]}")

    print("\n--- Демонстрация итератора (проход по всем записям) ---")
    for i, rec in enumerate(collection):
        print(f"{i+1}: {rec}")

    # 4. Вывод исходных данных (через вспомогательную функцию)
    print_collection(collection, "Исходные данные")

    # 5. Сортировка по полу и по номеру
    sorted_by_gender = collection.sort_by_gender()
    print_collection(sorted_by_gender, "Сортировка по полу (строка)")

    sorted_by_number = collection.sort_by_number()
    print_collection(sorted_by_number, "Сортировка по номеру (число)")

    # 6. Фильтрация с помощью генераторов
    entered_gen = collection.filter_by_entry(True)
    entered_list = list(entered_gen)  # преобразуем генератор в список для вывода
    entered_collection = RecordCollection(entered_list)
    print_collection(entered_collection, "Посетители, которые вошли (entry = True)")

    # 7. Демонстрация работы с дочерним классом NamedRecord
    print("\n--- Демонстрация наследования (NamedRecord) ---")
    named_rec = NamedRecord(99, "2025-04-24 12:00", True, "муж", "Иван Петров")
    print(f"Создан объект NamedRecord: {named_rec}")
    collection.add_record(named_rec)
    print("Запись с именем добавлена в коллекцию.")
    print_collection(collection, "Коллекция после добавления NamedRecord")

    # 8. Добавление новой записи через пользовательский ввод
    choice = input("\nХотите добавить новую запись? (да/нет): ").strip().lower()
    if choice in ('да', 'yes', 'y'):
        new_rec = input_new_record()
        collection.add_record(new_rec)
        # Сохраняем обновлённую коллекцию в CSV
        RecordCollection.save_to_csv(csv_file, collection)
        print_collection(collection, "Обновлённые данные после добавления")

    # 9. Дополнительная демонстрация генератора по полу
    print("\n--- Генератор filter_by_gender (женщины) ---")
    women_gen = collection.filter_by_gender("жен")
    for rec in women_gen:
        print(rec)


if __name__ == "__main__":
    main()


# новый комент для 5 лабы # создал новую ветку feature-1
