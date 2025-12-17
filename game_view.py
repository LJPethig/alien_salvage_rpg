# game_view.py
import arcade
from datetime import datetime, timedelta
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TEXT_COLOR, BACKGROUND_COLOR,
    MARGIN_X, FONT_NAME_PRIMARY, FONT_SIZE_DEFAULT
)

class GameView(arcade.View):
    def __init__(self, terminals_dict):
        super().__init__()
        self.terminals = terminals_dict

        # === Background as SpriteList (required in modern Arcade) ===
        self.background_list = arcade.SpriteList()

        try:
            background_sprite = arcade.Sprite("resources/images/corridor.png")
            background_sprite.center_x = SCREEN_WIDTH // 2
            background_sprite.center_y = SCREEN_HEIGHT // 2 + 100  # Shift up to leave bottom space

            # Scale to fit ~90% width, preserve aspect
            scale = (SCREEN_WIDTH * 0.9) / background_sprite.width
            background_sprite.scale = scale

            # Cap height to ~70% of screen
            if background_sprite.height * scale > SCREEN_HEIGHT * 0.7:
                scale = (SCREEN_HEIGHT * 0.7) / background_sprite.height
                background_sprite.scale = scale

            self.background_list.append(background_sprite)
        except Exception as e:
            print(f"Background load failed: {e}")

        # === MISSION TIME ===
        real_now = datetime(2025, 12, 16)
        self.mission_start_time = real_now + timedelta(days=365.25 * 150)
        self.elapsed_seconds = 0.0

        # Text state
        self.description_lines = [
            "You stand in a dimly lit corridor aboard the salvage vessel.",
            "Cold condensation drips from overhead pipes.",
            "The air recyclers hum faintly.",
            "A heavy bulkhead door ahead is marked 'MOTHER ACCESS'.",
            "",
            "> "
        ]
        self.current_input = ""
        self.response_lines = []

    def get_timestamp(self) -> str:
        current = self.mission_start_time + timedelta(seconds=self.elapsed_seconds)
        earth_date = current.strftime("%d %b %Y").upper()
        ship_time = current.strftime("%H:%M:%S")
        return f"{earth_date}  SHIP TIME: {ship_time}"

    def advance_time(self, seconds: float):
        self.elapsed_seconds += seconds

    def on_update(self, delta_time: float):
        self.elapsed_seconds += delta_time

    def on_draw(self):
        self.clear()
        arcade.set_background_color(BACKGROUND_COLOR)

        # Draw background (via SpriteList)
        self.background_list.draw()

        # Text area at bottom
        base_y = 60
        line_height = 28

        # Description
        for i, line in enumerate(self.description_lines[:-1]):
            arcade.draw_text(
                line,
                MARGIN_X,
                base_y + i * line_height,
                TEXT_COLOR,
                font_size=FONT_SIZE_DEFAULT,
                font_name=FONT_NAME_PRIMARY
            )

        # Responses
        response_y = base_y + len(self.description_lines[:-1]) * line_height + 20
        for i, line in enumerate(self.response_lines):
            arcade.draw_text(
                line,
                MARGIN_X,
                response_y + i * line_height,
                TEXT_COLOR,
                font_size=FONT_SIZE_DEFAULT,
                font_name=FONT_NAME_PRIMARY
            )

        # Input prompt
        prompt_y = response_y + len(self.response_lines) * line_height + 40
        prompt_text = self.description_lines[-1] + self.current_input + "█"

        arcade.draw_text(
            prompt_text,
            MARGIN_X,
            prompt_y,
            TEXT_COLOR,
            font_size=FONT_SIZE_DEFAULT + 4,
            font_name=FONT_NAME_PRIMARY
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
            return

        if key == arcade.key.ENTER:
            command = self.current_input.strip().lower()
            self.response_lines = self.process_command(command)
            self.current_input = ""

        elif key == arcade.key.BACKSPACE:
            self.current_input = self.current_input[:-1]

        elif 32 <= key <= 126:
            self.current_input += chr(key)

    def process_command(self, command):
        if command in ["access mother", "use mother", "mother", "use terminal", "enter mother"]:
            if "mother" in self.terminals:
                mother_term = self.terminals["mother"]
                mother_term.game_view = self  # Connect timestamp
                mother_term.previous_view = self
                self.window.show_view(mother_term)
                return ["Accessing MOTHER core interface..."]
            return ["Terminal not available."]

        if command in ["look", "l"]:
            return ["Dark corridor. MOTHER access ahead."]

        if command == "help":
            return ["look, access mother, help"]

        if command == "":
            return []

        return [f"Unknown command: {command}"]