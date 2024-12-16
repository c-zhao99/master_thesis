from enum import Enum, auto

class Cardinality(Enum):
    ZERO_TO_ONE = auto()
    ZERO_TO_MANY = auto()
    ONE_TO_ONE = auto()
    ONE_TO_MANY = auto()

    def convert_cardinality(cardinality: str):
        if cardinality == "ZERO_TO_ONE":
            return Cardinality.ZERO_TO_ONE
        elif cardinality == "ZERO_TO_MANY":
            return Cardinality.ZERO_TO_MANY
        elif cardinality == "ONE_TO_ONE":
            return Cardinality.ONE_TO_ONE
        else:
            return Cardinality.ONE_TO_MANY


class HierarchyCompleteness(Enum):
    TOTAL = auto()
    PARTIAL = auto()

    def convert_completeness(completeness):
        if completeness == "TOTAL":
            return HierarchyCompleteness.TOTAL
        else:
            return HierarchyCompleteness.PARTIAL

class HierarchyDisjointness(Enum):
    OVERLAPPING = auto()
    DISJOINT = auto()

    def convert_disjointness(disjointness):
        if disjointness == "OVERLAPPING":
            return HierarchyDisjointness.OVERLAPPING
        else:
            return HierarchyDisjointness.DISJOINT

class Entity:
    def __init__(self, name: str, identifier: list["Attribute"], weak_entity: str, attributes: list["Attribute"], hierarchy: "Hierarchy" = None):
        self.name = name
        self.identifier = identifier
        self.weak_entity = weak_entity
        self.attributes = attributes
        self.hierarchy = hierarchy

class Hierarchy:
    def __init__(self, children: list[str], hierarchy_completeness: HierarchyCompleteness, hierarchy_disjointness: HierarchyDisjointness):
        self.children = children
        self.hierarchy_completeness = hierarchy_completeness
        self.hierarchy_disjointness = hierarchy_disjointness

class Relationship:
    def __init__(self, name: str, entity_from: str, entity_to: str, cardinality_from: Cardinality, cardinality_to: Cardinality):
        self.name = name
        self.entity_from = entity_from
        self.entity_to = entity_to
        self.cardinality_from = cardinality_from
        self.cardinality_to = cardinality_to

class Attribute:
    def __init__(self, name: str, cardinality: Cardinality, attribute_type: type, is_unique: bool):
        self.name = name
        self.cardinality = cardinality
        self.attribute_type = attribute_type
        self.is_unique = is_unique
        

class CompositeAttribute(Attribute):
    def __init__(self, name: str, cardinality: Cardinality, attribute_type: type, is_unique: bool, simple_attributes: list[Attribute]):
        super().__init__(name, cardinality, attribute_type, is_unique)
        self.simple_attributes = simple_attributes
