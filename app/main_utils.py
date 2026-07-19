from typing import Any
from dataclasses import dataclass

from app.database.models import Habit


@dataclass
class LogStart:
    habit: Habit
    frequency: int
    period: str
    number_of_due: int

    def get_habit_log(self) -> list[Any]:
        return self.habit.logs

    def get_frequency(self) -> str:
        return self.habit.frequency_type

    def calculate_completed_log_for_seven_days(self):
        if self.get_frequency() == "daily":
            self.number_of_due = 7
        elif self.get_frequency() == "interval":
            self.number_of_due = self.habit.interval_days
        else:
            self.number_of_due = len(self.habit.day_of_week)
        complete_days = len(self.get_habit_log)

        return {
            "completed": complete_days,
            "due": self.number_of_due
        }










