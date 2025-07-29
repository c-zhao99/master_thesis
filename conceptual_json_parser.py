# Parse JSON file describing ER diagram into the classes of conceptual.py

from data.conceptual import *
import json

def convert_type(attribute_type):
    if attribute_type == "string":
        return str
    elif attribute_type == "int":
        return int
    elif attribute_type == "bool":
        return bool
    else:
        return None

def json_create_attribute(attribute):
    name = attribute["attribute_name"]

    cardinality = attribute["cardinality"]
    min_cardinality = cardinality["min_cardinality"]
    max_cardinality = cardinality["max_cardinality"]

    attribute_type = attribute["attribute_type"]
    is_unique = attribute["is_unique"]
    simple_attributes = attribute["simple_attributes"]

    new_cardinality = Cardinality.convert_cardinality(min_cardinality, max_cardinality)
    new_attribute_type = convert_type(attribute_type)
    new_simple_attributes = []
    for simple_attribute in simple_attributes:
        new_simple_attributes.append(json_create_attribute(simple_attribute))
    
    if new_simple_attributes:
        return CompositeAttribute(name, new_cardinality, new_attribute_type, is_unique, new_simple_attributes)
    else:
        return Attribute(name, new_cardinality, new_attribute_type, is_unique)


def json_create_hierarchy(hierarchy):
    children = hierarchy["children"]
    hierarchy_completeness = hierarchy["hierarchy_completeness"]
    hierarchy_disjointness = hierarchy["hierarchy_disjointness"]

    new_hierarchy_completeness = HierarchyCompleteness.convert_completeness(hierarchy_completeness)
    new_hierarchy_disjointness = HierarchyDisjointness.convert_disjointness(hierarchy_disjointness)

    return Hierarchy(children, new_hierarchy_completeness, new_hierarchy_disjointness)

def json_create_entity(entity):
    entity_name = entity["entity_name"]
    identifiers = entity["identifier"]
    weak_entity = entity["weak_entity"]
    attributes = entity["attributes"]
    hierarchy = entity["hierarchy"]

    new_identifiers = []
    for identifier in identifiers:
        new_identifiers.append(json_create_attribute(identifier))

    new_attributes = []
    for attribute in attributes:
        new_attributes.append(json_create_attribute(attribute))
    
    if hierarchy:
        new_hierarchy = json_create_hierarchy(hierarchy)

        return Entity(entity_name, new_identifiers, new_attributes, weak_entity, new_hierarchy)
    else:
        return Entity(entity_name, new_identifiers, new_attributes, weak_entity)
  
def json_create_relationship(relationship):
    name = relationship["relationship_name"]
    entity_from = relationship["entity_from"]
    entity_to = relationship["entity_to"]

    cardinality_from = relationship["cardinality_from"]
    min_cardinality_from = cardinality_from["min_cardinality"]
    max_cardinality_from = cardinality_from["max_cardinality"]

    cardinality_to = relationship["cardinality_to"]
    min_cardinality_to = cardinality_to["min_cardinality"]
    max_cardinality_to = cardinality_to["max_cardinality"]

    attributes = relationship["attributes"]

    new_attributes = []
    for attribute in attributes:
        new_attributes.append(json_create_attribute(attribute))

    new_cardinality_from = Cardinality.convert_cardinality(min_cardinality_from, max_cardinality_from)
    new_cardinality_to = Cardinality.convert_cardinality(min_cardinality_to, max_cardinality_to)

    return Relationship(name, entity_from, entity_to, new_cardinality_from, new_cardinality_to, new_attributes)
