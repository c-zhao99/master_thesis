from erdplus_parser import *
from diagram_printer import *

if __name__ == "__main__":
    file_path = 'examples/every_possibility_no_hierarchy.erdplus'

    erdplus_parser = ERDPLUS_Parser()
    erdplus_parser.parse_erdplus_diagram(file_path)

    print_entities(erdplus_parser.entities.values())
    print_relationships(erdplus_parser.relationships.values())