#import click
from pathlib import Path

from er_translator.parsers.erdplus_parser import *
from er_translator.printers.diagram_printer import *
from er_generator import create_diagram
from choices_prompt import choices_selector


#@click.command()
#@click.argument('file_path', type=click.Path(exists=True))
def cli(file_path):
    """
    Parse and process an ERDPlus diagram file.
    
    FILE_PATH: Path to the .erdplus file to process
    """
    file_path = Path(file_path)
    
    erdplus_parser = ERDPLUS_Parser()
    erdplus_parser.parse_erdplus_diagram(file_path)
    entities = erdplus_parser.entities
    relationships = erdplus_parser.relationships
    
    #print_entities(erdplus_parser.entities.values())
    #print_relationships(erdplus_parser.relationships.values())

    entities, relationships = create_diagram()
    file_path = None
    choices_selector(entities, relationships, file_path)

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


if __name__ == "__main__":
    file_path = Path(__file__).parent.joinpath('er_translator/examples/down_t_d_N_1.erdplus')
    cli(file_path)