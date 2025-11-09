from enum import Enum, auto
from ..exceptions.exceptions import NoHierarchyExcpetion

class MinimumCardinality(Enum):
    ZERO = auto()
    ONE = auto()

class MaximumCardinality(Enum):
    ONE = auto()
    MANY = auto()

class HierarchyCompleteness(Enum):
    TOTAL = auto()
    PARTIAL = auto()

class HierarchyDisjointness(Enum):
    OVERLAPPING = auto()
    DISJOINT = auto()

class Cardinality():
    def __init__(self, min_cardinality: MinimumCardinality, max_cardinality: MaximumCardinality):
        self._min_cardinality = min_cardinality
        self._max_cardinality = max_cardinality
    
    @property
    def min_cardinality(self):
        return self._min_cardinality
    
    @property
    def max_cardinality(self):
        return self._max_cardinality

    @staticmethod
    def convert_cardinality(min_c: str, max_c: str) -> "Cardinality": 
        min_cardinality = None
        max_cardinality = None
        if min_c == "Optional":
            min_cardinality = MinimumCardinality.ZERO
        else:
            min_cardinality = MinimumCardinality.ONE
        
        if max_c == "One":
            max_cardinality = MaximumCardinality.ONE
        else:
            max_cardinality = MaximumCardinality.MANY

        return Cardinality(min_cardinality, max_cardinality)
    
    def deep_copy(self) -> "Cardinality":
        """Create a deep copy of this Cardinality."""
        return Cardinality(self._min_cardinality, self._max_cardinality)

class Entity:
    def __init__(self, name: str):
        self._name = name
        self._identifiers = []
        self._strong_entity = None
        self._attributes = []
        self._hierarchy = None

    @property
    def name(self):
        return self._name

    @property
    def identifiers(self):
        return self._identifiers
    
    @property
    def strong_entity(self):
        return self._strong_entity
    
    @property
    def attributes(self):
        return self._attributes
    
    @property
    def hierarchy(self):
        return self._hierarchy
    
    def add_identifier(self, identifier: "Attribute"):
        self._identifiers.append(identifier)
        
    def add_attribute(self, attribute: "Attribute"):
        self._attributes.append(attribute)

    def set_strong_entity(self, strong_entity: str):
        self._strong_entity = strong_entity
    
    def set_hierarchy(self, hierarchy: "Hierarchy"):
        self._hierarchy = hierarchy
    
    def add_child(self, child: str):
        if self.hierarchy:
            self._hierarchy.add_child(child)
        else:
            raise NoHierarchyExcpetion()
        
    def remove_attribute(self, attribute_name: str):
        for attribute in self._attributes:
            if attribute.name == attribute_name:
                self._attributes.remove(attribute)
                break
    
    def remove_identifier(self, identifier_name: str):
        for identifier in self._identifiers:
            if identifier.name == identifier_name:
                self._identifiers.remove(identifier)
                break
    
    def deep_copy(self) -> "Entity":
        """Create a deep copy of this Entity."""
        entity_copy = Entity(self._name)
        
        # Deep copy identifiers
        for identifier in self._identifiers:
            entity_copy.add_identifier(identifier.deep_copy())
        
        # Deep copy attributes
        for attribute in self._attributes:
            entity_copy.add_attribute(attribute.deep_copy())
        
        # Copy strong entity reference (string, immutable)
        entity_copy._strong_entity = self._strong_entity
        
        # Deep copy hierarchy if it exists
        if self._hierarchy:
            entity_copy._hierarchy = self._hierarchy.deep_copy()
        
        return entity_copy

class Hierarchy:
    def __init__(self, hierarchy_completeness: HierarchyCompleteness, hierarchy_disjointness: HierarchyDisjointness):
        self._children = []
        self._hierarchy_completeness = hierarchy_completeness
        self._hierarchy_disjointness = hierarchy_disjointness
    
    @property
    def children(self):
        return self._children

    @property
    def hierarchy_completeness(self):
        return self._hierarchy_completeness
    
    @property
    def hierarchy_disjointness(self):
        return self._hierarchy_disjointness
    
    def add_child(self, child: str):
        self.children.append(child)
    
    def deep_copy(self) -> "Hierarchy":
        """Create a deep copy of this Hierarchy."""
        hierarchy_copy = Hierarchy(self._hierarchy_completeness, self._hierarchy_disjointness)
        # Copy all children (strings are immutable, so we can just copy the list)
        hierarchy_copy._children = self._children.copy()
        return hierarchy_copy

class Relationship:
    def __init__(self, name: str, entity_from: str, entity_to: str, cardinality_from: Cardinality, cardinality_to: Cardinality):
        self._name = name
        self._entity_from = entity_from
        self._entity_to = entity_to
        self._cardinality_from = cardinality_from
        self._cardinality_to = cardinality_to
        self._attributes = []
    
    @property
    def name(self):
        return self._name
    
    @property
    def entity_from(self):
        return self._entity_from

    @property
    def entity_to(self):
        return self._entity_to
    
    @property
    def cardinality_from(self):
        return self._cardinality_from

    @property
    def cardinality_to(self):
        return self._cardinality_to
    
    @property
    def attributes(self):
        return self._attributes
    
    def set_name(self, name: str):
        self._name = name

    def add_attribute(self, attribute: "Attribute"):
        self._attributes.append(attribute)

    def set_cardinality_from(self, cardinality: Cardinality):
        self._cardinality_from = cardinality
    
    def set_cardinality_to(self, cardinality: Cardinality):
        self._cardinality_to = cardinality
    
    def set_entity_from(self, entity_from: str):
        self._entity_from = entity_from
    
    def set_entity_to(self, entity_to: str):
        self._entity_to = entity_to
    
    def deep_copy(self) -> "Relationship":
        """Create a deep copy of this Relationship."""
        relationship_copy = Relationship(
            self._name,
            self._entity_from,
            self._entity_to,
            self._cardinality_from.deep_copy(),
            self._cardinality_to.deep_copy()
        )
        
        # Deep copy attributes
        for attribute in self._attributes:
            relationship_copy.add_attribute(attribute.deep_copy())
        
        return relationship_copy


class Attribute:
    def __init__(self, name: str, cardinality: Cardinality, is_unique: bool):
        self._name = name
        self._cardinality = cardinality
        self._is_unique = is_unique
        
    @property
    def name(self):
        return self._name
    
    @property
    def cardinality(self):
        return self._cardinality
    
    @property
    def is_unique(self):
        return self._is_unique

    def set_cardinality(self, cardinality: Cardinality):
        self._cardinality = cardinality
    
    def deep_copy(self) -> "Attribute":
        """Create a deep copy of this Attribute."""
        return Attribute(self._name, self._cardinality.deep_copy(), self._is_unique)

class CompositeAttribute(Attribute):
    def __init__(self, name: str, cardinality: Cardinality, is_unique: bool):
        super().__init__(name, cardinality, is_unique)
        self._simple_attributes = []
    
    @property
    def simple_attributes(self):
        return self._simple_attributes
    
    def add_simple_attribute(self, simple_attribute: Attribute):
        self._simple_attributes.append(simple_attribute)
    
    def deep_copy(self) -> "CompositeAttribute":
        """Create a deep copy of this CompositeAttribute."""
        composite_copy = CompositeAttribute(self._name, self._cardinality.deep_copy(), self._is_unique)
        
        # Deep copy all simple attributes
        for simple_attr in self._simple_attributes:
            composite_copy.add_simple_attribute(simple_attr.deep_copy())
        
        return composite_copy
    