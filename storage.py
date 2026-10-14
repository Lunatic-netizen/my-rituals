import os
from datetime import datetime
from models import Habit, HabitTracker


def _habits_file(user_name):
    return f"habits_{user_name}.txt"


def _report_file(user_name):
    return f"report_{user_name}.txt"


def save_all(tracker, user_name):
    """Сохраняет привычки конкретного пользователя."""
    filename = _habits_file(user_name)
    with open(filename, "w", encoding="utf-8") as f:
        for h in tracker.habits:
            dates_str = ",".join(d.strftime("%Y-%m-%d") for d in h.done_dates)
            f.write(f"{h.name}|{h.emoji}|{h.goal}|{dates_str}\n")


def load_all(user_name):
    """Загружает привычки конкретного пользователя. Если файла нет — отдаёт пустой трекер."""
    tracker = HabitTracker()
    filename = _habits_file(user_name)
    if not os.path.exists(filename):
        return tracker
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) < 4:
                continue
            name = parts[0]
            emoji = parts[1]
            goal = int(parts[2])
            dates_str = parts[3]
            h = Habit(name, emoji, goal)
            if dates_str:
                for d_str in dates_str.split(","):
                    h.done_dates.append(datetime.strptime(d_str, "%Y-%m-%d").date())
            tracker.add_habit(h)
    return tracker


def save_user_name(name, filename="user.txt"):
    """Сохраняет имя последнего пользователя."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(name)


def load_user_name(filename="user.txt"):
    """Загружает имя последнего пользователя, если сохранено."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_report(tracker, user_name):
    """Отчёт для конкретного пользователя."""
    filename = _report_file(user_name)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("+----------------------+---------------------+---------------------+\n")
        f.write("|        login         |       time_in       |      time_out       |\n")
        f.write("|----------------------|---------------------|---------------------|\n")
        for h in tracker.habits:
            login = user_name[:20].ljust(20)
            time_in = "—".ljust(19)
            time_out = "—".ljust(19)
            if h.done_dates:
                time_in = h.done_dates[0].strftime("%d.%m.%Y %H:%M:%S").ljust(19)
                time_out = h.done_dates[-1].strftime("%d.%m.%Y %H:%M:%S").ljust(19)
            f.write(f"| {login} | {time_in} | {time_out} |\n")
        f.write("+----------------------+---------------------+---------------------+\n")


def create_test_tracker():
    tracker = HabitTracker()
    habits = [
        Habit("Пить воду", "💧", 30),
        Habit("Читать книгу", "📚", 14),
        Habit("Зарядка", "🏃‍♀️", 21),
        Habit("Медитация", "🧘‍♀️", 10),
        Habit("Английский", "🇬🇧", 60),
        Habit("Без сладкого", "🍬", 7),
        Habit("Прогулка", "🚶‍♀️", 30),
        Habit("Рано вставать", "🌅", 21),
        Habit("Дневник", "📓", 30),
        Habit("Рисование", "🎨", 14),
    ]
    for h in habits:
        tracker.add_habit(h)
    return tracker
