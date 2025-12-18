# locations.py
import arcade
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TEXT_COLOR, BACKGROUND_COLOR, FONT_NAME_PRIMARY, FONT_SIZE_DEFAULT
)

SHIP_LOCATIONS = [
    {
        "id": "corridor",
        "name": "Main Corridor",
        "description": [
            "You stand in a long, dimly lit corridor aboard the derelict salvage vessel.",
            "Flickering emergency lights cast harsh shadows on rusted bulkheads.",
            "Cold vapor hisses from cracked pipes overhead.",
            "To the north, a heavy door bears the label: MOTHER CORE ACCESS.",
        ],
        "background": "resources/images/corridor.png",
        "exits": {"north": "mother_room", "n": "mother_room", "go north": "mother_room"},
        "terminal": None,
    },
    {
        "id": "mother_room",
        "name": "Mother Core Chamber",
        "description": [
            "You stand in the heart of the ship — the MOTHER core chamber.",
            "A massive curved console dominates the room, its screen dark and silent.",
            "Alien glyphs are etched into the metal. The air is thick with static.",
            "This is the primary AI interface.",
            "",
            "You can 'use terminal' or 'access console' to interact with it.",
            "Type 'south' or 'leave' to return to the corridor.",
        ],
        "background": "resources/images/mother_room.png",
        "exits": {"south": "corridor", "s": "corridor", "leave": "corridor", "back": "corridor"},
        "terminal": "mother",
        "access_commands": ["use terminal", "access terminal", "use console", "access console", "terminal", "console"],
    },
]

class Location(arcade.View):
    def __init__(self, data, terminals_dict, game_state):
        super().__init__()
        self.data = data
        self.terminals_dict = terminals_dict
        self.game_state = game_state

        self.current_input = ""
        self.messages = []

        # === Background SpriteList (correct for Arcade 3.x) ===
        self.background_list = arcade.SpriteList()
        try:
            bg_sprite = arcade.Sprite(data["background"])
            # Scale to fill height, preserve aspect
            scale = SCREEN_HEIGHT / bg_sprite.height
            bg_sprite.scale = scale
            # Center in full screen (sections don't affect sprite positioning)
            bg_sprite.center_x = SCREEN_WIDTH // 2
            bg_sprite.center_y = SCREEN_HEIGHT // 2
            self.background_list.append(bg_sprite)
        except Exception as e:
            print(f"Background load failed: {e}")

        # Section Manager (optional for future event routing, but useful)
        self.section_manager = arcade.SectionManager(self)

        # Background section bounds (for overlay)
        bg_width = int(SCREEN_WIDTH * 0.7)
        self.bg_section = arcade.Section(left=0, bottom=0, width=bg_width, height=SCREEN_HEIGHT)
        self.section_manager.add_section(self.bg_section)

        # Text section bounds
        text_left = bg_width
        self.text_section = arcade.Section(left=text_left, bottom=0, width=SCREEN_WIDTH - text_left, height=SCREEN_HEIGHT)
        self.section_manager.add_section(self.text_section)

        # Terminal state
        self.terminal_instance = None
        terminal_name = data.get("terminal")
        if terminal_name and terminal_name in terminals_dict:
            self.terminal_instance = terminals_dict[terminal_name]
            self.terminal_instance.previous_view = self
            self.terminal_instance.on_exit_callback = self.deactivate_terminal

        self.terminal_active = False

    def activate_terminal(self):
        if self.terminal_instance:
            self.terminal_active = True
            self.messages.append("Console initializing...")

    def deactivate_terminal(self):
        self.terminal_active = False
        self.messages.append("Terminal session ended. Screen powers down.")

    def on_update(self, delta_time: float):
        self.game_state.update_time(delta_time)
        if self.terminal_active and self.terminal_instance:
            self.terminal_instance.on_update(delta_time)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(BACKGROUND_COLOR)

        # Draw background (full screen)
        self.background_list.draw()

        # Dark overlay on background area
        arcade.draw_lrbt_rectangle_filled(
            self.bg_section.left, self.bg_section.right,
            self.bg_section.bottom, self.bg_section.top,
            (0, 0, 0, 140)
        )

        # Dark panel on text area
        arcade.draw_lrbt_rectangle_filled(
            self.text_section.left, self.text_section.right,
            self.text_section.bottom, self.text_section.top,
            (0, 0, 0, 200)
        )

        # Text content (only when terminal inactive)
        if not self.terminal_active:
            # Timestamp
            timestamp = self.game_state.get_timestamp()
            arcade.draw_text(
                timestamp,
                SCREEN_WIDTH - 30, SCREEN_HEIGHT - 40,
                arcade.color.DARK_GREEN, 14,
                anchor_x="right", font_name=FONT_NAME_PRIMARY
            )

            # Room title
            arcade.draw_text(
                self.data["name"],
                self.text_section.left + 30, SCREEN_HEIGHT - 70,
                arcade.color.LIGHT_GREEN, 36,
                bold=True, font_name=FONT_NAME_PRIMARY
            )

            # Description
            y = SCREEN_HEIGHT - 160
            for line in self.data["description"]:
                arcade.draw_text(
                    line,
                    self.text_section.left + 30, y,
                    TEXT_COLOR, FONT_SIZE_DEFAULT,
                    font_name=FONT_NAME_PRIMARY,
                    width=self.text_section.width - 60
                )
                y -= 45

            # Messages
            y = self.text_section.height // 2 + 100
            for msg in self.messages[-10:]:
                arcade.draw_text(
                    msg,
                    self.text_section.left + 30, y,
                    arcade.color.CYAN, 15,
                    font_name=FONT_NAME_PRIMARY,
                    width=self.text_section.width - 60
                )
                y -= 35

            # Input prompt
            cursor = "█" if int(self.game_state.elapsed_seconds * 2) % 2 else " "
            arcade.draw_text(
                f"> {self.current_input}{cursor}",
                self.text_section.left + 30, 120,
                TEXT_COLOR, FONT_SIZE_DEFAULT + 6,
                font_name=FONT_NAME_PRIMARY
            )

        # Full terminal when active
        if self.terminal_active and self.terminal_instance:
            self.terminal_instance.on_draw()

    def on_key_press(self, key, modifiers):
        if self.terminal_active and self.terminal_instance:
            self.terminal_instance.on_key_press(key, modifiers)
            return

        if key == arcade.key.ENTER:
            cmd = self.current_input.strip().lower()
            self.current_input = ""
            self.messages.append(f"> {cmd}")

            if cmd in self.data.get("access_commands", []) and self.terminal_instance:
                self.activate_terminal()
                return

            if cmd in self.data["exits"]:
                target_id = self.data["exits"][cmd]
                target_loc = self.window.locations.get(target_id)
                if target_loc:
                    self.window.show_view(target_loc)
                    target_loc.messages.append("You enter the chamber.")
                else:
                    self.messages.append("You can't go that way.")
                return

            if cmd in ["look", "l"]:
                self.messages.extend(self.data["description"])
            elif cmd == "help":
                cmds = list(self.data["exits"].keys()) + self.data.get("access_commands", [])
                self.messages.append(f"Commands: {', '.join(cmds)}, look, help")
            else:
                self.messages.append("I don't understand that.")

        elif key == arcade.key.BACKSPACE:
            self.current_input = self.current_input[:-1]
        elif 32 <= key <= 126:
            self.current_input += chr(key)