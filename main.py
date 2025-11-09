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

    choices_selector(entities, relationships, file_path)

if __name__ == "__main__":
    file_path = Path(__file__).parent.joinpath('er_translator/examples/down_t_d_N_1.erdplus')
    cli(file_path)