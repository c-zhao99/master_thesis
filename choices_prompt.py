from er_translator.translation.er_translation import ERTranslator
from er_translator.data.choices import HIERARCHY_CHOICE
from pathlib import Path

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


def choices_selector(entities, relationships, file_path=None):
    sql_code = ""
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

    for entity_name in current_hierarchy_choices.keys():
        current_hierarchy_choices[entity_name] = HIERARCHY_CHOICE.COLLAPSE_DOWNWARDS
    
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

    if sql_code and file_path:
        # Create result folder if it doesn't exist
        result_folder = Path(file_path).parent / "result"
        result_folder.mkdir(exist_ok=True)
        
        # Get filename without extension and create .sql file
        output_filename = Path(file_path).stem + ".sql"
        output_path = result_folder / output_filename
        
        # Write SQL code to file
        with open(output_path, 'w') as f:
            f.write(sql_code)
        
        print(f"\n SQL code written to: {output_path}")
