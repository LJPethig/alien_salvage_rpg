import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_NAME_PRIMARY, FONT_SIZE_DEFAULT
from utils import build_terminal
from terminal.terminal_view import Terminal

from game_view import GameView  # ← UNCOMMENT this line when you're ready for full game

# Central definition of ship terminals
SHIP_TERMINALS = [
    {
        "name": "mother",
        "type": "MOTHER",
        "integrity": {"cpu": 100, "memory": 70, "storage": 50},
        "font_name": FONT_NAME_PRIMARY,
        "font_size": FONT_SIZE_DEFAULT,
    },
    {
        "name": "security",
        "type": "SECURITY",
        "integrity": {"cpu": 62, "memory": 89, "storage": 100},
        "font_name": FONT_NAME_PRIMARY,
        "font_size": FONT_SIZE_DEFAULT,
    },
    # Add more later...
]


def create_terminals():
    """Build all Terminal instances from the central spec list."""
    terminals = {}
    for spec in SHIP_TERMINALS:
        config = build_terminal(spec["integrity"], spec["type"])

        font_name = spec.get("font_name", FONT_NAME_PRIMARY)
        font_size = spec.get("font_size", FONT_SIZE_DEFAULT)

        terminal_instance = Terminal(config, font_name=font_name, font_size=font_size)
        terminal_instance.name = spec["name"]

        terminals[spec["name"]] = terminal_instance

    return terminals


def main():
    window = arcade.Window(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        "Alien Salvage RPG",
        resizable=False,
        style=arcade.Window.WINDOW_STYLE_BORDERLESS
    )

    all_terminals = create_terminals()

    # ===================================================================
    # QUICK TESTING MODE — keep this while developing terminals
    # ===================================================================
    # terminal_to_show = "mother"  # Change to "security" or any name to test directly
    #
    # if terminal_to_show in all_terminals:
    #     term = all_terminals[terminal_to_show]
    #     window.show_view(term)
    # else:
    #     # Safety fallback
    #     arcade.draw_text(
    #         f"ERROR: Terminal '{terminal_to_show}' not found.",
    #         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
    #         arcade.color.RED, 30, anchor_x="center", anchor_y="center"
    #     )
    #     window.show_view(arcade.View())
    #     arcade.run()
    #     return

    # ===================================================================
    # FULL GAME MODE — uncomment the block below when GameView is ready
    # ===================================================================
    game_view = GameView(all_terminals)
    window.show_view(game_view)

    arcade.run()


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    main()