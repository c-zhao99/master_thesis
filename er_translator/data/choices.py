from enum import Enum, auto

class COMPOSITE_ATTRIBUTE_CHOICE(Enum):
    KEEP_COMPOSITE = auto()
    KEEP_SIMPLE_ATTRIBUTES = auto()

class RELATIONSHIP_CHOICE(Enum):
    RELANTIONSHIP_TABLE = auto()
    MERGE_INTO_SINGLE_TABLE = auto()
    ADD_FOREIGN_KEY = auto()

class HIERARCHY_CHOICE(Enum):
    COLLAPSE_UPWARDS = auto()
    COLLAPSE_DOWNWARDS = auto()