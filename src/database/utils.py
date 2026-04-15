from enum import Enum


class DifficultyEnum(Enum):
    Unknown = "Unknown"
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"

    def get_values() -> list[str]:
        return [x.value for x in DifficultyEnum]
