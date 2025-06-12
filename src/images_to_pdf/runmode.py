from typing import Literal

state: Literal["gui", "cli"] = "cli"


def set_runmode(mode: Literal["gui", "cli"]):
    global state
    state = mode
