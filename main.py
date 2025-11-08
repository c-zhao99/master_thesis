from pathlib import Path
from subprocess import check_output

from er_translator.data.conceptual import *
from er_translator.parsers.erdplus_parser import *
from er_translator.printers.diagram_printer import *
from er_translator.translation.hierarchy_translation import HierachyTranslator
from er_translator.translation.sql_generator import SQLGenerator
from er_translator.translation.er_translation import ERTranslator
from er_translator.printers.diagram_printer import print_entities, print_relationships

def parse_erd_plus():
    file_path = Path(__file__).parent.joinpath('er_translator/examples/every_possibility_no_hierarchy.erdplus')

    erdplus_parser = ERDPLUS_Parser()
    erdplus_parser.parse_erdplus_diagram(file_path)

    print_entities(erdplus_parser.entities.values())
    print_relationships(erdplus_parser.relationships.values())

def create_diagram():
    # from Child1 to Father
    r1_from = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
    r1_to = Cardinality(MinimumCardinality.ZERO, MaximumCardinality.MANY)
    # from Child1 to Child1
    r2_from = Cardinality(MinimumCardinality.ZERO, MaximumCardinality.ONE)
    r2_to = Cardinality(MinimumCardinality.ZERO, MaximumCardinality.MANY)
    # from Child1 to Child2
    r3_from = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
    r3_to = Cardinality(MinimumCardinality.ONE, MaximumCardinality.MANY)
    # from Child3 to Other_Entity
    r4_from = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
    r4_to = Cardinality(MinimumCardinality.ZERO, MaximumCardinality.MANY)

    entities, relationships = create_diagram_from_cardinality(
        r1_from=r1_from,
        r1_to=r1_to,
        r2_from=r2_from,
        r2_to=r2_to,
        r3_from=r3_from,
        r3_to=r3_to,
        r4_from=r4_from,
        r4_to=r4_to
    )

    return entities, relationships


def create_diagram_from_cardinality(r1_from, r1_to, r2_from, r2_to, r3_from, r3_to, r4_from, r4_to):
    entities = {}
    relationships = {}
    #father
    father = Entity("Father")
    id1 = Attribute("F_ID1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    id2 = Attribute("F_ID2", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    father.add_identifier(id1)
    father.add_identifier(id2)
    attr1 = Attribute("F_ATTR1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    father.add_attribute(attr1)

    #child1
    child1 = Entity("Child1")
    attr1 = Attribute("C1_ATTR1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    child1.add_attribute(attr1)

    #child2
    child2 = Entity("Child2")
    attr1 = Attribute("C2_ATTR1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    child2.add_attribute(attr1)

    #child3
    child3 = Entity("Child3")
    #attr2 = Attribute("Child3-ATTR2", Cardinality(MinimumCardinality.ZERO, MaximumCardinality.ONE), True)
    attr1 = Attribute("C3_ATTR1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    child3.add_attribute(attr1)
    '''
    attr3 = CompositeAttribute("Child3-CompositeAttr", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    simple_attr1 = Attribute("Child3-SimpleAttr1-ATTR1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    simple_attr2 = Attribute("Child3-SimpleAttr2-ATTR2", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    attr3.add_simple_attribute(simple_attr1)
    attr3.add_simple_attribute(simple_attr2)
    child3.add_identifier(attr3)
    child3.add_attribute(attr2)
    '''
    #hierarchy
    hierarchy = Hierarchy(HierarchyCompleteness.PARTIAL, HierarchyDisjointness.OVERLAPPING)
    hierarchy.add_child(child1.name)
    hierarchy.add_child(child2.name)
    hierarchy.add_child(child3.name)
    father.set_hierarchy(hierarchy)

    #entity4
    entity4 = Entity("Other_Entity")
    id1 = Attribute("OE_ID1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    id2 = Attribute("OE_ID2", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    entity4.add_identifier(id1)
    entity4.add_identifier(id2)
    attr1 = Attribute("OE_ATTR1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    entity4.add_attribute(attr1)
    

    #add entitites
    entities["Father"] = father
    entities["Child1"] = child1
    entities["Child2"] = child2
    entities["Child3"] = child3
    entities["Other_Entity"] = entity4

    #relationship R1
    r1 = Relationship("Relationship1", "Father", "Child1", r1_from, r1_to)
    relationship_attr1 = Attribute("R1_ATTR1", Cardinality(MinimumCardinality.ZERO, MaximumCardinality.ONE), True)
    r1.add_attribute(relationship_attr1)
    r2 = Relationship("Relationship2", "Child1", "Child1", r2_from, r2_to)
    relationship_attr2 = Attribute("R2-ATTR1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    r2.add_attribute(relationship_attr2)
    r3 = Relationship("Relationship3", "Child2", "Child1", r3_from, r3_to)
    relationship_attr3 = Attribute("R3_ATTR1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    r3.add_attribute(relationship_attr3)    
    r4 = Relationship("Relationship4", "Other_Entity", "Child3", r4_from, r4_to)
    relationship_attr4 = Attribute("R4_ATTR1", Cardinality(MinimumCardinality.ZERO, MaximumCardinality.ONE), True)
    r4.add_attribute(relationship_attr4)
    #add relationships
    relationships["Relationship1"] = r1
    relationships["Relationship2"] = r2
    relationships["Relationship3"] = r3
    relationships["Relationship4"] = r4

    return entities, relationships


def print_current_choices(current_items, item_name):
    if len(current_items) != 0:
        print(f"\n Current choices for {item_name}")
        for item_key, item_choice in current_items.items():
            if isinstance(item_key, tuple):
                entity_name, attr_name = item_key
                print(f"{attr_name} of {entity_name}: {item_choice}")
            else:
                print(f"{item_key}: {item_choice}")

def prompt_item_choices(item_name, item_key, item_choices, current_items):
    if isinstance(item_key, tuple):
        entity_name, attr_name = item_key
        print(f"\n How do you want to translate {attr_name} of {entity_name}?")
    else:
        print(f"\n How do you want to translate {item_key}?")
    
    current_item_choice = current_items[item_key]
    saved = {}
    for i, choice in enumerate(item_choices, 1):
        if choice == current_item_choice:
            print(f"{i}. {choice} (current choice)")
        else:
            print(f"{i}. {choice}")
        saved[i] = choice
    number_of_items = len(item_choices)

    user_input = input(f"\n Enter the number of the choice you want: ").strip()
    try:
        choice_num = int(user_input)
        if 1 <= choice_num <= number_of_items:
            current_items[item_key] = saved[choice_num]
            if isinstance(item_key, tuple):
                entity_name, attr_name = item_key
                print(f"\n Chosen: {current_items[item_key]} for {attr_name} of {entity_name}")
            else:
                print(f"\n Chosen: {current_items[item_key]} for {item_key}")
        else:
            print(f"\n Please enter a number between 1 and {number_of_items}!")
    except ValueError:
        print("\n Invalid input. Please enter a number or press Enter.")

def prompt_items(items, current_items, item_name):
    while True:
        print(f"\n Which {item_name} do you want to change?")
        saved = {}
        for i, (item_key, _) in enumerate(items.items(), 1):
            if isinstance(item_key, tuple):
                entity_name, attr_name = item_key
                print(f"{i}. {attr_name} of Entity: {entity_name}")
                saved[i] = item_key
            else:
                entity_name = item_key
                print(f"{i}. {entity_name}")
                saved[i] = item_key
        number_of_items = len(items.values())
        print(f"{number_of_items + 1}. Exit")
    
        user_input = input(f"\n Enter the number of the {item_name} you want to change: ").strip()
        try:
            choice_num = int(user_input)
            if 1 <= choice_num <= number_of_items+1:
                if choice_num == number_of_items+1:
                    break
                else:
                    prompt_item_choices(item_name, saved[choice_num], items[saved[choice_num]], current_items)
            else:
                print(f"\n Please enter a number between 1 and {number_of_items+1}!")
        except ValueError:
            print("\n Invalid input. Please enter a number or press Enter.")


def choices_selector(entities, relationships):
    entities_copy = {}
    for entity_name, entity in entities.items():
        entities_copy[entity_name] = entity.deep_copy()
    relationships_copy = {}
    for relationship_name, relationship in relationships.items():
        relationships_copy[relationship_name] = relationship.deep_copy()
    er_translator = ERTranslator(entities_copy, relationships_copy)

    composite_attributes_choices, current_composite_attributes_choices = er_translator.get_composite_attributes_choices()
    hierarchy_choices, current_hierarchy_choices = er_translator.get_hierarchy_choices()
    relationship_choices, current_relationship_choices = er_translator.get_relationship_choices()
    
    while True:
        entities_copy = {}
        for entity_name, entity in entities.items():
            entities_copy[entity_name] = entity.deep_copy()
        relationships_copy = {}
        for relationship_name, relationship in relationships.items():
            relationships_copy[relationship_name] = relationship.deep_copy()
        er_translator = ERTranslator(entities_copy, relationships_copy)

        sql_code = er_translator.translate(current_composite_attributes_choices, current_hierarchy_choices, current_relationship_choices)
        print("------- SQL CODE -------")
        print(sql_code)
        print_current_choices(current_composite_attributes_choices, "Composite Attribute")
        print_current_choices(current_hierarchy_choices, "Hierarchy")
        print_current_choices(current_relationship_choices, "Relationship")

        if len(current_composite_attributes_choices) == 0 and len(current_hierarchy_choices) == 0 and len(current_relationship_choices) == 0:
            print("\n No translations choices to change. Exiting...")
            break
        
        user_input = input(f"\n Do you want to change any translations choices? (y/n): ").strip()

        if user_input == "y":
            while True:
                print(f"\n What do you want to change?")
                print(f"1. Composite Attributes")
                print(f"2. Hierarchies")
                print(f"3. Relationships")
                print(f"4. Exit")
                user_input = input(f"\n Enter the number of what you want to change: ").strip()
                try:
                    choice_num = int(user_input)
                    if 1 <= choice_num <= 4:
                        if choice_num == 1:
                            prompt_items(composite_attributes_choices, current_composite_attributes_choices, "Composite Attribute")
                        elif choice_num == 2:
                            prompt_items(hierarchy_choices, current_hierarchy_choices, "Hierarchy")
                        elif choice_num == 3:
                            prompt_items(relationship_choices, current_relationship_choices, "Relationship")
                        elif choice_num == 4:
                            entities_copy = {}
                            for entity_name, entity in entities.items():
                                entities_copy[entity_name] = entity.deep_copy()
                            relationships_copy = {}
                            for relationship_name, relationship in relationships.items():
                                relationships_copy[relationship_name] = relationship.deep_copy()
                            er_translator = ERTranslator(entities_copy, relationships_copy)
                            sql_code = er_translator.translate(current_composite_attributes_choices, current_hierarchy_choices, current_relationship_choices)
                            print("------- SQL CODE -------")
                            print(sql_code)
                            break
                    else:
                        print(f"\n Please enter a number between 1 and 4!")
                except ValueError:
                    print("\n Invalid input. Please enter a number or press Enter.")
        else:
            print("\n Translation done. Exiting...")
            break

if __name__ == "__main__":

    #parse_erd_plus()
    #entities, relationships = create_diagram()

    #er_translator = ERTranslator(entities, relationships)
    #sql__code = er_translator.translate()
    #hierarchy_checks = er_translator._hierarchy_checks
    #print_entities(er_translator._entities.values())
    #print_relationships(er_translator._relationships.values())
    '''
    print("------- SELECTORS -------")
    for entity_name, selector in hierarchy_checks.selectors.items():
        print("Entity name: ", entity_name)
        print("Selector: ", selector)
        print()
    print("------- CONSTRAINTS -------")
    for entity_name, constraint in hierarchy_checks.constraints.items():
        print("Entity name: ", entity_name)
        print("Constraint: ", constraint)
        print()
    print("------- TRIGGERS -------")
    for trigger in hierarchy_checks.triggers:
        print(trigger)
        print()
    '''
    '''
    print("------- TABLES -------")
    
    for table in er_translator._tables.values():
        print(table.name)
        print()
        for primary_key in table.primary_keys:
            print("Primary key:")
            print(f" - name: {primary_key.name}, is_optional: {primary_key.is_optional}, is_unique: {primary_key.is_unique}")
            print()
        for attribute in table.attributes:
            print("Attribute:")
            print(f" - name: {attribute.name}, is_optional: {attribute.is_optional}, is_unique: {attribute.is_unique}")
            print()
        for foreign_key in table.foreign_keys:
            print("Foreign key:")
            print(f" - name: {foreign_key.name}, is_optional: {foreign_key.is_optional}, is_unique: {foreign_key.is_unique}, table_ref: {foreign_key.table_ref.name}, primary_key_ref: {foreign_key.primary_key_ref.name}")
            print()
        print()
    
    '''
    #print("------- SQL CODE -------")
    #print(sql__code)
    entities, relationships = create_diagram()
    choices_selector(entities, relationships)


