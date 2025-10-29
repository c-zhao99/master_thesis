from ..data.conceptual import *

def load_tpl_file(file_path):
    with open(file_path) as f:
        return f.read()
    

def create_copy_from_entity(entity: Entity, entity_name: str = None) -> Entity:
    new_entity_name = entity_name if entity_name else entity.name
    new_entity = Entity(new_entity_name)
    for identifier in entity.identifiers:
        new_identifier = Attribute(identifier.name, identifier.cardinality, identifier.is_unique)
        new_entity.add_identifier(new_identifier)
    for attribute in entity.attributes:
        new_attribute = Attribute(attribute.name, attribute.cardinality, attribute.is_unique)
        new_entity.add_attribute(new_attribute)
    return new_entity

def get_primary_keys(entity: Entity) -> list[str]:
    ids = []
    for identifier in entity.identifiers:
        ids.append(identifier.name)
    return ids