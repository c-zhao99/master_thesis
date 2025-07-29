from enum import Enum, auto

class MinimumCardinality(Enum):
    ZERO = auto()
    ONE = auto()

class MaximumCardinality(Enum):
    ONE = auto()
    MANY = auto()


class Cardinality():
    def __init__(self, min_cardinality: MinimumCardinality, max_cardinality: MaximumCardinality):
        self.min_cardinality = min_cardinality
        self.max_cardinality = max_cardinality

    @staticmethod
    def convert_cardinality(min_c: str, max_c: str) -> "Cardinality": 
        min_cardinality = None
        max_cardinality = None
        if min_c == "ZERO":
            min_cardinality = MinimumCardinality.ZERO
        else:
            min_cardinality = MinimumCardinality.ONE
        
        if max_c == "ONE":
            max_cardinality = MaximumCardinality.ONE
        else:
            max_cardinality = MaximumCardinality.MANY

        return Cardinality(min_cardinality, max_cardinality)

class HierarchyCompleteness(Enum):
    TOTAL = auto()
    PARTIAL = auto()

    def convert_completeness(completeness: str) -> "HierarchyCompleteness":
        if completeness == "TOTAL":
            return HierarchyCompleteness.TOTAL
        else:
            return HierarchyCompleteness.PARTIAL

class HierarchyDisjointness(Enum):
    OVERLAPPING = auto()
    DISJOINT = auto()

    def convert_disjointness(disjointness: str) -> "HierarchyDisjointness":
        if disjointness == "OVERLAPPING":
            return HierarchyDisjointness.OVERLAPPING
        else:
            return HierarchyDisjointness.DISJOINT

class Entity:
    def __init__(self, name: str, identifier: list["Attribute"], attributes: list["Attribute"], weak_entity: str = None, hierarchy: "Hierarchy" = None):
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
    def __init__(self, name: str, entity_from: str, entity_to: str, cardinality_from: Cardinality, cardinality_to: Cardinality, attributes: list["Attribute"]):
        self.name = name
        self.entity_from = entity_from
        self.entity_to = entity_to
        self.cardinality_from = cardinality_from
        self.cardinality_to = cardinality_to
        self.attributes = attributes

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
