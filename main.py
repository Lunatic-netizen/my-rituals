import flet as ft
import os
from models import Habit
from storage import (
    save_all, load_all, save_report, create_test_tracker,
    save_user_name, load_user_name,
)


def main(page: ft.Page):
    page.title = "Мои ритуалы"
    page.window_width = 600
    page.window_height = 750
    page.bgcolor = "#F5F5F7"
    page.padding = 20

    user_name = load_user_name()

    # Трекер создаём пустым — заполним после входа
    tracker = create_test_tracker()

    # ---- Поля для добавления привычки ----
    name_input = ft.TextField(label="Название привычки", expand=True)
    emoji_input = ft.TextField(label="Эмодзи", value="⭐", width=100)
    goal_input = ft.TextField(label="Цель (дней)", value="30", width=120)

    habits_column = ft.Column(spacing=8)

    def refresh_habits():
        habits_column.controls.clear()
        habits_column.controls.append(
            ft.Text(
                f"Всего: {tracker.total_habits()}  |  "
                f"Выполнено сегодня: {tracker.done_today_count()}  |  "
                f"Лучшая серия: {tracker.best_streak()}",
                size=13, color="grey",
            )
        )
        habits_column.controls.append(ft.Divider())

        for habit in tracker.habits:
            def make_toggle(h):
                def toggle(e):
                    if h.is_done_today():
                        h.unmark_done_today()
                    else:
                        h.mark_done_today()
                    save_all(tracker, user_name)
                    save_report(tracker, user_name)
                    refresh_habits()
                    page.update()
                return toggle

            def make_delete(h):
                def delete(e):
                    tracker.remove_habit(h)
                    save_all(tracker, user_name)
                    save_report(tracker, user_name)
                    refresh_habits()
                    page.update()
                return delete

            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CHECK_CIRCLE if habit.is_done_today()
                                 else ft.Icons.RADIO_BUTTON_UNCHECKED,
                            icon_color="green" if habit.is_done_today() else "grey",
                            on_click=make_toggle(habit),
                        ),
                        ft.Text(habit.emoji, size=22),
                        ft.Column(
                            controls=[
                                ft.Text(habit.name, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Серия: {habit.current_streak()} / {habit.goal}",
                                        size=12, color="grey"),
                            ],
                            spacing=2, expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color="red",
                            on_click=make_delete(habit),
                        ),
                    ],
                    spacing=8,
                ),
                padding=8, bgcolor="white", border_radius=12,
            )
            habits_column.controls.append(card)
        page.update()

    def logout_click(e):
        page.controls.clear()
        name_field.value = user_name
        page.add(login_screen)
        page.update()

    def show_main_screen():
        header = ft.Row(
            controls=[
                ft.Text("🌿 Мои ритуалы", size=24, weight=ft.FontWeight.BOLD, expand=True),
                ft.Text(f"👤 {user_name}", size=14, color="grey"),
                ft.TextButton("Выйти", on_click=logout_click),
            ],
        )
        page.scroll = ft.ScrollMode.AUTO
        page.add(header, add_panel, habits_column)
        refresh_habits()

    def add_habit_click(e):
        name = name_input.value.strip()
        emoji = emoji_input.value.strip() or "⭐"
        try:
            goal = int(goal_input.value)
        except ValueError:
            goal = 30
        if name:
            tracker.add_habit(Habit(name, emoji, goal))
            name_input.value = ""
            save_all(tracker, user_name)
            refresh_habits()

    add_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("➕ Добавить привычку", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(controls=[name_input, emoji_input, goal_input], spacing=8),
                ft.FilledButton("Добавить", on_click=add_habit_click),
            ],
            spacing=8,
        ),
        padding=15, bgcolor="white", border_radius=12,
    )
    # ЭКРАН АВТОРИЗАЦИИ
    name_field = ft.TextField(
        label="Как тебя зовут?",
        hint_text="Например: Иван",
        value=user_name,
        width=300,
    )

    def login_click(e):
        nonlocal user_name, tracker
        entered = name_field.value.strip()
        if not entered:
            name_field.error_text = "Введи имя"
            page.update()
            return
        user_name = entered
        save_user_name(user_name)

        # Загружаем привычки ИМЕННО этого пользователя
        loaded = load_all(user_name)
        if loaded.total_habits() == 0:
            # У нового пользователя нет файла — даём стартовые 10 привычек
            tracker = create_test_tracker()
            save_all(tracker, user_name)
        else:
            tracker = loaded

        page.controls.clear()
        show_main_screen()
        page.update()

    def reset_all(e):
        """Полный сброс: удаляем все файлы всех пользователей и перезапускаем."""
        for fname in os.listdir("."):
            if fname.startswith("habits_") or fname.startswith("report_") or fname == "user.txt":
                try:
                    os.remove(fname)
                except Exception:
                    pass

        nonlocal user_name, tracker
        user_name = ""
        tracker = create_test_tracker()
        page.controls.clear()
        name_field.value = ""
        name_field.error_text = None
        page.add(login_screen)
        page.update()

    login_screen = ft.Column(
        controls=[
            ft.Text("🌿 Мои ритуалы", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Войди, чтобы начать", size=14, color="grey"),
            ft.Container(height=20),
            name_field,
            ft.Container(height=10),
            ft.FilledButton("Войти", on_click=login_click, width=300),
            ft.Container(height=20),
            ft.TextButton("🔄 Начать заново", on_click=reset_all),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )
    # СТАРТ
    if user_name:
        # Если имя уже сохранялось — грузим его привычки
        loaded = load_all(user_name)
        if loaded.total_habits() == 0:
            tracker = create_test_tracker()
            save_all(tracker, user_name)
        else:
            tracker = loaded
        show_main_screen()
    else:
        page.add(login_screen)


if __name__ == "__main__":
    ft.run(main)
