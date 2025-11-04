from ..data.conceptual import MinimumCardinality, MaximumCardinality, Cardinality, HierarchyCompleteness, HierarchyDisjointness, Entity, Hierarchy, Relationship, Attribute as C_Attribute, CompositeAttribute
from ..data.relational import Table, Attribute as R_Attribute, ForeignKey
from ..data.choices import COMPOSITE_ATTRIBUTE_CHOICE, RELATIONSHIP_CHOICE, HIERARCHY_CHOICE
from ..data.hierachy_checks import HierarchyChecks
from ..translation.hierarchy_translation import HierachyTranslator
from ..translation.sql_generator import SQLGenerator
from ..utils.utils import get_all_father_entities, retrieve_connected_relationships, retrieve_children_names, retrieve_all_hierarchy_relationships

class ERTranslator:
    def __init__(self, entities: dict[str, Entity], relationships: dict[str, Relationship]):
        self._entities = entities
        self._relationships = relationships
        self._tables = {}
        self._hierarchy_checks = HierarchyChecks()
        self._hierarchy_changes = {}

    def translate(self, composite_attributes_choices: dict[(str, str), COMPOSITE_ATTRIBUTE_CHOICE], hierarchy_choices: dict[str, HIERARCHY_CHOICE], relationship_choices: dict[str, RELATIONSHIP_CHOICE]) -> list[Table]:
        print("\n Translating ER model...")
        
        # Translation steps:
        # 1. Normalize composite attributes
        self.normalize_all_attributes(composite_attributes_choices)

        
        # 2. Eliminate hierarchies
        self.eliminate_one_to_one_relationships(hierarchy_choices)
        self.create_hierarchy_checks(hierarchy_choices)
        self._eliminate_hierarchies(hierarchy_choices)
        
        # 3. Translate entities
        for entity_name in self._entities.keys():
            self.translate_entity(entity_name)
        
        # 4. Translate relationships
        for relationship_name, relationship in self._relationships.items():
            # Check if it's a recursive relationship (entity references itself)
            if relationship.entity_from == relationship.entity_to:
                table_name = relationship.entity_from
                if table_name in self._hierarchy_changes:
                    table = self._tables[self._hierarchy_changes[table_name]]
                self.translate_recursive_relationship(table, relationship, table_name)
            else:
                if relationship_name in relationship_choices:
                    self.translate_relationship(relationship_name, relationship_choices[relationship_name])
                else:
                    self.translate_relationship(relationship_name)
        
        # 5. Create SQL code
        return self.create_sql_code()
        

        

    # 1. Normalize composite attributes
    # Three possibilities:
    # - Keep simple attributes
    # - Have one single main attribute
    # - Create new entity (mandatory when cardinality is n)

    def get_composite_attributes_choices(self):
        choices = {}
        default_choices = {}
        for entity in self._entities.values():
            for identifier in entity.identifiers:
                if isinstance(identifier, CompositeAttribute):
                    choices[(entity.name, identifier.name)] = {COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE, COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES}
                    default_choices[(entity.name, identifier.name)] = COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE
            for attribute in entity.attributes:
                if isinstance(attribute, CompositeAttribute):
                    choices[(entity.name, attribute.name)] = {COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE, COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES}
                    default_choices[(entity.name, attribute.name)] = COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE
        return choices, default_choices

    def normalize_all_attributes(self, composite_attributes_choices: dict[(str, str), COMPOSITE_ATTRIBUTE_CHOICE]):
        """Normalize all attributes (identifiers and regular attributes) in all entities."""
        # We need to iterate over a copy of entity names since we may add new entities during normalization
        entity_names = list(self._entities.keys())
        
        for entity_name in entity_names:
            entity = self._entities[entity_name]
            
            # Normalize identifiers
            identifiers_to_normalize = list(entity.identifiers)
            for identifier in identifiers_to_normalize:
                key = (entity_name, identifier.name)
                if key in composite_attributes_choices:
                    self._normalize_attribute(entity_name, identifier, is_identifier=True, choice=composite_attributes_choices[key])
                else:
                    self._normalize_attribute(entity_name, identifier, is_identifier=True)
                
            # Normalize regular attributes
            attributes_to_normalize = list(entity.attributes)
            for attribute in attributes_to_normalize:
                key = (entity_name, attribute.name)
                if key in composite_attributes_choices:
                    self._normalize_attribute(entity_name, attribute, is_identifier=False, choice=composite_attributes_choices[key])
                else:
                    self._normalize_attribute(entity_name, attribute, is_identifier=False)
                

   
    def _normalize_attribute(self, entity_name: str, attribute: C_Attribute, 
                            is_identifier: bool = False,
                            choice: COMPOSITE_ATTRIBUTE_CHOICE = COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE) -> None:
        entity = self._entities[entity_name]
        if isinstance(attribute, CompositeAttribute) and attribute.cardinality.max_cardinality == MaximumCardinality.MANY:
            if choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE:

                # Create a new object of C_Attribute(conceptual attribute) to limit access to child class (CompositeAttribute) attributes
                # In a statically typed language like Java it could just be converted to parent class, but can't do that in a dynamically typed language like Python

                self._normalize_multi_value_attribute(entity, C_Attribute(attribute.name, attribute.cardinality, attribute.is_unique), is_identifier)
            elif choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES:
                simple_attributes = attribute.simple_attributes
                for simple_attribute in simple_attributes:
                    self._normalize_multi_value_attribute(entity, simple_attribute, is_identifier)
            
            # Remove the composite attribute after processing
            if is_identifier:
                entity.remove_identifier(attribute.name)
            else:
                entity.remove_attribute(attribute.name)
        elif isinstance(attribute, CompositeAttribute):
            self._normalize_composite_attribute(entity, attribute, is_identifier, choice)
        elif attribute.cardinality.max_cardinality == MaximumCardinality.MANY:
            self._normalize_multi_value_attribute(entity, attribute, is_identifier)


    def _normalize_composite_attribute(self, entity: Entity, composite_attribute: CompositeAttribute, is_identifier: bool, choice: COMPOSITE_ATTRIBUTE_CHOICE) -> None:
        if choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_COMPOSITE:
            # Keep composite attribute

            # Create a new object of C_Attribute(conceptual attribute) to limit access to child class (CompositeAttribute) attributes
            # In a statically typed language like Java it could just be converted to parent class, but can't do that in a dynamically typed language like Python

            new_attributes = [C_Attribute(composite_attribute.name, composite_attribute.cardinality, composite_attribute.is_unique)]
            
        elif choice == COMPOSITE_ATTRIBUTE_CHOICE.KEEP_SIMPLE_ATTRIBUTES:
            # Use simple attributes

            new_attributes = composite_attribute.simple_attributes
        
        # Remove from the correct list (identifiers or attributes)
        if is_identifier:
            entity.remove_identifier(composite_attribute.name)
        else:
            entity.remove_attribute(composite_attribute.name)
        
        # Add back to the correct list
        for new_attribute in new_attributes:
            if is_identifier:
                entity.add_identifier(new_attribute)
            else:
                entity.add_attribute(new_attribute)
            
    def _normalize_multi_value_attribute(self, entity: Entity, attribute: C_Attribute, is_identifier: bool) -> None:
        new_entity = None

        if attribute.is_unique:
            new_entity = Entity(entity.name + attribute.name)
            new_entity.add_identifier(attribute)
        else:
            new_id_cardinality = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
            new_id = C_Attribute(attribute.name + "_id", new_id_cardinality, True)
            new_entity = Entity(entity.name + attribute.name)
            new_entity.add_identifier(new_id)
            new_entity.add_attribute(attribute)

        # Remove from the correct list (identifiers or attributes)
        if is_identifier:
            entity.remove_identifier(attribute.name)
        else:
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

    # 2. Eliminate hierarchies
    def get_hierarchy_choices(self):
        choices = {}
        default_choices = {}
        for entity in self._entities.values():
            hierarchy = entity.hierarchy
            if hierarchy and hierarchy.hierarchy_completeness == HierarchyCompleteness.TOTAL and hierarchy.hierarchy_disjointness == HierarchyDisjointness.DISJOINT:
                choices[(entity.name)] = {HIERARCHY_CHOICE.COLLAPSE_UPWARDS, HIERARCHY_CHOICE.COLLAPSE_DOWNWARDS}
                default_choices[(entity.name)] = HIERARCHY_CHOICE.COLLAPSE_UPWARDS
        
        return choices, default_choices


    def eliminate_one_to_one_relationships(self, hierarchy_choices: dict[str, HIERARCHY_CHOICE]):
        father_entities_names = get_all_father_entities(self._entities.values())

        for father_entity_name in father_entities_names:
            father_entity = self._entities[father_entity_name]

            if father_entity_name in hierarchy_choices:
                choice = hierarchy_choices[father_entity_name]
            else:
                # default
                choice = HIERARCHY_CHOICE.COLLAPSE_UPWARDS
            
            if choice == HIERARCHY_CHOICE.COLLAPSE_UPWARDS:
                children_entities = retrieve_children_names(father_entity)
                hierarchy_relationships = retrieve_connected_relationships(children_entities, self._relationships)
                
                for relationship_name in hierarchy_relationships:
                    relationship = self._relationships[relationship_name]
                    if relationship.cardinality_from.max_cardinality == MaximumCardinality.ONE and relationship.cardinality_to.max_cardinality == MaximumCardinality.ONE:
                        if relationship.entity_from in children_entities:
                            relationship.set_cardinality_to(Cardinality(relationship.cardinality_to.min_cardinality, MaximumCardinality.MANY))
                        elif relationship.entity_to in children_entities:
                            relationship.set_cardinality_from(Cardinality(relationship.cardinality_from.min_cardinality, MaximumCardinality.MANY))
            elif choice == HIERARCHY_CHOICE.COLLAPSE_DOWNWARDS:
                hierarchy_relationships = retrieve_connected_relationships([father_entity.name], self._relationships)
            
                for relationship_name in hierarchy_relationships:
                    relationship = self._relationships[relationship_name]
                    if relationship.cardinality_from.max_cardinality == MaximumCardinality.ONE and relationship.cardinality_to.max_cardinality == MaximumCardinality.ONE:
                        if relationship.entity_from in father_entities_names:
                            relationship.set_cardinality_from(Cardinality(relationship.cardinality_from.min_cardinality, MaximumCardinality.MANY))
                        elif relationship.entity_to in father_entities_names:
                            relationship.set_cardinality_to(Cardinality(relationship.cardinality_to.min_cardinality, MaximumCardinality.MANY))            
                    
    def create_hierarchy_checks(self, hierarchy_choices: dict[str, HIERARCHY_CHOICE]):
        hierachy_translator = HierachyTranslator(self._entities, self._relationships)
        hierachy_translator.translate_hierarchies(hierarchy_choices)
        self._hierarchy_checks = hierachy_translator.hierarchy_checks


    def _eliminate_hierarchies(self, hierarchy_choices: dict[str, HIERARCHY_CHOICE]):
        parent_entities = get_all_father_entities(self._entities.values())
        
        # Process each hierarchy
        for parent_entity_name in parent_entities:
            if parent_entity_name in hierarchy_choices:
                choice = hierarchy_choices[parent_entity_name]
            else:
                # default
                choice = HIERARCHY_CHOICE.COLLAPSE_UPWARDS
            parent_entity = self._entities[parent_entity_name]
            children = parent_entity.hierarchy.children
            if choice == HIERARCHY_CHOICE.COLLAPSE_UPWARDS:
                
                
                # Add all children's attributes to parent as optional            
                for child_name in children:
                    self._hierarchy_changes[child_name] = parent_entity_name
                    child_entity = self._entities[child_name]
                    
                    for identifier in child_entity.identifiers:
                        optional_cardinality = Cardinality(MinimumCardinality.ZERO, identifier.cardinality.max_cardinality)
                        optional_attr = C_Attribute(identifier.name, optional_cardinality, identifier.is_unique)
                        parent_entity.add_attribute(optional_attr)
                        
                    for attribute in child_entity.attributes:
                        optional_cardinality = Cardinality(MinimumCardinality.ZERO, attribute.cardinality.max_cardinality)
                        optional_attr = C_Attribute(attribute.name, optional_cardinality, attribute.is_unique)
                        parent_entity.add_attribute(optional_attr)

                for child_name in children:

                    if child_name in self._entities:
                        del self._entities[child_name]
            elif choice == HIERARCHY_CHOICE.COLLAPSE_DOWNWARDS:
                parent_relationships = retrieve_connected_relationships([parent_entity.name], self._relationships)
                for child_name in children:
                    child_entity = self._entities[child_name]
                    for identifier in parent_entity.identifiers:
                        child_entity.add_identifier(identifier)
                    for attribute in parent_entity.attributes:
                        child_entity.add_attribute(attribute)
        
                    for relationship_name in parent_relationships:
                        relationship = self._relationships[relationship_name]
                        relationship_copy = relationship.deep_copy()
                        
                        if parent_entity.name == relationship.entity_from:
                            relationship_copy.set_entity_from(child_name)
                        elif parent_entity.name == relationship.entity_to:
                            relationship_copy.set_entity_to(child_name)
                        relationship_copy.set_name(relationship_copy.name + "_" + relationship_copy.entity_from + "_" + relationship_copy.entity_to)
                        self._relationships[relationship_copy.name] = relationship_copy
                for relationship_name in parent_relationships:
                    del self._relationships[relationship_name]
                del self._entities[parent_entity_name]

    # 3. Translate entities

    def translate_entity(self, entity_name: str) -> None:
        if entity_name not in self._tables:
            entity = self._entities[entity_name]
            primary_keys = []
            for identifier in entity.identifiers:
                primary_keys.append(self._translate_attribute(identifier))

            strong_entity_name = entity.strong_entity
            if strong_entity_name:
                strong_entity = None
                if strong_entity_name in self._tables:
                    strong_entity = self._tables[strong_entity_name]
                else:
                    self.translate_entity(strong_entity_name)
                    strong_entity = self._tables[strong_entity_name]
                primary_keys += strong_entity.primary_keys

            attributes = []
            for attribute in entity.attributes:
                attributes.append(self._translate_attribute(attribute))

            new_table = Table(entity.name, primary_keys, attributes)
            self._tables[entity_name] = new_table
       
    # 4. Translate relationships

    def get_relationship_choices(self):
        choices = {}
        default_choices = {}
        hierarchy_relationships = retrieve_all_hierarchy_relationships(self._entities.values(), self._relationships)
        for relationship in self._relationships.values():
            if relationship.name in hierarchy_relationships:
                continue
            if relationship.cardinality_to.max_cardinality == MaximumCardinality.ONE and relationship.cardinality_from.max_cardinality == MaximumCardinality.ONE:
                # one_to_one relationship
                if relationship.cardinality_from.min_cardinality == MinimumCardinality.ZERO and relationship.cardinality_to.min_cardinality == MinimumCardinality.ZERO:
                    choices[relationship.name] = {RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE, RELATIONSHIP_CHOICE.ADD_FOREIGN_KEY}
                    default_choices[relationship.name] = RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE
                else:
                    choices[relationship.name] = {RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE, RELATIONSHIP_CHOICE.ADD_FOREIGN_KEY, RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE}
                    default_choices[relationship.name] = RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE
            elif relationship.cardinality_from.max_cardinality != relationship.cardinality_to.max_cardinality:
                # many_to_one relationship
                choices[relationship.name] = {RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE, RELATIONSHIP_CHOICE.ADD_FOREIGN_KEY}
                default_choices[relationship.name] = RELATIONSHIP_CHOICE.ADD_FOREIGN_KEY
        
        return choices, default_choices

    def translate_recursive_relationship(self, table: Table, relationship: Relationship, table_name: str) -> None:
        if relationship.cardinality_from.max_cardinality != relationship.cardinality_to.max_cardinality:
            # add foreign key
            for key in table.primary_keys:
                table.add_foreign_key(ForeignKey(table_name + "_" + key.name, key.is_optional, key.is_unique, table, key))
        else:
            # create new table
            new_attribues = []
            for attribute in relationship.attributes:
                new_attribues.append(self._translate_attribute(attribute))

            new_primary_keys = []
            for key in table.primary_keys:
                new_primary_keys.append(R_Attribute(table_name + "_" + key.name + "_A", key.is_optional, key.is_unique))
                new_primary_keys.append(R_Attribute(table_name + "_" + key.name + "_B", key.is_optional, key.is_unique))

            new_table = Table(relationship.name, new_primary_keys, new_attribues)

            for key in table.primary_keys:
                new_table.add_foreign_key(ForeignKey(table_name + "_" + key.name + "_A", key.is_optional, key.is_unique, table, key))
                new_table.add_foreign_key(ForeignKey(table_name + "_" + key.name + "_B", key.is_optional, key.is_unique, table, key))
            
            self._tables[new_table.name] = new_table

    def translate_relationship(self, relationship_name: str, choice: RELATIONSHIP_CHOICE = None) -> None:
        relationship = self._relationships[relationship_name]
        table_from_name = relationship.entity_from
        if relationship.entity_from in self._hierarchy_changes:
            table_from = self._tables[self._hierarchy_changes[relationship.entity_from]]
        else:
            table_from = self._tables[relationship.entity_from]
        table_to_name = relationship.entity_to
        if relationship.entity_to in self._hierarchy_changes:
            table_to = self._tables[self._hierarchy_changes[relationship.entity_to]]
        else:
            table_to = self._tables[relationship.entity_to]
        if relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY and relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY: 
            # many to many relationship
            self._translate_many_to_many_relationship(table_from, table_to, relationship, table_from_name, table_to_name)
        elif relationship.cardinality_from.max_cardinality == MaximumCardinality.MANY:
            # table_to one side
            if choice:
                self._translate_one_to_many_relationship(table_to, table_from, relationship, table_to_name, table_from_name, choice)
            else:
                self._translate_one_to_many_relationship(table_to, table_from, relationship, table_to_name, table_from_name)

        elif relationship.cardinality_to.max_cardinality == MaximumCardinality.MANY:
            # table_from one side
            if choice:
                self._translate_one_to_many_relationship(table_from, table_to, relationship, table_from_name, table_to_name, choice)
            else:
                self._translate_one_to_many_relationship(table_from, table_to, relationship, table_from_name, table_to_name)
        else:
            # one_to_one relationship
            if choice:
                self._translate_one_to_one_relationship(table_from, table_to, relationship, table_from_name, table_to_name, choice)
            else:
                self._translate_one_to_one_relationship(table_from, table_to, relationship, table_from_name, table_to_name)
            

    def _translate_many_to_many_relationship(self, table_from: Table, table_to: Table, relationship: Relationship, table_from_name: str, table_to_name: str) -> None:
        new_attribues = []
        for attribute in relationship.attributes:
            new_attribues.append(self._translate_attribute(attribute))

        new_primary_keys = []
        for key in table_from.primary_keys:
            new_pk = R_Attribute(table_from_name + "_" + key.name, key.is_optional, key.is_unique)
            new_primary_keys.append(new_pk)
            
        for key in table_to.primary_keys:
            new_pk = R_Attribute(table_to_name + "_" + key.name, key.is_optional, key.is_unique)
            new_primary_keys.append(new_pk)

        new_table = Table(relationship.name, new_primary_keys, new_attribues)


        for key in table_from.primary_keys:
            new_table.add_foreign_key(ForeignKey(table_from_name + "_" + key.name, key.is_optional, key.is_unique, table_from, key))
            
        for key in table_to.primary_keys:
            new_table.add_foreign_key(ForeignKey(table_to_name + "_" + key.name, key.is_optional, key.is_unique, table_to, key))
        
        self._tables[new_table.name] = new_table

    def _translate_one_to_many_relationship(self, one_side: Table, many_side: Table, relationship: Relationship,
                                            one_side_name: str, many_side_name: str,
                                            choice: RELATIONSHIP_CHOICE = RELATIONSHIP_CHOICE.ADD_FOREIGN_KEY) -> None:
        if choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
            self._translate_many_to_many_relationship(one_side, many_side, relationship, one_side_name, many_side_name)
        else:
            self._add_foreign_keys_and_attributes(one_side, many_side, relationship, one_side_name, many_side_name)



    def _translate_one_to_one_relationship(self, table_from: Table, table_to: Table, relationship: Relationship,
                                           one_side_name: str, many_side_name: str,
                                           choice: RELATIONSHIP_CHOICE = RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE) -> None:
        # if both sides has optionality, then need two tables
        # if at least one side is not optional, can choose if merge into one table or have two tables
        
        if relationship.cardinality_from.min_cardinality == MinimumCardinality.ZERO and relationship.cardinality_to.min_cardinality == MinimumCardinality.ZERO:
            # need two tables since both sides can be optional
            if choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
                self._translate_many_to_many_relationship(table_from, table_to, relationship, one_side_name, many_side_name)
            else:
                self._add_foreign_keys_and_attributes(table_from, table_to, relationship, one_side_name, many_side_name)
        
        elif relationship.cardinality_from.min_cardinality == MinimumCardinality.ONE:
            # can be table_to optional or neither are optional
            # merge into table_from or keep two tables with foreign key on table_from
            if choice == RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE:
                self._merge_tables_into_one(table_from, table_to, relationship, one_side_name, many_side_name)
            elif choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
                self._translate_many_to_many_relationship(table_from, table_to, relationship, one_side_name, many_side_name)
            else:
                self._add_foreign_keys_and_attributes(table_from, table_to, relationship, one_side_name, many_side_name)
        
        else:
            # merge into table_to or keep two tables with foreign key on table_to
            if choice == RELATIONSHIP_CHOICE.MERGE_INTO_SINGLE_TABLE:
                self._merge_tables_into_one(table_to, table_from, relationship, one_side_name, many_side_name)
            elif choice == RELATIONSHIP_CHOICE.RELANTIONSHIP_TABLE:
                self._translate_many_to_many_relationship(table_to, table_from, relationship, one_side_name, many_side_name)
            else:
                self._add_foreign_keys_and_attributes(table_to, table_from, relationship, one_side_name, many_side_name)        
    
    def _add_foreign_keys_and_attributes(self, main_table: Table, referenced_table: Table, relationship: Relationship, main_table_name: str, referenced_table_name: str) -> None:
        relationship_attributes = relationship.attributes
        for key in referenced_table.primary_keys:
            main_table.add_foreign_key(ForeignKey(referenced_table_name + "_" + key.name, key.is_optional, key.is_unique, referenced_table, key))
            
        for attribute in relationship_attributes:
            new_attribute = self._translate_attribute(attribute)
            new_attribute.name = main_table_name + "_" + attribute.name
            main_table.add_attribute(new_attribute)

    def _merge_tables_into_one(self, main_table: Table, secondary_table: Table, relationship: Relationship, main_table_name: str, secondary_table_name: str) -> None:
        new_name = main_table_name + secondary_table_name
        new_primary_keys = list(main_table.primary_keys)
        new_attributes = list(main_table.attributes) + list(secondary_table.primary_keys) + list(secondary_table.attributes)
        for attribute in relationship.attributes:
            new_attributes.append(self._translate_attribute(attribute))
        
        new_table = Table(new_name, new_primary_keys, new_attributes)

        new_foreign_keys = main_table.foreign_keys + secondary_table.foreign_keys
        for foreign_key in new_foreign_keys:
            new_table.add_foreign_key(foreign_key)
        
        # Remove old tables and add the merged table
        if main_table_name in self._tables:
            del self._tables[main_table_name]
        if secondary_table_name in self._tables:
            del self._tables[secondary_table_name]
        
        self._tables[new_table.name] = new_table

    # helper functions
    def _translate_attribute(self, conceptual_attribute: C_Attribute) -> R_Attribute:
        # Translate conceptual attribute to relational attribute
        isOptional = True if conceptual_attribute.cardinality.min_cardinality == MinimumCardinality.ZERO else False
        
        return R_Attribute(conceptual_attribute.name, isOptional, conceptual_attribute.is_unique)

    # 5. Create SQL code

    def create_sql_code(self) -> str:
        """Generate SQL code for all tables using SQLGenerator templates."""
        sql_statements = []
        
        for table_name, table in self._tables.items():
            # Generate attributes SQL
            attributes_sql = []
            for primary_key in table.primary_keys:
                attr_sql = SQLGenerator.create_sql_attribute(primary_key.name, primary_key.is_optional)
                attributes_sql.append(attr_sql)
            for attribute in table.attributes:
                attr_sql = SQLGenerator.create_sql_attribute(attribute.name, attribute.is_optional, attribute.is_unique)
                attributes_sql.append(attr_sql)
            
            # Generate selectors SQL (empty for now, will be used for hierarchies)
            selectors_sql = self._hierarchy_checks.selectors.get(table_name, [])
            
            # Generate foreign key references SQL
            references_sql = []
            for foreign_key in table.foreign_keys:
                ref_table_name = foreign_key.table_ref.name
                ref_primary_key = foreign_key.primary_key_ref.name
                ref_sql = SQLGenerator.create_sql_reference(
                    foreign_key.name, 
                    ref_table_name, 
                    ref_primary_key
                )
                references_sql.append(ref_sql)
            
            # Get primary key names
            primary_keys = [pk.name for pk in table.primary_keys]
            
            # Generate constraints SQL (empty for now, will be added later)
            constraints_sql = self._hierarchy_checks.constraints.get(table_name, [])
            
            # Create the complete SQL table statement
            table_sql = SQLGenerator.create_sql_table(
                table_name,
                attributes_sql,
                selectors_sql,
                references_sql,
                primary_keys,
                constraints_sql
            )
            sql_statements.append(table_sql)
        
        return "\n\n".join(sql_statements) + "\n\n" + "\n\n".join(self._hierarchy_checks.triggers)
        