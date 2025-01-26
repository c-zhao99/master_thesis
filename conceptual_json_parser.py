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
    attribute_type = attribute["attribute_type"]
    is_unique = attribute["is_unique"]
    simple_attributes = attribute["simple_attributes"]

    new_cardinality = Cardinality.convert_cardinality(cardinality)
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

        return Entity(entity_name, new_identifiers, weak_entity, new_attributes, new_hierarchy)
    else:
        return Entity(entity_name, new_identifiers, weak_entity, new_attributes)
  
def json_create_relationship(relationship):
    name = relationship["relationship_name"]
    entity_from = relationship["entity_from"]
    entity_to = relationship["entity_to"]
    cardinality_from = relationship["cardinality_from"]
    cardinality_to = relationship["cardinality_to"]
    attributes = relationship["attributes"]

    new_attributes = []
    for attribute in attributes:
        new_attributes.append(json_create_attribute(attribute))


    new_cardinality_from = Cardinality.convert_cardinality(cardinality_from)
    new_cardinality_to = Cardinality.convert_cardinality(cardinality_to)

    return Relationship(name, entity_from, entity_to, new_cardinality_from, new_cardinality_to, new_attributes)


entities = {}
relationships = {}

with open("examples/example1.json", "r") as file:
    json_data = json.load(file)

for entity in json_data["entities"]:
    entity_name = entity["entity_name"]
    if entity_name not in entities:
        entities[entity_name] = json_create_entity(entity)

for relationship in json_data["relationships"]:
    relationship_name = relationship["relationship_name"]
    relationships[relationship_name] = json_create_relationship(relationship)

from diagram_printer import *

print_entities(entities.values())
print_relationships(relationships.values())
