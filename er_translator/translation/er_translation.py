from ..data.conceptual import MinimumCardinality, MaximumCardinality, Cardinality, HierarchyCompleteness, HierarchyDisjointness, Entity, Hierarchy, Relationship, Attribute as C_Attribute, CompositeAttribute
from ..data.relational import Table, Attribute as R_Attribute, ForeignKey
from ..data.choices import COMPOSITE_ATTRIBUTE_CHOICE, RELATIONSHIP_CHOICE

class ERTranslator:
    def __init__(self, entities: list[Entity], relationships: list[Relationship]):
        self._entities = entities
        self._relationships = relationships
        self._tables = []

    def translate(self) -> list[Table]:
        # Translation steps:
        # 1. Eliminate hierarchies TODO

        # 2. Normalize composite attributes
        # Three possibilities:
        # - Keep simple attributes
        # - Have one single main attribute
        # - Create new entity (mandatory when cardinality is n)

        # 3. Translate entities

        # 4. Translate relationships

        return self._tables


    
    # 1. Eliminate hierarchies TODO

    # 2. Normalize composite attributes
    # Three possibilities:
    # - Keep simple attributes
    # - Have one single main attribute
    # - Create new entity (mandatory when cardinality is n)

    def get_composite_attributes_choices(self, entity_name: str, attribute: C_Attribute, choices: dict[str, dict[str, set[COMPOSITE_ATTRIBUTE_CHOICE]]]):
        if isinstance(attribute, CompositeAttribute):
            if entity_name in choices:
                choices[entity_name][attribute.name] = {COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE, COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES}
            else:
                choices[entity_name] = {attribute.name: {COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE, COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES}}

    def normalize_attribute(self, entity_name: str, attribute: C_Attribute, 
                            choice: COMPOSITE_ATTRIBUTE_CHOICE = COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE) -> None:
        entity = self._entities[entity_name]
        if isinstance(attribute, CompositeAttribute) and attribute.cardinality.max_cardinality == MaximumCardinality.MANY:
            if choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE:

                # Create a new object of C_Attribute(conceptual attribute) to limit access to child class (CompositeAttribute) attributes
                # In a statically typed language like Java it could just be converted to parent class, but can't do that in a dynamically typed language like Python

                self._normalize_multi_value_attribute(entity, C_Attribute(attribute.name, attribute.cardinality, attribute.is_unique))
            elif choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES:
                simple_attributes = attribute.simple_attributes
                for simple_attribute in simple_attributes:
                    self._normalize_multi_value_attribute(entity, simple_attribute)
        elif isinstance(attribute, CompositeAttribute):
            self._normalize_composite_attribute(entity, attribute, choice)
        elif attribute.cardinality.max_cardinality == MaximumCardinality.MANY:
            self._normalize_multi_value_attribute(entity, attribute)


    def _normalize_composite_attribute(self, entity: Entity, composite_attribute: CompositeAttribute, choice: COMPOSITE_ATTRIBUTE_CHOICE) -> None:
        if choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE:
            # Keep composite attribute

            # Create a new object of C_Attribute(conceptual attribute) to limit access to child class (CompositeAttribute) attributes
            # In a statically typed language like Java it could just be converted to parent class, but can't do that in a dynamically typed language like Python

            new_attributes = [C_Attribute(composite_attribute.name, composite_attribute.cardinality, composite_attribute.is_unique)]
            
        elif choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES:
            # Use simple attributes

            new_attributes = composite_attribute.simple_attributes
        
        entity.remove_attribute(composite_attribute.name)
        for new_attribute in new_attributes:
            entity.add_attribute(new_attribute)
            
    def _normalize_multi_value_attribute(self, entity: Entity, attribute: C_Attribute) -> None:
        new_entity = None

        if attribute.is_unique:
            new_entity = Entity(entity.name + attribute.name, attribute, [], None)
        else:
            new_id_cardinality = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
            new_id = C_Attribute(attribute.name + "_id", new_id_cardinality, int, True)
            new_entity = Entity(entity.name + attribute.name, new_id, [attribute], None)
        entity.remove_attribute(attribute.name)
        self._entities[new_entity.name] = new_entity
        new_relationship = Relationship(
            entity.name + "_AND_" + attribute.name,
            entity.name,
            new_entity.name,
            attribute.cardinality,
            Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
        )
        self._relationships[new_relationship.name] = new_relationship

    # 3. Translate entities

    def translate_entity(self, entity_name: str) -> None:
        if entity_name not in self._tables:
            entity = self._entities[entity_name]
            primary_keys = []
            for identifier in entity.identifier:
                primary_keys.append(self._translate_attribute(identifier))

            weak_entity = entity.weak_entity
            if weak_entity:
                strong_entity = None
                if weak_entity in self._tables:
                    strong_entity = self._tables[weak_entity]
                else:
                    strong_entity = self.translate_entity(weak_entity)
                primary_keys += strong_entity.primary_key

            attributes = []
            for attribute in entity.attributes:
                attributes.append(self._translate_attribute(attribute))

            new_table = Table(entity.name, primary_keys, attributes)
            self._tables[entity_name] = new_table
       
    # 4. Translate relationships

    def get_relationship_choices(self, relationship: Relationship, choices: dict[str, set[RELATIONSHIP_CHOICE]]):
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
        
    def translate_recursive_relationship(self, table: Table, relationship: Relationship) -> None:
        if relationship.cardinality_from.max_cardinality != relationship.cardinality_to.max_cardinality:
            # add foreign key
            for key in table.primary_key:
                table.add_foreign_key(R_Attribute(key.name + "B", key.is_optional, key.is_unique))
        else:
            # create new table
            new_attribues = []
            for attribute in relationship.attributes:
                new_attribues.append(self._translate_attribute(attribute))

            new_primary_keys = []
            for key in table.primary_key:
                new_primary_keys.append(R_Attribute(key.name + "A", key.is_optional, key.is_unique))
                new_primary_keys.append(R_Attribute(key.name + "B", key.is_optional, key.is_unique))

            new_table = Table(relationship.name, new_primary_keys, new_attribues)

            for key in new_table.primary_key:
                new_table.add_foreign_key(key)
            
            self._tables[new_table.name] = new_table

    def translate_relationship(self, relationship_name: str, choice: RELATIONSHIP_CHOICE = None) -> None:
        relationship = self._relationships[relationship_name]
        table_from = self._tables[relationship.entity_from]
        table_to = self._tables[relationship.entity_to]
        if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY: 
            # many to many relationship
            self._translate_many_to_many_relationship(table_from, table_to, relationship)
        elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
            # table_to one side
            self._translate_one_to_many_relationship(table_to, table_from, relationship)

        elif relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
            # table_from one side
            self._translate_one_to_many_relationship(table_from, table_to, relationship)
        else:
            # one_to_one relationship
            self._translate_one_to_one_relationship(table_from, table_to, relationship)
            

    def _translate_many_to_many_relationship(self, table_from: Table, table_to: Table, relationship: Relationship) -> None:
        new_attribues = []
        for attribute in relationship.attributes:
            new_attribues.append(self._translate_attribute(attribute))

        new_table = Table(relationship.name, table_from.primary_key + table_to.primary_key, new_attribues)

        for key in new_table.primary_key:
            new_table.add_foreign_key(key)
        
        self._tables[new_table.name] = new_table

    def _translate_one_to_many_relationship(self, one_side: Table, many_side: Table, relationship: Relationship, 
                                            choice: RELATIONSHIP_CHOICE = RELATIONSHIP_CHOICE.ADD_FOREIGN_KEY) -> None:
        if choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
            self._translate_many_to_many_relationship(one_side, many_side, relationship)
        else:
            self._add_foreign_keys_and_attributes(one_side, many_side, relationship.attributes)



    def _translate_one_to_one_relationship(self, table_from: Table, table_to: Table, relationship: Relationship, 
                                           choice: RELATIONSHIP_CHOICE = RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE) -> None:
        # if both sides has optionality, then need two tables
        # if at least one side is not optional, can choose if merge into one table or have two tables
        
        if relationship.cardinality_from.min_cardinality == MinimumCardinality.ZERO and relationship.cardinality_to.min_cardinality == MinimumCardinality.ZERO:
            # need two tables since both sides can be optional
            if choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
                self._translate_many_to_many_relationship(table_from, table_to, relationship)
            else:
                self._add_foreign_keys_and_attributes(table_from, table_to, relationship.attributes)
        
        elif relationship.cardinality_from.min_cardinality == MinimumCardinality.ONE:
            # can be table_to optional or neither are optional
            # merge into table_from or keep two tables with foreign key on table_from
            if choice == RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE:
                self._merge_tables_into_one(table_from, table_to, relationship.attributes)
            elif choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
                self._translate_many_to_many_relationship(table_from, table_to, relationship)
            else:
                self._add_foreign_keys_and_attributes(table_from, table_to, relationship.attributes)
        
        else:
            # merge into table_to or keep two tables with foreign key on table_to
            if choice == RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE:
                self._merge_tables_into_one(table_to, table_from, relationship.attributes)
            elif choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
                self._translate_many_to_many_relationship(table_to, table_from, relationship)
            else:
                self._add_foreign_keys_and_attributes(table_to, table_from, relationship.attributes)        
    
    def _add_foreign_keys_and_attributes(self, main_table: Table, referenced_table: Table, relationship_attributes: list[C_Attribute]) -> None:
        for key in referenced_table.primary_key:
            main_table.add_foreign_key(key)
            
        for attribute in relationship_attributes:
            main_table.add_attribute(self._translate_attribute(attribute))

    def _merge_tables_into_one(self, main_table: Table, secondary_table: Table, relationship_attributes: list[C_Attribute]) -> None:
        new_name = main_table.name + secondary_table.name
        new_primary_keys = main_table.primary_key
        new_attributes = main_table.attributes + secondary_table.attributes
        for attribute in relationship_attributes:
            new_attributes.append(self._translate_attribute(attribute))
        
        new_table = Table(new_name, new_primary_keys, new_attributes)

        new_foreign_keys = main_table.foreign_key + secondary_table.foreign_key
        for foreign_key in new_foreign_keys:
            new_table.add_foreign_key(foreign_key)
        
        self._tables[new_table.name] = new_table

    # helper functions
    def _translate_attribute(self, conceptual_attribute: C_Attribute) -> R_Attribute:
        # Translate conceptual attribute to relational attribute
        isOptional = True if conceptual_attribute.cardinality.min_cardinality == MinimumCardinality.ZERO else False
        
        return R_Attribute(conceptual_attribute.name, isOptional, conceptual_attribute.is_unique)

    