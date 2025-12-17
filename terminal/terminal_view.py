import arcade
import random
from utils import jitter
from constants import *

class Terminal(arcade.View):
    def __init__(self, build, font_name=FONT_NAME_FALLBACK, font_size=FONT_SIZE_DEFAULT, line_spacing=None):
        super().__init__()
        (self.cpu_integrity,
         self.memory_integrity,
         self.storage_integrity,
         self.system_degradation,
         self.terminal_type,
         self.boot_lines) = build

        self.font_name = font_name
        self.font_size = font_size
        self.line_spacing = line_spacing or int(font_size * LINE_HEIGHT_MULTIPLIER)

        # Boot typewriter state
        self.current_line = 0
        self.current_char = 0
        self.write_line = 0
        self.char_timer = 0.0
        self.char_delay = 0.0

        # General display and input
        self.displayed_text = [""]  # All lines shown
        self.input_mode = False
        self.current_input = ""

        # Dynamic response typewriter (for responses and future windows)
        self.typing_response = False
        self.response_lines = []  # List of {"text": str, "speed": float}
        self.response_line_idx = 0
        self.response_char_idx = 0
        self.response_write_line = 0  # Which visual line we're writing to

        self.blink_timer = 0.0
        self.cursor_visible = True

        self.previous_view = None
        self.game_view = None  # Will be set by parent view
        self.on_exit_callback = None

    def start_typing_response(self, lines):
        """Start typing out multiple lines with degradation"""
        self.response_lines = lines
        self.response_line_idx = 0
        self.response_char_idx = 0
        self.typing_response = True
        # Only add the first blank line for the first response line
        self.displayed_text.append("")
        self.response_write_line = len(self.displayed_text) - 1

    def apply_degraded_char(self, char):
        """Apply glitch/corruption to a single character"""
        if self.system_degradation > GLITCH_CHAR_THRESHOLD and random.random() <= GLITCH_CHAR_CHANCE:
            return random.choice(GLITCH_CHARS)
        return char

    def get_next_delay(self, base_speed):
        """Shared delay logic for both boot and responses"""
        if self.system_degradation and random.random() < self.system_degradation / 100:
            return base_speed * jitter(DEGRADED_JITTER_MIN, DEGRADED_JITTER_MAX)
        return base_speed * jitter(NORMAL_JITTER_MIN, NORMAL_JITTER_MAX)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(BACKGROUND_COLOR)

        # Calculate how many lines fit on the screen
        available_height = self.height - MARGIN_TOP - MARGIN_BOTTOM  # Small bottom padding
        max_visible_lines = available_height // self.line_spacing

        total_lines = len(self.displayed_text)
        x = MARGIN_X

        # Determine the starting line index for drawing
        if total_lines <= max_visible_lines:
            # Not full yet — start from the top (classic boot behavior)
            start_y = self.height - MARGIN_TOP
            start_index = 0
            anchor_y = "top"
            y_step = -self.line_spacing  # Draw downward
        else:
            # Screen is full — show only the last N lines (scrolling)
            start_y = MARGIN_TOP + MARGIN_BOTTOM + (max_visible_lines - 1) * self.line_spacing
            start_index = total_lines - max_visible_lines
            anchor_y = "bottom"
            y_step = -self.line_spacing  # Still draw from bottom up for consistency

        # Draw all visible lines
        for i in range(start_index, total_lines):
            line_text = self.displayed_text[i]

            # Add live input if this is the active line and we're in input mode
            if i == total_lines - 1 and self.input_mode and not self.typing_response:
                line_text += self.current_input

            if total_lines <= max_visible_lines:
                # Top-aligned mode: grow downward from top
                y = start_y + (i - start_index) * y_step
            else:
                # Scrolling mode: bottom-aligned
                y = start_y + (i - (total_lines - max_visible_lines)) * y_step

            arcade.draw_text(
                line_text,
                x, y,
                TEXT_COLOR,
                font_size=self.font_size,
                font_name=self.font_name,
                anchor_y=anchor_y
            )

        # Cursor — only show when in input mode and not typing a response
        if self.cursor_visible and self.input_mode and not self.typing_response:
            active_line_text = self.displayed_text[-1] + self.current_input
            # measure_text is for calculating line width to place cursor
            measure_text = arcade.Text(
                active_line_text, 0, 0,
                font_size=self.font_size,
                font_name=self.font_name
            )
            cursor_x = x + measure_text.content_width

            if total_lines <= max_visible_lines:
                # Cursor follows last line from top
                cursor_y = start_y + (total_lines - 1 - start_index) * y_step
            else:
                # Cursor always at bottom in scrolling mode
                cursor_y = MARGIN_TOP + MARGIN_BOTTOM

            arcade.draw_text(
                "█",
                cursor_x, cursor_y,
                CURSOR_COLOR,
                font_size=self.font_size,
                font_name=self.font_name,
                anchor_y=anchor_y
            )

        # Border
        arcade.draw_line(0, self.height, self.width, self.height, BORDER_COLOR, BORDER_WIDTH)
        arcade.draw_line(0, 0, self.width, 0, BORDER_COLOR, BORDER_WIDTH)
        arcade.draw_line(0, 0, 0, self.height, BORDER_COLOR, BORDER_WIDTH)
        arcade.draw_line(self.width, 0, self.width, self.height, BORDER_COLOR, BORDER_WIDTH)

        # Scanlines
        for y in range(0, self.height, SCANLINE_STEP):
            arcade.draw_line(0, y, self.width, y, SCANLINE_COLOR, SCANLINE_WIDTH)

    def on_update(self, delta_time):
        self.blink_timer += delta_time
        if self.blink_timer >= CURSOR_BLINK_INTERVAL:
            self.blink_timer = 0
            self.cursor_visible = not self.cursor_visible

        self.char_timer += delta_time

        # Boot sequence typing
        if self.current_line < len(self.boot_lines):
            line_data = self.boot_lines[self.current_line]
            text = line_data["text"]

            # Dynamic timestamp replacement
            if text == "TIME_STAMP":
                if self.game_view:
                    text = self.game_view.get_timestamp()
                else:
                    text = "16 DEC 2175  SHIP TIME: 00:00:00"  # Fallback for direct testing

            base_speed = line_data["speed"]

            self.char_delay = self.get_next_delay(base_speed)

            while self.current_line < len(self.boot_lines):
                if self.current_char < len(text):
                    if self.char_timer >= self.char_delay:
                        char = text[self.current_char]
                        if char != " ":  # Spaces instant
                            char = self.apply_degraded_char(char)
                        self.displayed_text[self.write_line] += char
                        self.current_char += 1
                        self.char_timer -= self.char_delay
                    else:
                        break
                else:
                    # Line done
                    if line_data.get("pause"):
                        pause_mult = jitter(DEGRADED_JITTER_MIN, DEGRADED_JITTER_MAX) if (
                                self.system_degradation and random.random() < self.system_degradation / 100
                        ) else jitter(NORMAL_JITTER_MIN, NORMAL_JITTER_MAX)
                        self.char_timer = - (PAUSE * (pause_mult / 2))

                    next_idx = self.current_line + 1
                    if next_idx < len(self.boot_lines) and self.boot_lines[next_idx].get("same_line"):
                        self.current_line = next_idx
                        self.current_char = 0
                    else:
                        self.current_line = next_idx
                        self.current_char = 0
                        if self.current_line < len(self.boot_lines):
                            self.write_line += 1
                            self.displayed_text.append("")
                    break

            # Boot finished → enable input
            if self.current_line >= len(self.boot_lines) and not self.input_mode:
                self.input_mode = True
                self.cursor_visible = True

        # Response typing (after commands)
        elif self.typing_response and self.response_line_idx < len(self.response_lines):
            line_data = self.response_lines[self.response_line_idx]
            text = line_data["text"]
            base_speed = line_data.get("speed", FAST)

            self.char_delay = self.get_next_delay(base_speed)

            if self.response_char_idx < len(text):
                if self.char_timer >= self.char_delay:
                    char = text[self.response_char_idx]
                    if char != " ":
                        char = self.apply_degraded_char(char)
                    self.displayed_text[self.response_write_line] += char
                    self.response_char_idx += 1
                    self.char_timer -= self.char_delay
            else:
                # Current line finished — move to next
                self.response_line_idx += 1
                self.response_char_idx = 0
                if self.response_line_idx < len(self.response_lines):
                    # Add a new blank line for the next response line
                    self.displayed_text.append("")
                    self.response_write_line += 1

            # All responses done?
            if self.response_line_idx >= len(self.response_lines):
                self.typing_response = False
                # Add final prompt
                self.displayed_text.append("> ")
                self.current_input = ""

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.on_exit_callback:
                self.on_exit_callback()
            elif self.previous_view:
                self.window.show_view(self.previous_view)
            else:
                arcade.close_window()
            return

        if not self.input_mode or self.typing_response:
            return

        if key == arcade.key.ENTER:
            command = self.current_input.strip()
            full_line = "> " + self.current_input

            # Commit the typed command to the last line
            if self.displayed_text:
                self.displayed_text[-1] = full_line
            else:
                self.displayed_text.append(full_line)

            # Get response from command
            response_texts = self.process_command(command.lower())

            if response_texts:
                # Normal case: type out the response with degradation
                typed_lines = [{"text": line, "speed": FAST} for line in response_texts]
                self.start_typing_response(typed_lines)
            else:
                # Special case: no response lines (e.g. clear or empty enter)
                # → instantly add a fresh prompt
                self.displayed_text.append("> ")

            # Always reset input buffer
            self.current_input = ""

        elif key == arcade.key.BACKSPACE:
            self.current_input = self.current_input[:-1]

        else:
            if 32 <= key <= 126:
                char = chr(key)
                if modifiers & arcade.key.MOD_SHIFT:
                    shift_map = { '`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+',
                                  '[': '{', ']': '}', '\\': '|', ';': ':', "'": '"', ',': '<', '.': '>', '/': '?' }
                    char = shift_map.get(char.lower(), char.upper())
                # Optional: apply glitch to typed char too (feels chaotic, but cool)
                if self.system_degradation > GLITCH_CHAR_THRESHOLD and random.random() < GLITCH_CHAR_CHANCE:
                    char = random.choice(GLITCH_CHARS)
                self.current_input += char

    def process_command(self, command):
        if not command:
            return [""]

        if command == "help":
            return [
                "Available commands:",
                "  help    - Show this help",
                "  status  - Show system status",
                "  clear   - Clear terminal",
                "  exit    - Return to menu / quit"
            ]
        elif command == "status":
            return [
                f"System degradation: {self.system_degradation}%",
                f"CPU: {self.cpu_integrity}%   Memory: {self.memory_integrity}%   Storage: {self.storage_integrity}%"
            ]
        elif command == "clear":
            self.displayed_text = ["> "]
            self.current_input = ""
            return []
        elif command in ("exit", "quit", "back", "leave"):
            if self.on_exit_callback:
                self.on_exit_callback()
                return ["Logging out..."]
            elif self.previous_view:
                self.window.show_view(self.previous_view)
                return ["Logging out..."]
            else:
                arcade.close_window()
                return []
        else:
            return [f"Command not found: {command}"]

