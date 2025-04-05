from conceptual_json_parser import *

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