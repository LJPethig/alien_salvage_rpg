# main.py
import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

from utils import build_terminal
from terminal.terminal_view import Terminal

# New imports
from locations import SHIP_LOCATIONS, Location
from game_state import GameState

# Your existing terminal specs
SHIP_TERMINALS = [
    {
        "name": "mother",
        "type": "MOTHER",
        "integrity": {"cpu": 100, "memory": 70, "storage": 50},
        "font_name": "Courier New",
        "font_size": 18,
    },
    {
        "name": "security",
        "type": "SECURITY",
        "integrity": {"cpu": 62, "memory": 89, "storage": 100},
        "font_name": "Courier New",
        "font_size": 18,
    },
    # Add more later
]

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, resizable=False)
        arcade.set_background_color(arcade.color.BLACK)

        self.game_state = GameState()

        # Build terminals
        self.terminals = {}
        for spec in SHIP_TERMINALS:
            config = build_terminal(spec["integrity"], spec["type"])

            terminal = Terminal(
                config,
                font_name=spec.get("font_name", "Courier New"),
                font_size=spec.get("font_size", 18)
            )
            terminal.name = spec["name"]

            # Proxy to preserve game_view.get_timestamp() compatibility
            class TimestampProxy:
                def __init__(self, gs):
                    self.gs = gs
                def get_timestamp(self):
                    return self.gs.get_timestamp()

            terminal.game_view = TimestampProxy(self.game_state)

            self.terminals[spec["name"]] = terminal

        # Create all locations
        self.locations = {}
        for loc_data in SHIP_LOCATIONS:
            loc = Location(loc_data, self.terminals, self.game_state)
            self.locations[loc_data["id"]] = loc

        # Start in corridor
        starting = self.locations["corridor"]
        starting.messages.append("You awaken. Darkness. Pain. Then — flickering light.")
        self.show_view(starting)

    def on_update(self, delta_time: float):
        self.game_state.update_time(delta_time)
        super().on_update(delta_time)


def main():
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()