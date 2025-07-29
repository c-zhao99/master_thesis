from data.conceptual import MinimumCardinality, MaximumCardinality, Cardinality, HierarchyCompleteness, HierarchyDisjointness, Entity, Hierarchy, Relationship, Attribute as C_Attribute, CompositeAttribute
from data.relational import Table, Attribute as R_Attribute, ForeignKey
from data.choices import COMPOSITE_ATTRIBUTE_CHOICE, RELATIONSHIP_CHOICE

# helper functions
def translate_attribute(conceptual_attribute: C_Attribute) -> R_Attribute:
    # Translate conceptual attribute to relational attribute
    isOptional = True if conceptual_attribute.cardinality.min_cardinality == MinimumCardinality.ZERO else False
    
    return R_Attribute(conceptual_attribute.name, conceptual_attribute.attribute_type, isOptional, conceptual_attribute.is_unique)

def add_foreign_keys_and_attributes(main_table: Table, referenced_table: Table, attributes: list[C_Attribute]) -> None:
    for key in referenced_table.primary_key:
        main_table.add_foreign_key(key)
        
    for attribute in attributes:
        main_table.add_attribute(translate_attribute(attribute))

def merge_tables_into_one(main_table: Table, secondary_table: Table, attributes: list[C_Attribute]) -> Table:
    new_name = main_table.name + secondary_table.name
    new_primary_keys = main_table.primary_key
    new_attributes = main_table.attributes + secondary_table.attributes
    for attribute in attributes:
        new_attributes.append(translate_attribute(attribute))
    
    new_table = Table(new_name, new_primary_keys, new_attributes)

    new_foreign_keys = main_table.foreign_key + secondary_table.foreign_key
    for foreign_key in new_foreign_keys:
        new_table.add_foreign_key(foreign_key)
    
    return new_table


# Translation steps:
# 1. Eliminate hierarchies TODO

# 2. Normalize composite attributes
# Three possibilities:
# - Keep simple attributes
# - Have one single main attribute
# - Create new entity (mandatory when cardinality is n)

def get_composite_attributes_choices(entity: Entity, attribute: C_Attribute, choices: dict[str, dict[str, set[COMPOSITE_ATTRIBUTE_CHOICE]]]) -> None:
    if isinstance(attribute, CompositeAttribute):
        if entity.name in choices:
            choices[entity.name][attribute.name] = {COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE, COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES}
        else:
            choices[entity.name] = {attribute.name: {COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE}}

def normalize_attribute(entity: Entity, attribute: C_Attribute, choice: COMPOSITE_ATTRIBUTE_CHOICE = None):
    if isinstance(attribute, CompositeAttribute) and attribute.cardinality.max_cardinality == MaximumCardinality.MANY:
        if choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE:

            # Create a new object of C_Attribute(conceptual attribute) to limit access to child class (CompositeAttribute) attributes
            # In a statically typed language like Java it could just be converted to parent class, but can't do that in a dynamically typed language like Python

            normalize_multi_value_attribute(entity, C_Attribute(attribute.name, attribute.cardinality, attribute.attribute_type, attribute.is_unique))
        elif choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES:
            simple_attributes = attribute.simple_attributes
            for simple_attribute in simple_attributes:

                normalize_multi_value_attribute(simple_attribute)
                #TODO: remove attribute and add relationships
                
    elif isinstance(attribute, CompositeAttribute):
        normalize_composite_attribute(attribute, choice)
    elif attribute.cardinality.max_cardinality == MaximumCardinality.MANY:
        normalize_multi_value_attribute(entity, attribute)


def normalize_composite_attribute(composite_attribute: CompositeAttribute, choice: COMPOSITE_ATTRIBUTE_CHOICE):
    if choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE:
        # Keep composite attribute

        # Create a new object of C_Attribute(conceptual attribute) to limit access to child class (CompositeAttribute) attributes
        # In a statically typed language like Java it could just be converted to parent class, but can't do that in a dynamically typed language like Python

        return C_Attribute(composite_attribute.name, composite_attribute.cardinality, composite_attribute.attribute_type, composite_attribute.is_unique)
    elif choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES:
        # Use simple attributes
        return composite_attribute.simple_attributes
    
    #TODO: remove original attribute and add new attribute/s
        
def normalize_multi_value_attribute(entity: Entity, attribute: C_Attribute):
    new_entity = None

    if attribute.is_unique:
        new_entity = Entity(entity.name + attribute.name, attribute, [], None)
    else:
        new_id_cardinality = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
        new_id = C_Attribute(attribute.name + "_id", new_id_cardinality, int, True)
        new_entity = Entity(entity.name + attribute.name, new_id, [attribute], None)

    # TODO: remove attribute from the original entity and create a relationship (relationship name composition of two ids)
    return new_entity



# 3. Translate entities
def translate_entity(tables: dict[str, Table], entities: dict[str, Entity], entity_name: str) -> Table:
    entity = entities[entity_name]
    primary_keys = []
    for identifier in entity.identifier:
        primary_keys.append(translate_attribute(identifier))

    weak_entity = entity.weak_entity
    if weak_entity:
        strong_entity = None
        if weak_entity in tables:
            strong_entity = tables[weak_entity]
        else:
            strong_entity = translate_entity(tables, entities, weak_entity)
        primary_keys += strong_entity.primary_key

    attributes = []
    for attribute in entity.attributes:
        attributes.append(translate_attribute(attribute))

    new_table = Table(entity.name, primary_keys, attributes)
    #TODO: check if entity already translated because of weak entity recursion
    return new_table

# 4. Translate relationships
def get_relationship_choices(tables: dict[str, Table], relationship: Relationship, choices: dict[str, set[RELATIONSHIP_CHOICE]]):
    table_from = tables[relationship.entity_from]
    table_to = tables[relationship.entity_to]
    if relationship.cardinality_to.max_cardinality == MaximumCardinality.ONE and relationship.cardinality_from.max_cardinality == MaximumCardinality.ONE:
        # one_to_one relationship
        if relationship.cardinality_from.min_cardinality == MinimumCardinality.ZERO and relationship.cardinality_to.min_cardinality == MinimumCardinality.ZERO:
            choices[relationship.name] = {RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE, RELATIONSHIP_CHOICE.ADD_FOREIGN_KEY}
        else:
            choices[relationship.name] = {RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE, RELATIONSHIP_CHOICE.ADD_FOREIGN_KEY, RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE}
    elif relationship.cardinality_from.max_cardinality != relationship.cardinality_to.max_cardinality:
        # many_to_one relationship
        choices[relationship.name] = {RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE, RELATIONSHIP_CHOICE.ADD_FOREIGN_KEY}
    
def translate_recursive_relationship(table: Table, relationship: Relationship):
    if relationship.cardinality_from.max_cardinality != relationship.cardinality_to.max_cardinality:
        # add foreign key
        for key in table.primary_key:
            table.add_foreign_key(R_Attribute(key.name + "2", key.attribute_type, key.is_optional, key.is_unique))
    else:
        # create new table
        new_attribues = []
        for attribute in relationship.attributes:
            new_attribues.append(translate_attribute(attribute))

        new_primary_keys = []
        for key in table.primary_key:
            new_primary_keys.append(R_Attribute(key.name, key.attribute_type, key.is_optional, key.is_unique))
            new_primary_keys.append(R_Attribute(key.name + "2", key.attribute_type, key.is_optional, key.is_unique))

        new_table = Table(relationship.name, new_primary_keys, new_attribues)

        for key in new_table.primary_key:
            new_table.add_foreign_key(key)
        
        return new_table

def translate_relationship(tables: dict[str, Table], relationship: Relationship, choice: RELATIONSHIP_CHOICE):
    table_from = tables[relationship.entity_from]
    table_to = tables[relationship.entity_to]
    if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY: 
        # many to many relationship
        return translate_many_to_many_relationship(table_from, table_to, relationship)
    elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
        # table_to one side
        translate_one_to_many_relationship(table_to, table_from, relationship, choice)

    elif relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
        # table_from one side
        translate_one_to_many_relationship(table_from, table_to, relationship, choice)
    else:
        # one_to_one relationship
        translate_one_to_one_relationship(table_from, table_to, relationship, choice)
        

def translate_many_to_many_relationship(table_from: Table, table_to: Table, relationship: Relationship):
    new_attribues = []
    for attribute in relationship.attributes:
        new_attribues.append(translate_attribute(attribute))

    new_table = Table(relationship.name, table_from.primary_key + table_to.primary_key, new_attribues)

    for key in new_table.primary_key:
        new_table.add_foreign_key(key)
    
    return new_table

def translate_one_to_many_relationship(one_side: Table, many_side: Table, relationship: Relationship, choice: RELATIONSHIP_CHOICE):
    if choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
        return translate_many_to_many_relationship(one_side, many_side, relationship)
    else:
        add_foreign_keys_and_attributes(one_side, many_side, relationship.attributes)



def translate_one_to_one_relationship(table_from: Table, table_to: Table, relationship: Relationship, choice: RELATIONSHIP_CHOICE):
    # if both sides has optionality, then need two tables
    # if at least one side is not optional, can choose if merge into one table or have two tables
    
    if relationship.cardinality_from.min_cardinality == MinimumCardinality.ZERO and relationship.cardinality_to.min_cardinality == MinimumCardinality.ZERO:
        # need two tables since both sides can be optional
        if choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
            return translate_many_to_many_relationship(table_from, table_to, relationship)
        else:
            add_foreign_keys_and_attributes(table_from, table_to, relationship.attributes)
    
    elif relationship.cardinality_from.min_cardinality == MinimumCardinality.ONE:
        # can be table_to optional or neither are optional
        # merge into table_from or keep two tables with foreign key on table_from
        if choice == RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE:
            return merge_tables_into_one(table_from, table_to, relationship.attributes)
        elif choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
            return translate_many_to_many_relationship(table_from, table_to, relationship)
        else:
            add_foreign_keys_and_attributes(table_from, table_to, relationship.attributes)
    
    else:
        # merge into table_to or keep two tables with foreign key on table_to
        if choice == RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE:
            return merge_tables_into_one(table_to, table_from, relationship.attributes)
        elif choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
            return translate_many_to_many_relationship(table_to, table_from, relationship)
        else:
            add_foreign_keys_and_attributes(table_to, table_from, relationship.attributes)        


