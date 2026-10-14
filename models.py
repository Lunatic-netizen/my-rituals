from abc import ABC, abstractmethod
from datetime import date, timedelta


class BaseEntity(ABC):
    @abstractmethod
    def get_info(self):
        pass


class Habit(BaseEntity):
    def __init__(self, name: str, emoji: str, goal: int):
        self._name = name
        self._emoji = emoji
        self._goal = goal
        self._done_dates = []

    @property
    def name(self):
        return self._name

    @property
    def emoji(self):
        return self._emoji

    @property
    def goal(self):
        return self._goal

    @property
    def done_dates(self):
        return self._done_dates

    @name.setter
    def name(self, value):
        self._name = value

    @goal.setter
    def goal(self, value):
        self._goal = value

    def mark_done_today(self):
        today = date.today()
        if today not in self._done_dates:
            self._done_dates.append(today)
            self._done_dates.sort()

    def unmark_done_today(self):
        today = date.today()
        if today in self._done_dates:
            self._done_dates.remove(today)

    def is_done_today(self):
        return date.today() in self._done_dates

    def current_streak(self):
        if not self._done_dates:
            return 0
        streak = 0
        check_day = date.today()
        while check_day in self._done_dates:
            streak += 1
            check_day -= timedelta(days=1)
        return streak

    def total_done(self):
        return len(self._done_dates)

    def __str__(self):
        return f"{self._emoji} {self._name} — серия: {self.current_streak()}/{self._goal}"

    def __repr__(self):
        return f"Habit(name='{self._name}', goal={self._goal}, done={self.total_done()})"

    def __eq__(self, other):
        if not isinstance(other, Habit):
            return False
        return self._name == other._name

    def get_info(self):
        return str(self)


class HabitTracker(BaseEntity):
    def __init__(self):
        self._habits = []

    @property
    def habits(self):
        return self._habits

    def add_habit(self, habit):
        self._habits.append(habit)

    def remove_habit(self, habit):
        if habit in self._habits:
            self._habits.remove(habit)

    def total_habits(self):
        return len(self._habits)

    def done_today_count(self):
        return sum(1 for h in self._habits if h.is_done_today())

    def best_streak(self):
        if not self._habits:
            return 0
        return max(h.current_streak() for h in self._habits)

    def __str__(self):
        return f"Трекер: {self.total_habits()} привычек"

    def __repr__(self):
        return f"HabitTracker(habits={len(self._habits)})"

    def __eq__(self, other):
        if not isinstance(other, HabitTracker):
            return False
        return self._habits == other._habits

    def get_info(self):
        return str(self)
