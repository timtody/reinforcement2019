from enum import Enum, auto

class ActionSpace(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    IDLE = 4

    def get_dir(self):
        if self.value == 0:
            return (0, -1)
        if self.value == 1:
            return (0, 1)
        if self.value == 2:
            return (-1, 0)
        if self.value == 3:
            return (1, 0)
        if self.value == 4:
            return (0, 0)