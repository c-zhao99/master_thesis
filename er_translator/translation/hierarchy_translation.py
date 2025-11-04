from .sql_generator import SQLGenerator
from ..data.conceptual import *
from ..data.hierachy_checks import HierarchyChecks
from ..data.choices import HIERARCHY_CHOICE
from ..data.constraint import *
from ..utils.utils import get_all_father_entities, create_copy_from_entity, retrieve_connected_relationships, retrieve_children_names

SELECTOR_PREFIX = "TYPE_"

class HierachyTranslator:
    def __init__(self, entities: list[Entity], relationships: list[Relationship]):
        self._entities = entities
        self._relationships = relationships
        self._constraints: dict[str, Constraint] = {}
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


    def translate_hierarchies(self, hierarchy_choices: dict[str, HIERARCHY_CHOICE]):
        father_entities = get_all_father_entities(self._entities.values())

        for father_entity_name in father_entities:
            if father_entity_name in hierarchy_choices:
                self._translate_hierarchy(father_entity_name, hierarchy_choices[father_entity_name])
            else:
                self._translate_hierarchy(father_entity_name)

        for constraint in self._constraints.values():
            self._hierarchy_checks.add_constraint(constraint.entity_name, SQLGenerator.create_sql_constraint(constraint))

    def _translate_hierarchy(self, father_entity_name, choice: HIERARCHY_CHOICE = HIERARCHY_CHOICE.COLLAPSE_UPWARDS):
        father_entity: Entity = self._entities[father_entity_name]
        if choice == HIERARCHY_CHOICE.COLLAPSE_UPWARDS:
            self._collapse_upwards(father_entity)
        else:
            self._collapse_downwards(father_entity)
        
    def _collapse_upwards(self, father_entity: Entity):
        self._create_selectors(father_entity)
        self._create_constraint_and_trigger(father_entity)

        if father_entity.hierarchy.hierarchy_completeness == HierarchyCompleteness.TOTAL and father_entity.hierarchy.hierarchy_disjointness == HierarchyDisjointness.OVERLAPPING:
            self._create_sql_total_constraint(father_entity)


    def _collapse_downwards(self, father_entity: Entity):
        father_relationships = retrieve_connected_relationships([father_entity.name], self._relationships)
        children = father_entity.hierarchy.children

        for relationship_name in father_relationships:
            relationship = self._relationships[relationship_name]
            if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
                self._create_sql_trigger_downwards_relationship(relationship, father_entity, children)
            elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
                if relationship.entity_from == father_entity.name:
                    self._create_sql_constraint_downwards(relationship.entity_to, relationship_name, father_entity)
                else:
                    self._create_sql_trigger_downwards_child(relationship, father_entity, children)
            else:
                if relationship.entity_to == father_entity.name:
                    self._create_sql_constraint_downwards(relationship.entity_from, relationship_name, father_entity)
                else:
                    self._create_sql_trigger_downwards_child(relationship, father_entity, children)
      
                
                

    def _create_selectors(self, father_entity: Entity):
        selectors = {}
        hierarchy = father_entity.hierarchy
        children = hierarchy.children
        if hierarchy.hierarchy_disjointness == HierarchyDisjointness.DISJOINT:
            selector_name = SELECTOR_PREFIX
            selector_values = []
            for child_name in children:
                selector_name += child_name
                selector_values.append(child_name)
            if hierarchy.hierarchy_completeness == HierarchyCompleteness.PARTIAL:
                selector_values.append(father_entity.name)
            selectors[selector_name] = selector_values
        else:
            for child_name in children:
                selector_name = SELECTOR_PREFIX + child_name
                selectors[selector_name] = ["0", "1"]
        
        for selector_name, selector_values in selectors.items():
            selector = SQLGenerator.create_sql_selector(selector_name, selector_values)
            self._hierarchy_checks.add_selector(father_entity.name, selector)

    
    def _create_constraint_and_trigger(self, father_entity: Entity):
        children_names = retrieve_children_names(father_entity)
        hierarchy_relationships = retrieve_connected_relationships(children_names, self._relationships)

        for relationship_name in hierarchy_relationships:
            relationship = self._relationships[relationship_name]
            self._check_relationship(relationship, children_names, father_entity)

    

    
    
    def _check_relationship(self, relationship: Relationship, children_names: list[str], father: Entity):
        if relationship.entity_from in children_names and relationship.entity_to in children_names:
            self._check_relationship_cardinality_both_child(relationship, father)
        elif relationship.entity_from in children_names:
            self._check_relationship_cardinality_from_child(relationship, father)
        else:
            self._check_relationship_cardinality_to_child(relationship, father)

    def _check_relationship_cardinality_both_child(self, relationship: Relationship, father: Entity):
       
        entity_from = self._entities[relationship.entity_from]
        entity_to = self._entities[relationship.entity_to]
        
        if entity_from.name == entity_to.name:
            self._check_recursive_relationship_child_cardinality(relationship, father, entity_from)
        else:
            if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
                self._create_sql_trigger(relationship, relationship.name, father, entity_from, entity_to)
                self._create_sql_trigger(relationship, relationship.name, father, entity_to, entity_from)
            elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
                self._create_sql_trigger(relationship, father.name, father, entity_from, entity_to)
                self._create_sql_constraint(relationship, father, entity_to)
            else:
                self._create_sql_trigger(relationship, father.name, father, entity_to, entity_from)
                self._create_sql_constraint(relationship, father, entity_from)

    def _check_recursive_relationship_child_cardinality(self, relationship: Relationship, father: Entity, entity_from: Entity):
        if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
            self._create_sql_trigger(relationship, relationship.name, father, entity_from, entity_from, "_A")
            self._create_sql_trigger(relationship, relationship.name, father, entity_from, entity_from, "_B")
        else:
            self._create_sql_trigger(relationship, father.name, father, entity_from, entity_from)
            self._create_sql_constraint(relationship, father, entity_from)

    def _check_relationship_cardinality_from_child(self, relationship: Relationship, father: Entity):
        entity_from = self._entities[relationship.entity_from]
        entity_to = self._entities[relationship.entity_to]
        
        if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
            self._create_sql_trigger(relationship, relationship.name, father, entity_from)
        elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
            self._create_sql_trigger(relationship, entity_to.name, father, entity_from)
        else:
            self._create_sql_constraint(relationship, father, entity_from)

    def _check_relationship_cardinality_to_child(self, relationship: Relationship, father: Entity):
        
        entity_from = self._entities[relationship.entity_from]
        entity_to = self._entities[relationship.entity_to]
        
        if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
            self._create_sql_trigger(relationship, relationship.name, father, entity_to)
        elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
            self._create_sql_constraint(relationship, father, entity_to)
        else:
            self._create_sql_trigger(relationship, entity_from.name, father, entity_to)
    
    def _create_sql_trigger(self, relationship: Relationship, table_name: str, father: Entity, connected_child: Entity, other_child: Entity = None, identifier_modifier: str = ""):
        hierarchy = father.hierarchy
        
        if hierarchy.hierarchy_disjointness == HierarchyDisjointness.OVERLAPPING:
            selector_name = self._get_selector_name(father, connected_child)
        else:
            selector_name = self._get_selector_name(father)
        if other_child:
            if identifier_modifier != "":
                sql_trigger = SQLGenerator.create_sql_trigger_before_insert(relationship, table_name, father, connected_child, selector_name, other_child, identifier_modifier)
            else:
                sql_trigger = SQLGenerator.create_sql_trigger_before_insert(relationship, table_name, father, connected_child, selector_name, other_child)
        else:
            sql_trigger = SQLGenerator.create_sql_trigger_before_insert(relationship, table_name, father, connected_child, selector_name)
        self._hierarchy_checks.add_trigger(sql_trigger)

    def _create_sql_constraint(self, relationship: Relationship, father: Entity, connected_child: Entity):
        hierarchy = father.hierarchy

        if hierarchy.hierarchy_disjointness == HierarchyDisjointness.OVERLAPPING:
            for child_name in hierarchy.children:
                child_entity = self._entities[child_name]
                constraint_name = child_name
                selector_name = self._get_selector_name(father, child_entity)
                if child_name == connected_child.name:
                    conditions = self._get_sql_constraint_values_overlapping(relationship, father, connected_child)
                else:
                    conditions = self._get_sql_constraint_values_overlapping_child(child_entity)
                constraint = Constraint(father.name, constraint_name, selector_name, conditions)
                self._add_constraint(constraint)
        else:
            constraint_name = "".join(retrieve_children_names(father))
            selector_name = self._get_selector_name(father)
            conditions = self._get_sql_constraint_values_disjoint(relationship, father, connected_child)
            constraint = Constraint(father.name, constraint_name, selector_name, conditions)
            self._add_constraint(constraint)
            

    def _add_constraint(self, constraint: Constraint):
        constraint_name = constraint.constraint_name
        if constraint_name in self._constraints:
            self._constraints[constraint_name].add_conditions(constraint.conditions)
        else:
            self._constraints[constraint_name] = constraint

    def _create_sql_total_constraint(self, father: Entity):
        children_names = retrieve_children_names(father)
        sql_constraint = SQLGenerator.create_sql_total_constraint(children_names)
        self._hierarchy_checks.add_constraint(father.name, sql_constraint)


    def _get_selector_name(self, father: Entity, child: Entity = None):
        if child:
            return SELECTOR_PREFIX + child.name
        else:
            children_names = retrieve_children_names(father)
            return SELECTOR_PREFIX + "".join(children_names)
    
    def _get_foreign_key_name(self, relationship: Relationship, child: Entity, primary_key: Attribute):
        # Get the other entity in the relationship (the one being referenced)
        if relationship.entity_from == child.name:
            other_entity_name = relationship.entity_to
        else:
            other_entity_name = relationship.entity_from
        return other_entity_name + "_" + primary_key.name

    def _get_sql_constraint_values_disjoint(self, relationship: Relationship, father: Entity, connected_child: Entity) -> list[Condition]:
        conditions = []
        foreign_keys = []
        relationship_attributes = []
        is_relationship_optional = self._is_optional_child_entity_relationship(relationship, connected_child)
        
        # Create foreign keys for father's identifiers
        for identifier in father.identifiers:
            foreign_key_name = self._get_foreign_key_name(relationship, connected_child, identifier)
            min_cardinality = MinimumCardinality.ZERO if is_relationship_optional else MinimumCardinality.ONE 
            cardinality = Cardinality(min_cardinality, MaximumCardinality.ONE)
            foreign_key = Attribute(foreign_key_name, cardinality, True)
            foreign_keys.append(foreign_key)
        
        # Create attributes for relationship's attributes
        for rel_attribute in relationship.attributes:
            # Relationship attributes are always optional in hierarchy collapse
            attr_name = connected_child.name + "_" + rel_attribute.name
            min_card = MinimumCardinality.ZERO if is_relationship_optional else rel_attribute.cardinality.min_cardinality
            cardinality = Cardinality(min_card, rel_attribute.cardinality.max_cardinality)
            relationship_attr = Attribute(attr_name, cardinality, rel_attribute.is_unique)
            relationship_attributes.append(relationship_attr)
        
        hierarchy = father.hierarchy
        for child_name in hierarchy.children:
            child_entity = self._entities[child_name]
            checks = []
            checks += self._get_not_null_checks(child_entity.identifiers)
            checks += self._get_not_null_checks(child_entity.attributes)

            if child_name == connected_child.name:
                checks += self._get_not_null_checks(foreign_keys)
                checks += self._get_not_null_checks(relationship_attributes)
            else:
                checks += self._get_null_checks(foreign_keys)
                checks += self._get_null_checks(relationship_attributes)
            
            for other_child_name in hierarchy.children:
                if child_name != other_child_name:
                    other_child_entity = self._entities[other_child_name]
                    checks += self._get_null_checks(other_child_entity.identifiers)
                    checks += self._get_null_checks(other_child_entity.attributes)
            
            condition = Condition(child_name, checks)
            conditions.append(condition)
        
        if hierarchy.hierarchy_completeness == HierarchyCompleteness.PARTIAL:
            checks = []
            for child_name in hierarchy.children:
                child_entity = self._entities[child_name]
                checks += self._get_null_checks(child_entity.identifiers)
                checks += self._get_null_checks(child_entity.attributes)
                
            checks += self._get_null_checks(foreign_keys)
            checks += self._get_null_checks(relationship_attributes)
            
            condition = Condition(father.name, checks)
            conditions.append(condition)
        
        return conditions
    
    def _is_optional_child_entity_relationship(self, relationship: Relationship, child: Entity):
        if relationship.entity_from == child.name and relationship.cardinality_from.min_cardinality == MinimumCardinality.ZERO:
            return True
        elif relationship.entity_to == child.name and relationship.cardinality_to.min_cardinality == MinimumCardinality.ZERO:
            return True
        return False
    def _get_sql_constraint_values_overlapping(self, relationship: Relationship, father: Entity, connected_child: Entity) -> list[Condition]:
        conditions = []
        foreign_keys = []
        relationship_attributes = []
        is_relationship_optional = self._is_optional_child_entity_relationship(relationship, connected_child)
        
        # Create foreign keys for father's identifiers
        for identifier in father.identifiers:
            foreign_key_name = self._get_foreign_key_name(relationship, connected_child, identifier)
            min_cardinality = MinimumCardinality.ZERO if is_relationship_optional else MinimumCardinality.ONE 
            cardinality = Cardinality(min_cardinality, MaximumCardinality.ONE)
            foreign_key = Attribute(foreign_key_name, cardinality, True)
            foreign_keys.append(foreign_key)
        
        # Create attributes for relationship's attributes
        for rel_attribute in relationship.attributes:
            # Relationship attributes are always optional in hierarchy collapse
            attr_name = connected_child.name + "_" + rel_attribute.name
            min_card = MinimumCardinality.ZERO if is_relationship_optional else rel_attribute.cardinality.min_cardinality
            cardinality = Cardinality(min_card, rel_attribute.cardinality.max_cardinality)
            relationship_attr = Attribute(attr_name, cardinality, rel_attribute.is_unique)
            relationship_attributes.append(relationship_attr)
        
        selector_value = 1

        checks = []
        checks += self._get_not_null_checks(connected_child.identifiers)
        checks += self._get_not_null_checks(connected_child.attributes)
        checks += self._get_not_null_checks(foreign_keys)
        checks += self._get_not_null_checks(relationship_attributes)
        
        condition = Condition(selector_value, checks)
        conditions.append(condition)

        selector_value = 0

        checks = []
        checks += self._get_null_checks(connected_child.identifiers)
        checks += self._get_null_checks(connected_child.attributes)
        checks += self._get_null_checks(foreign_keys)
        checks += self._get_null_checks(relationship_attributes)
        
        condition = Condition(selector_value, checks)
        conditions.append(condition)

        return conditions
    
    def _get_sql_constraint_values_overlapping_child(self, child: Entity) -> list[Condition]:
        conditions = []
        
        selector_value = 1
        checks = []
        checks += self._get_not_null_checks(child.identifiers)
        checks += self._get_not_null_checks(child.attributes)
        
        condition = Condition(selector_value, checks)
        conditions.append(condition)

        selector_value = 0
        checks = []
        checks += self._get_null_checks(child.identifiers)
        checks += self._get_null_checks(child.attributes)
        
        condition = Condition(selector_value, checks)
        conditions.append(condition)

        return conditions

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
    
    def _get_null_checks(self, attributes: list[Attribute]) -> list[Check]:
        checks = []
        for attribute in attributes:
            check = Check(attribute.name, True)
            checks.append(check)

        return checks
    
    def _get_not_null_checks(self, attributes: list[Attribute]) -> list[Check]:
        checks = []
        for attribute in attributes:
            if attribute.cardinality.min_cardinality == MinimumCardinality.ONE:
                check = Check(attribute.name, False)
                checks.append(check)

        return checks

    def _create_sql_constraint_downwards(self, entity_name: str, relationship_name: str, father: Entity):
        relationship = self._relationships[relationship_name]
        
        conditions = []
        
        for child_name in father.hierarchy.children:
            checks = []
            father_ids = self._get_identifier_names(father)
            for id in father_ids:
                check = f"{child_name}_{id} IS NOT NULL"
                checks.append(check)
            
            # Add mandatory relationship attributes checks for this child
            for rel_attribute in relationship.attributes:
                if rel_attribute.cardinality.min_cardinality == MinimumCardinality.ONE:
                    attr_name = f"{relationship_name}_{rel_attribute.name}"
                    check = f"{attr_name} IS NOT NULL"
                    checks.append(check)
            
            for other_child_name in father.hierarchy.children:
                if child_name != other_child_name:
                    for id in father_ids:
                        check = f"{other_child_name}_{id} IS NULL"
                        checks.append(check)
                    
                    # Add relationship attributes checks for other children (all must be NULL)
                    for rel_attribute in relationship.attributes:
                        attr_name = f"{relationship_name}_{rel_attribute.name}"
                        check = f"{attr_name} IS NULL"
                        checks.append(check)

            condition = " AND ".join(checks)
            conditions.append(f"({condition})")
        sql_constraint = SQLGenerator.create_sql_downwards_constraint(relationship_name, conditions)
        self._hierarchy_checks.add_constraint(entity_name, sql_constraint)

    def _create_sql_trigger_downwards_relationship(self, relationship: Relationship, father: Entity, children: list[str]):
        relationship_name = relationship.name
        entity_from = relationship.entity_from
        entity_to = relationship.entity_to
        from_side_father = entity_from == father.name
        for child_name in children:
            for other_child_name in children:
                if child_name == other_child_name:
                    continue
                father_ids = self._get_identifier_names(father)
                checks = []
                if from_side_father:
                    other_relationship_table = relationship_name + "_" + other_child_name + "_" + entity_to
                else:
                    other_relationship_table = relationship_name + "_" + other_child_name + "_" + entity_from
                for id in father_ids:
                    check = f"N.{child_name}_{id} = {other_relationship_table}.{other_child_name}_{id}"
                    checks.append(check)
                conditions = " OR ".join(checks)
                if from_side_father:
                    relationship_table = relationship_name + "_" + child_name + "_" + entity_to
                else:
                    relationship_table = relationship_name + "_" + child_name + "_" + entity_from
                self._create_sql_trigger_downwards(relationship.name, relationship_table, other_relationship_table, conditions)

    def _create_sql_trigger_downwards_child(self, relationship: Relationship, father: Entity, children: list[str]):
        other_entity_name = relationship.entity_to if relationship.entity_from == father.name else relationship.entity_from
        
        for child_name in children:
            for other_child_name in children:
                if child_name == other_child_name:
                    continue
                checks = []
                for identifier in father.identifiers:
                    check = f"N.{identifier.name} = {other_child_name}.{identifier.name}"
                    checks.append(check)
                conditions = " OR ".join(checks)
                
                self._create_sql_trigger_downwards(relationship.name, child_name, other_child_name, conditions)

                    
    def _create_sql_trigger_downwards(self, relationship_name: str, table_name: str, other_table_name: str, conditions: str):        
        sql_trigger = SQLGenerator.create_sql_downwards_trigger(relationship_name, table_name, other_table_name, conditions)
        self._hierarchy_checks.add_trigger(sql_trigger)
