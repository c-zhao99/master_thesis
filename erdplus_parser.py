import json
from collections import deque

from data.conceptual import *

class ERDPLUS_Parser:
    def __init__(self):
        self._json_data = {}
        self._entities = {}
        self._relationships = {}

        self._entity_ids = {}
        self._relationship_ids = {}
        self._attribute_ids = {}

        self._json_entities = deque()
        self._json_relationships = deque()
        self._json_attributes = deque()

    @property
    def entities(self):
        return self._entities
    
    @property
    def relationships(self):
        return self._relationships
    
    def parse_erdplus_diagram(self, file_path: str):
        self._load_json_data(file_path)
        # separate nodes
        self._separate_nodes()

        # parse entities
        self._parse_entities()

        # parse relationships
        self._parse_relationships()

        # parse attributes
        self._parse_attributes()
        
    def _separate_nodes(self):
        for node in self._json_data.get("data").get("nodes"):
            node_type = node.get("type")
            if node_type == "Entity":
                self._json_entities.append(node)
            elif node_type == "Relationship":
                self._json_relationships.append(node)
            elif node_type == "Attribute":
                self._json_attributes.append(node)

    def _parse_entities(self):
        while self._json_entities:
            json_entity = self._json_entities.popleft()
            entity_data = json_entity.get("data")
            parent_id = entity_data.get("parentId")
            if parent_id and parent_id not in self._entity_ids:
                # current entity is a subtype and parent hasn't been created yet
                # put it back in the queue
                self._json_entities.append(json_entity)
            else:
                entity = self._create_entity(entity_data)
                self._entities[entity.name] = entity
                entity_id = json_entity.get("id")
                self._entity_ids[entity_id] = entity

    def _parse_relationships(self):
        while self._json_relationships:
            json_relationship = self._json_relationships.popleft()
            relationship_id = json_relationship.get("id")
            json_data = json_relationship.get("data")

            name = json_data.get("label")
            
            source_entity = json_data.get("sourceEntityDetails")
            source_entity_name = self._entity_ids[source_entity.get("id")].name
            source_cardinality = Cardinality.convert_cardinality(source_entity.get("minCardinality"), source_entity.get("maxCardinality"))

            target_entity = json_data.get("targetEntityDetails")
            target_entity_name = self._entity_ids[target_entity.get("id")].name
            target_cardinality = Cardinality.convert_cardinality(target_entity.get("minCardinality"), target_entity.get("maxCardinality"))

            if json_data.get("isIdentifying"):
                self._add_strong_entity(source_entity_name, target_entity_name)

            relationship = Relationship(name, source_entity_name, target_entity_name, source_cardinality, target_cardinality)
            self._relationships[name] = relationship
            self._relationship_ids[relationship_id] = relationship

    def _parse_attributes(self):
        while self._json_attributes:
            json_attribute = self._json_attributes.popleft()
            attribute_data = json_attribute.get("data")
            parent_id = json_attribute.get("parentId")

            if parent_id not in self._entity_ids and parent_id not in self._relationship_ids and parent_id not in self._attribute_ids:
                # Composite attribute not created yet
                # put it back in the queue
                
                self._json_attributes.append(json_attribute)
                continue
            
            attribute = self._create_attribute(attribute_data)
            if parent_id in self._entity_ids:
                # is an attribute of an entity

                # TODO how to define identifiers in ERD PLUS
                attribute_types = attribute_data.get("types")
                attribute_parameters = {} if isinstance(attribute_types, list) else attribute_types
                is_unique = attribute_parameters.get("Unique") or attribute_parameters.get("Partially Unique")
                entity = self._entity_ids[parent_id]
                if is_unique:
                    entity.add_identifier(attribute)
                else:
                    entity.add_attribute(attribute)
            elif parent_id in self._relationship_ids:
                # is an attribute of a relationship
                self._relationship_ids[parent_id].add_attribute(attribute)
            else:
                # is a simple attribute of a composite
                self._attribute_ids[parent_id].add_simple_attribute(attribute)
                
            attribute_id = json_attribute.get("id")
            self._attribute_ids[attribute_id] = attribute

    def _load_json_data(self, file_path: str):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self._json_data = data
        except FileNotFoundError as e:
            print(e.strerror)
        except json.JSONDecodeError as e: 
            print(e.strerror)

    def _create_entity(self, entity_data):
        name = entity_data.get("label")
        entity = Entity(name)
        entity_type = entity_data.get("type")
        if entity_type and entity_type == "Weak":
            entity.set_strong_entity("MISSING_STRONG_ENTITY")
        parent_id = entity_data.get("parentId")

        if parent_id:
            parent = self._entity_ids[parent_id]
            hierarchy = parent.hierarchy
            if not hierarchy:
                hierarchy = self._create_hierarchy()
                parent.set_hierarchy(hierarchy)
            parent.add_child(name)
        else:
            completeness = entity_data.get("totalSpecialization")
            disjointness = entity_data.get("supertypeDefinition")

            if completeness or disjointness:
                hierarchy = self._create_hierarchy(completeness, disjointness)
                entity.set_hierarchy(hierarchy)
            
        return entity

    def _create_hierarchy(self, completeness = None, disjointness = None):
        # default
        hierarchy_completeness = HierarchyCompleteness.PARTIAL
        hierarchy_disjointness = HierarchyDisjointness.DISJOINT

        if completeness:
            hierarchy_completeness = HierarchyCompleteness.TOTAL
        
        if disjointness and disjointness == "Overlapping":
            hierarchy_disjointness = HierarchyDisjointness.OVERLAPPING
        
        return Hierarchy(hierarchy_completeness, hierarchy_disjointness)
    
    def _add_strong_entity(self, entity_from_name: str, entity_to_name: str):
        entity_from = self._entities[entity_from_name]
        entity_to = self._entities[entity_to_name]
        
        if entity_from.strong_entity == "MISSING_STRONG_ENTITY":
            entity_from.set_strong_entity(entity_to_name)
        else:
            entity_to.set_strong_entity(entity_from_name)

    def _create_attribute(self, attribute_data):
        name = attribute_data.get("label")
        attribute_types = attribute_data.get("types")
        attribute_parameters = {} if isinstance(attribute_types, list) else attribute_types 
        min_cardinality = MinimumCardinality.ZERO if attribute_parameters.get("Optional") else MinimumCardinality.ONE
        max_cardinality = MaximumCardinality.MANY if attribute_parameters.get("Multivalued") else MaximumCardinality.ONE

        cardinality = Cardinality(min_cardinality, max_cardinality)
        is_unique = attribute_parameters.get("Unique") or attribute_parameters.get("Partially Unique")
        attribute_type = str #TODO how to define attribute type in ERD PLUS diagram
        composite = attribute_parameters.get("Composite")

        if composite:
            return CompositeAttribute(name, cardinality, attribute_type, is_unique)
        return Attribute(name, cardinality, attribute_type, is_unique)

