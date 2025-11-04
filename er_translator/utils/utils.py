from ..data.conceptual import *

def load_tpl_file(file_path):
    with open(file_path) as f:
        return f.read()
    

def create_copy_from_entity(entity: Entity, entity_name: str = None, identifiers_modifier: str = "", keep_attributes: bool = True) -> Entity:
    new_entity_name = entity_name if entity_name else entity.name
    new_entity = Entity(new_entity_name)
    
    for identifier in entity.identifiers:
        if identifiers_modifier != "":
            new_identifier_name = identifier.name + identifiers_modifier
        else:
            new_identifier_name = identifier.name
        new_identifier = Attribute(new_identifier_name, identifier.cardinality, identifier.is_unique)
        new_entity.add_identifier(new_identifier)
    
    if keep_attributes:
        for attribute in entity.attributes:
            new_attribute = Attribute(attribute.name, attribute.cardinality, attribute.is_unique)
            new_entity.add_attribute(new_attribute)
    return new_entity

def get_primary_keys(entity: Entity) -> list[str]:
    ids = []
    for identifier in entity.identifiers:
        ids.append(identifier.name)
    return ids

def get_all_father_entities(entities: list[Entity]) -> set[str]:
    father_entities = set()

    for entity in entities:
        if entity.hierarchy:
            father_entities.add(entity.name)

    return father_entities

def retrieve_connected_relationships(entity_names: list[str], relationships: dict[str, Relationship]) -> set[str]:
    connected_relationships = set()

    for relationship in relationships.values():
        
        if relationship.entity_from in entity_names or relationship.entity_to in entity_names:
            connected_relationships.add(relationship.name)

    return connected_relationships

def retrieve_children_names(father_entity: Entity) -> set[str]:
    children_names = set()
    for child_name in father_entity.hierarchy.children:
        children_names.add(child_name)

    return children_names

def retrieve_all_hierarchy_entities(entities: list[Entity]) -> set[str]:
    hierarchy_entities = set()
    for entity in entities:
        if entity.hierarchy:
            hierarchy_entities.add(entity.name)
            for child_name in entity.hierarchy.children:
                hierarchy_entities.add(child_name)
    return hierarchy_entities

def retrieve_all_hierarchy_relationships(entities: list[Entity], relationships: dict[str, Relationship]) -> set[str]:
    hierarchy_entities = retrieve_all_hierarchy_entities(entities)
    return retrieve_connected_relationships(hierarchy_entities, relationships)