from constants import FAST, INSTANT, SLOW
from random import choice

def universal_boot_sequence(terminal_integrity, terminal_type):

    if terminal_type == "MOTHER":
        num1 = choice(range(206, 219))
        num2 = choice(range(63, 89))
        terminal = terminal_type + f" MOT-{num1}.{num2}"
    else:
        # add more logic for unique terminal names
        terminal = terminal_type + " terminal"
    # randomise this also
    # "loader 2175-rc2-00976-WYCorp cksum: 9f2d1e6a" random CRC-32 checksum

    return [
            {"text": terminal + " rebooting ", "speed": FAST, "pause": True},
            {"text": ".......", "speed": SLOW, "pause": True, "same_line": True},
            {"text": "loader 2175-rc2-00976-WYCorp cksum: 9f2d1e6a", "speed": FAST, "pause": True},
            {"text": "clearing /tmp", "speed": FAST, "pause": True},
            {"text": "starting network: rshd rexecd rlogind rwhod", "speed": FAST, "pause": True},
            {"text": "System Checks ", "speed": FAST, "pause": False},
            {"text": "CPU ", "speed": FAST, "pause": False},
            {"text": "....", "speed": SLOW, "pause": True, "same_line": True},
            {"text": str(terminal_integrity["cpu"]) + "%", "speed": INSTANT, "pause": True, "same_line": True},
            {"text": "Memory ", "speed": FAST, "pause": False},
            {"text": "....", "speed": SLOW, "pause": True, "same_line": True},
            {"text": str(terminal_integrity["memory"]) + "%", "speed": INSTANT, "pause": True, "same_line": True},
            {"text": "Storage ", "speed": FAST, "pause": False},
            {"text": "....", "speed": SLOW, "pause": True, "same_line": True},
            {"text": str(terminal_integrity["storage"]) + "%", "speed": INSTANT, "pause": True, "same_line": True},
            {"text": "OS load ", "speed": FAST, "pause": False},
            {"text": "TTY=pts/0; PWD=/var/log; USER = root; COMMAND=usr/bin/tail -f", "speed": FAST, "pause": True},
            {"text": "....", "speed": SLOW, "pause": True, "same_line": True},
            {"text": "-" * 50, "speed": INSTANT, "pause": True},
            {"text": "", "speed": INSTANT},
            {"text": "TIME_STAMP", "speed": FAST, "pause": True},
            {"text": "MOTHER 6000 OPERATING SYSTEM", "speed": FAST, "pause": False},
            {"text": "", "speed": INSTANT},
            {"text": "Enter command", "speed": FAST, "pause": False},
            {"text": "> ", "speed": INSTANT, "pause": False},
        ]
