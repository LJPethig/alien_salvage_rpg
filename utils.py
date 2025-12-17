import random
from terminal.boot_sequence import universal_boot_sequence
from datetime import datetime, timedelta


def jitter(min_val, max_val):
    return random.uniform(min_val, max_val)

def system_checks(components):
    """
    Calculate overall system degradation (deterministic).
    Higher values = more instability, longer jitters, more glitches.
    """
    # Weighted base degradation
    weights = {
        "cpu": 0.45,  # Biggest impact on terminal responsiveness
        "memory": 0.35,
        "storage": 0.20,
    }

    base_degradation = sum(
        (100 - integrity) * weight
        for integrity, weight in zip(components.values(), weights.values())
    )

    # Non-linear penalty for critically low components
    critical_threshold = 30
    critical_penalty = 0
    for integrity in components.values():
        if integrity < critical_threshold:
            deficit = critical_threshold - integrity
            critical_penalty += deficit * 1.8  # Adjust this multiplier for desired intensity

    total_degradation = base_degradation + critical_penalty

    return max(0, round(total_degradation))

def build_terminal(terminal_integrity, terminal_type):

    total_system_degradation = system_checks(terminal_integrity)
    message = universal_boot_sequence(terminal_integrity, terminal_type)

    return (terminal_integrity["cpu"],
            terminal_integrity["memory"],
            terminal_integrity["storage"],
            total_system_degradation,
            terminal_type,
            message)


