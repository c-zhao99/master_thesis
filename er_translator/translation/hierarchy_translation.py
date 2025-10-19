from .sql_generator import SQLGenerator
from ..data.conceptual import *
from ..data.hierachy_checks import HierarchyChecks
from ..data.choices import HIERARCHY_CHOICE
from ..utils.utils import create_copy_from_entity


SELECTOR_PREFIX = "TYPE_"

class HierachyTranslator:
    def __init__(self, entities: list[Entity], relationships: list[Relationship]):
        self._entities = entities
        self._relationships = relationships
        self._hierarchy_checks = HierarchyChecks()
        
    
    @property
    def entities(self):
        return self._entities
    
    @property
    def relationships(self):
        return self._relationships
    
    @property
    def hierarchy_checks(self):
        return self._hierarchy_checks


    def translate_hierarchies(self):
        father_entities = []

        for entity in self._entities.values():
            if entity.hierarchy:
                father_entities.append(entity.name)
        
        for father_entity in father_entities:
            self._translate_hierarchy(father_entity)

    def _translate_hierarchy(self, father_entity_name, choice: HIERARCHY_CHOICE = HIERARCHY_CHOICE.COLLAPSE_UPWARDS):
        father_entity: Entity = self._entities[father_entity_name]
        if choice == HIERARCHY_CHOICE.COLLAPSE_UPWARDS:
            self._collapse_upwards(father_entity)
        else:
            self._collapse_downwards(father_entity)
        
    def _collapse_upwards(self, father_entity: Entity):
        self._create_selectors(father_entity)
        self._create_constraint_and_trigger(father_entity)


    def _collapse_downwards(self, father_entity: Entity):
        pass


    def _create_selectors(self, father_entity: Entity):
        selectors = {}
        hierarchy = father_entity.hierarchy
        children = hierarchy.children
        if hierarchy.hierarchy_disjointness == HierarchyDisjointness.DISJOINT:
            selector_name = SELECTOR_PREFIX
            selector_values = []
            for child in children:
                child_name = child.name
                selector_name += child_name
                selector_values.append(child_name)
            if hierarchy.hierarchy_completeness == HierarchyCompleteness.PARTIAL:
                selector_values.append(father_entity.name)
            selectors[selector_name] = selector_values
        else:
            for child in children:
                child_name = child.name
                selector_name = SELECTOR_PREFIX + child_name
                selectors[selector_name] = ["0", child_name]
        
        for selector_name, selector_values in selectors.items():
            selector = SQLGenerator.create_sql_selector(selector_name, selector_values)
            self._hierarchy_checks.add_selector(selector)

    
    def _create_constraint_and_trigger(self, father_entity: Entity):
        children_names = self._retrieve_children_names(father_entity)
        hierarchy_relationships = self._retrieve_relationships(children_names)

        for relationship in hierarchy_relationships:
            self._check_relationship(relationship, children_names, father_entity)

    def _retrieve_children_names(self, father_entity: Entity) -> set[str]:
        children_names = set()
        for child in father_entity.hierarchy.children:
            children_names.add(child.name)

        return children_names

    def _retrieve_relationships(self, entity_names: list[str]) -> list[Relationship]:
        relationships = []

        for relationship in self._relationships.values():
            
            if relationship.entity_from in entity_names or relationship.entity_to in entity_names:
                relationships.append(relationship)

        return relationships
    
    def _check_relationship(self, relationship: Relationship, children_names: list[str], father: Entity):
        if relationship.entity_from in children_names and relationship.entity_to in children_names:
            self._check_relationship_cardinality_both_child(relationship, father)
        elif relationship.entity_from in children_names:
            self._check_relationship_cardinality_from_child(relationship, father)
        else:
            self._check_relationship_cardinality_to_child(relationship, father)

    def _check_relationship_cardinality_both_child(self, relationship: Relationship, father: Entity):
        new_entity = Entity(relationship.name)
        entity_from = self._entities[relationship.entity_from]
        entity_to = self._entities[relationship.entity_to]
        
        other_child = father.hierarchy.children[0] if father.hierarchy.children[0].name != entity_from.name else father.hierarchy.children[1]
        if entity_from.name == entity_to.name:
            self._check_recursive_relationship_child_cardinality(relationship, father, new_entity, entity_from, other_child)
        else:
            if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
                foreign_key = self._get_foreign_key_name(relationship, entity_from, father.identifiers[0])
                self._create_sql_trigger(relationship, new_entity, father, entity_from, foreign_key)
                foreign_key = self._get_foreign_key_name(relationship, other_child, father.identifiers[0])
                self._create_sql_trigger(relationship, new_entity, father, other_child, foreign_key)
            elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
                foreign_key = self._get_foreign_key_name(relationship, entity_from, father.identifiers[0])
                self._create_sql_trigger(relationship, father, father, entity_from, foreign_key, other_child)
                self._create_sql_constraint(relationship, father, other_child, entity_from)
            else:
                foreign_key = self._get_foreign_key_name(relationship, other_child, father.identifiers[0])
                self._create_sql_trigger(relationship, father, father, other_child, foreign_key, entity_from)
                self._create_sql_constraint(relationship, father, entity_from, other_child)

    def _check_recursive_relationship_child_cardinality(self, relationship: Relationship, father: Entity, new_entity: Entity, entity_from: Entity, other_child: Entity):
        if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
            foreign_key = self._get_foreign_key_name(relationship, entity_from, father.identifiers[0])
            self._create_sql_trigger(relationship, new_entity, father, entity_from, foreign_key+"_A")
            self._create_sql_trigger(relationship, new_entity, father, entity_from, foreign_key+"_B")
        else:
            foreign_key = self._get_foreign_key_name(relationship, entity_from, father.identifiers[0])
            self._create_sql_trigger(relationship, father, father, entity_from, foreign_key, entity_from)
            self._create_sql_constraint(relationship, father, entity_from, other_child)

    def _check_relationship_cardinality_from_child(self, relationship: Relationship, father: Entity):
        new_entity = Entity(relationship.name)
        entity_from = self._entities[relationship.entity_from]
        entity_to = self._entities[relationship.entity_to]
        other_child = father.hierarchy.children[0] if father.hierarchy.children[0].name != entity_from.name else father.hierarchy.children[1]
        if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
            foreign_key = self._get_foreign_key_name(relationship, entity_from, father.identifiers[0])
            self._create_sql_trigger(relationship, new_entity, father, entity_from, foreign_key)
        elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
            foreign_key = self._get_foreign_key_name(relationship, entity_from, father.identifiers[0])
            self._create_sql_trigger(relationship, entity_to, father, entity_from, foreign_key)
        else:
            self._create_sql_constraint(relationship, entity_to, entity_from, other_child)

    def _check_relationship_cardinality_to_child(self, relationship: Relationship, father: Entity):
        new_entity = Entity(relationship.name)
        entity_from = self._entities[relationship.entity_from]
        entity_to = self._entities[relationship.entity_to]
        other_child = father.hierarchy.children[0] if father.hierarchy.children[0].name != entity_to.name else father.hierarchy.children[1]
        if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
            foreign_key = self._get_foreign_key_name(relationship, entity_to, father.identifiers[0])
            self._create_sql_trigger(relationship, new_entity, father, entity_to, foreign_key)
        elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
            self._create_sql_constraint(relationship, entity_from, entity_to, other_child)
        else:
            foreign_key = self._get_foreign_key_name(relationship, entity_to, father.identifiers[0])
            self._create_sql_trigger(relationship, entity_from, father, entity_to, foreign_key)
    
    def _create_sql_trigger(self, relationship: Relationship, table: Entity, father: Entity, child: Entity, foreign_key: str, other_child: Entity = None):
        selector_name = self._get_selector_name(father)
        
        if other_child:
            sql_trigger = SQLGenerator.create_sql_trigger_before_insert(relationship, table, father, child, selector_name, foreign_key, other_child)
        else:
            sql_trigger = SQLGenerator.create_sql_trigger_before_insert(relationship, table, father, child, selector_name, foreign_key)
        self._hierarchy_checks.add_trigger(sql_trigger)

    def _create_sql_constraint(self, relationship: Relationship, father: Entity, connected_child: Entity, other_child: Entity):
        selector_name = self._get_selector_name(father)
        constraint_values = self._get_sql_constraint_values(relationship, father, connected_child, other_child)
        sql_constraint = SQLGenerator.create_sql_constraint(selector_name, constraint_values)
        self._hierarchy_checks.add_constraint(sql_constraint)

    def _get_selector_name(self, father: Entity):
        children_names = self._retrieve_children_names(father)
        return SELECTOR_PREFIX + "".join(children_names)
    
    def _get_foreign_key_name(self, relationship: Relationship, child: Entity, primary_key: Attribute):
        return relationship.name + child.name + primary_key.name

    def _get_sql_constraint_values(self, relationship: Relationship, father: Entity, connected_child: Entity, other_child: Entity) -> dict[str, str]:
        constraints = {}
        foreign_key = self._get_foreign_key_name(relationship, connected_child, father.identifiers[0])
        connected_child_ids = self._get_identifier_names(connected_child)
        connected_child_attrs = self._get_attributes_names(connected_child)
        connected_child_attrs.append(foreign_key)
        other_child_ids = self._get_identifier_names(other_child)
        other_child_attrs = self._get_attributes_names(other_child)
        
        constraints[connected_child.name] = self._get_not_null_constraint_values(connected_child_ids + connected_child_attrs) + " AND " + self._get_null_constraint_values(other_child_ids + other_child_attrs)
        constraints[other_child.name] = self._get_not_null_constraint_values(other_child_ids + other_child_attrs) + " AND " + self._get_null_constraint_values(connected_child_ids + connected_child_attrs)
        
        return constraints

    def _get_identifier_names(self, entity: Entity):
        names = []
        for identifier in entity.identifiers:
            names.append(identifier.name)

        return names

    def _get_attributes_names(self, entity: Entity):
        names = []
        for attribute in entity.attributes:
            names.append(attribute.name)

        return names
    
    def _get_null_constraint_values(self, attributes: list[str]) -> str:
        constraint = ""
        for attribute in attributes:
            constraint += (attribute + " IS NULL AND ")

        return constraint[:-5]
    
    def _get_not_null_constraint_values(self, attributes: list[str]) -> str:
        constraint = ""
        for attribute in attributes:
            constraint += (attribute + " IS NOT NULL AND ")

        return constraint[:-5]







'''
def add_constraints(old, new):
    for key, value in new.items():
        if key in old:
            old[key] = old[key] + " AND " + value
        else:
            old[key] = value
'''






'''
def collapse_upwards_total_exclusive():
    entities, relationships = create_diagram()
    

    sql_attributes = []
    sql_primary_keys = ["A1"]
    sql_selectors = []
    sql_references = []
    sql_constraints = []
    sql_triggers = []
    optional = "NOT NULL"

    #attributes
    
    e1 = entities["E1"]
    hierarchy = entities["E1"].hierarchy
    children_entities = hierarchy.children
    entities_to_iterate = [e1] + children_entities
    for entity in entities_to_iterate:
        id = entity.identifiers[0]
        sql_attributes.append(create_sql_attribute(id.name))
    
    #selector
    children = []
    for child in children_entities:
        children.append(child.name)
    selector_name = "TIPO" + "".join(children)
    values = ",".join(children)
    sql_selectors.append(create_sql_selector(selector_name, values))

    #relationships
    values = {}
    for relationship in relationships.values():
        if relationship.entity_from in children and relationship.entity_to in children:
            entity = relationship.entity_from
            if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
                entity_from = relationship.entity_from
                entity_to = relationship.entity_to
                entity_from_name = relationship.name + entities[entity_from].identifiers[0].name
                entity_to_name = relationship.name + entities[entity_to].identifiers[0].name
                new_sql_references = []
                new_sql_references.append(create_sql_reference(create_sql_attribute(entity_from_name), "E1", "A1"))
                new_sql_references.append(create_sql_reference(create_sql_attribute(entity_to_name), "E1", "A1"))
                new_primary_keys = [entity_from_name, entity_to_name]

                print(create_sql_table(relationship.name, [], [], new_sql_references, new_primary_keys, []))

                new_entity = Entity(relationship.name)
                for key in new_primary_keys:
                    new_entity.add_identifier(Attribute(key, Cardinality(
                        MinimumCardinality.ONE,
                        MaximumCardinality.ONE
                    ), True))
                foreign_key = entity_from_name
                trigger = create_sql_trigger_before_insert(relationships[relationship.name], new_entity, entities["E1"], entities[entity_from], entities["E1"], selector_name, foreign_key)
                print(trigger)

                foreign_key2 = entity_to_name
                trigger2 = create_sql_trigger_before_insert(relationships[relationship.name], new_entity, entities["E1"], entities[entity_to], entities["E1"], selector_name, foreign_key2)
                print(trigger2)

            elif relationship.cardinality_from.max_cardinality == MaximumCardinality.ONE:
                other_child = relationship.entity_to
                

                new_values = get_sql_constraint_values_on_child(entities[entity], entities[other_child], relationship.name, relationship.entity_to)
                add_constraints(values, new_values)
                foreign_key = relationship.name + entities[relationship.entity_from].identifiers[0].name
                trigger = create_sql_trigger_before_insert(relationships[relationship.name], entities["E1"], entities["E1"], entities[other_child], entities[relationship.entity_from], selector_name, foreign_key)
                sql_triggers.append(trigger)
            else:
                foreign_key = relationship.name + entities[relationship.entity_to].identifiers[0].name
                trigger = create_sql_trigger_before_insert(relationships[relationship.name], entities["E1"], entities["E1"], entities[entity], entities[relationship.entity_to], selector_name, foreign_key)
                sql_triggers.append(trigger)

                new_values = get_sql_constraint_values_on_child(entities[entity], entities[entity], relationship.name, relationship.entity_from)
                add_constraints(values, new_values)
            sql_reference = create_sql_reference(create_sql_attribute(relationship.name + "A1"), "E1", "A1")
            sql_references.append(sql_reference)
        elif relationship.entity_from in children:
            entity = relationship.entity_from
            if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
                entity_from = relationship.entity_from
                entity_to = relationship.entity_to
                entity_from_name = relationship.name + entities[entity_from].identifiers[0].name
                entity_to_name = relationship.name + entities[entity_to].identifiers[0].name
                new_sql_references = []
                new_sql_references.append(create_sql_reference(create_sql_attribute(entity_from_name), "E1", "A1"))
                new_sql_references.append(create_sql_reference(create_sql_attribute(entity_to_name), "E1", "A1"))
                new_primary_keys = [entity_from_name, entity_to_name]

                print(create_sql_table(relationship.name, [], [], new_sql_references, new_primary_keys, []))

                new_entity = Entity(relationship.name)
                for key in new_primary_keys:
                    new_entity.add_identifier(Attribute(key, Cardinality(
                        MinimumCardinality.ONE,
                        MaximumCardinality.ONE
                    ), True))
                if relationship.entity_from == "E1":
                    foreign_key2 = entity_to_name
                    trigger2 = create_sql_trigger_before_insert(relationships[relationship.name], new_entity, entities["E1"], entities[entity_to], entities["E1"], selector_name, foreign_key2)
                    print(trigger2)
                else:
                    foreign_key = entity_from_name
                    trigger = create_sql_trigger_before_insert(relationships[relationship.name], new_entity, entities["E1"], entities[entity_from], entities["E1"], selector_name, foreign_key)
                    print(trigger)
                    
            elif relationship.cardinality_from.max_cardinality == MaximumCardinality.ONE:

                other_child = "E2" if entity == "E3" else "E3"
                new_values = get_sql_constraint_values_on_child(entities[entity], entities[other_child], relationship.name, relationship.entity_to)
                add_constraints(values, new_values)
            else:
                foreign_key = relationship.name + entities[relationship.entity_to].identifiers[0].name
                trigger = create_sql_trigger_before_insert(relationships[relationship.name], entities["E1"], entities["E1"], entities[entity], entities[relationship.entity_to], selector_name, foreign_key)
                sql_triggers.append(trigger)
            sql_reference = create_sql_reference(create_sql_attribute(relationship.name + "A1"), "E1", "A1")
            sql_references.append(sql_reference)
        elif relationship.entity_to in children:
            entity = relationship.entity_to
            if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
                entity_from = relationship.entity_from
                entity_to = relationship.entity_to
                entity_from_name = relationship.name + entities[entity_from].identifiers[0].name
                entity_to_name = relationship.name + entities[entity_to].identifiers[0].name
                new_sql_references = []
                new_sql_references.append(create_sql_reference(create_sql_attribute(entity_from_name), "E1", "A1"))
                new_sql_references.append(create_sql_reference(create_sql_attribute(entity_to_name), "E1", "A1"))
                new_primary_keys = [entity_from_name, entity_to_name]

                print(create_sql_table(relationship.name, [], [], new_sql_references, new_primary_keys, []))

                new_entity = Entity(relationship.name)
                for key in new_primary_keys:
                    new_entity.add_identifier(Attribute(key, Cardinality(
                        MinimumCardinality.ONE,
                        MaximumCardinality.ONE
                    ), True))
                if relationship.entity_from == "E1":
                    foreign_key2 = entity_to_name
                    trigger2 = create_sql_trigger_before_insert(relationships[relationship.name], new_entity, entities["E1"], entities[entity_to], entities["E1"], selector_name, foreign_key2)
                    print(trigger2)
                else:
                    foreign_key = entity_from_name
                    trigger = create_sql_trigger_before_insert(relationships[relationship.name], new_entity, entities["E1"], entities[entity_from], entities["E1"], selector_name, foreign_key)
                    print(trigger)
            elif relationship.cardinality_to.max_cardinality == MaximumCardinality.ONE:
                
                other_child = "E2" if entity == "E3" else "E3"
                new_values = get_sql_constraint_values_on_child(entities[entity], entities[other_child], relationship.name, relationship.entity_from)

                add_constraints(values, new_values)

            else:
                foreign_key = relationship.name + entities[relationship.entity_from].identifiers[0].name
                trigger = create_sql_trigger_before_insert(relationships[relationship.name], entities["E1"], entities["E1"], entities[entity], entities[relationship.entity_from], selector_name, foreign_key)
                sql_triggers.append(trigger)
            sql_reference = create_sql_reference(create_sql_attribute(relationship.name + "A1"), "E1", "A1")
            sql_references.append(sql_reference)
    constraint = create_sql_constraint(selector_name, values)
    sql_constraints.append(constraint)
    print(create_sql_table("E1", sql_attributes, sql_selectors, sql_references, sql_primary_keys, sql_constraints))
    for trigger in sql_triggers:
        print(trigger)
'''