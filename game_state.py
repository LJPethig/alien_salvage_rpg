# game_state.py
from datetime import datetime, timedelta

class GameState:
    def __init__(self):
        # Base date: today (December 17, 2025)
        real_now = datetime(2025, 12, 17)
        # Mission is ~150 years in the future
        self.mission_start_time = real_now + timedelta(days=365.25 * 150)
        self.elapsed_seconds = 0.0

    def get_timestamp(self) -> str:
        current = self.mission_start_time + timedelta(seconds=self.elapsed_seconds)
        earth_date = current.strftime("%d %b %Y").upper()
        ship_time = current.strftime("%H:%M:%S")
        return f"{earth_date}  SHIP TIME: {ship_time}"

    def update_time(self, delta_time: float):
        self.elapsed_seconds += delta_time