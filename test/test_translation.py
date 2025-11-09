import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from er_translator.parsers.erdplus_parser import ERDPLUS_Parser
from er_translator.translation.er_translation import ERTranslator
from er_translator.data.choices import HIERARCHY_CHOICE

def test_translation(file_path: Path):
    """
    Parse and translate a single ERDPlus diagram file.
    
    Args:
        file_path: Path to the .erdplus file to process
        
    Returns:
        str: Generated SQL code or error message
    """
    try:
        print(f"\n{'='*80}")
        print(f"Processing: {file_path.name}")
        print(f"{'='*80}")
        
        # Parse the diagram
        parser = ERDPLUS_Parser()
        parser.parse_erdplus_diagram(file_path)
        
        # Get entities and relationships
        entities = parser.entities
        relationships = parser.relationships
        
        # Create translator
        translator = ERTranslator(entities, relationships)
        
        # Get choices (using defaults)
        composite_choices, composite_defaults = translator.get_composite_attributes_choices()
        hierarchy_choices, hierarchy_defaults = translator.get_hierarchy_choices()
        relationship_choices, relationship_defaults = translator.get_relationship_choices()
    
        if file_path.stem.startswith("down"):
            for entity_name in hierarchy_defaults.keys():
                hierarchy_defaults[entity_name] = HIERARCHY_CHOICE.COLLAPSE_DOWNWARDS

        # Translate with default choices
        sql_code = translator.translate(
            composite_defaults,
            hierarchy_defaults,
            relationship_defaults
        )
        
        print("\nGenerated SQL:")
        print("-" * 80)
        #print(sql_code)
        print("-" * 80)
        
        return sql_code
        
    except Exception as e:
        error_msg = f"ERROR processing {file_path.name}: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return None

def compare_results_with_correct(result_dir: Path, correct_dir: Path):
    print("COMPARING RESULTS WITH EXPECTED OUTPUT\n")
    
    result_files = sorted(result_dir.glob("*.sql"))
    
    for result_file in result_files:
        correct_file = correct_dir / result_file.name
        
        # Read both files
        with open(result_file, 'r') as f:
            result_content = f.read()
        with open(correct_file, 'r') as f:
            correct_content = f.read()
        
        # Compare
        if result_content == correct_content:
            print(f"✓ {result_file.name}: MATCH")
        else:
            print(f"✗ {result_file.name}: DIFFERENT")
    

def test_all_examples():
    """
    Run translation on all .erdplus files in the examples directory.
    """
    # Get the examples directory
    examples_dir = Path(__file__).parent.parent / "er_translator" / "examples"
    
    # Create result directory if it doesn't exist
    result_dir = Path(__file__).parent / "result"
    result_dir.mkdir(exist_ok=True)
    
    # Get all .erdplus files
    erdplus_files = sorted(examples_dir.glob("*.erdplus"))
    
    print(f"\nFound {len(erdplus_files)} .erdplus files to process")
    
    failed = 0

    # Process each file
    for file_path in erdplus_files:
        if file_path.stem == "edizione_telegiornali" or file_path.stem == "every_possibility_no_hierarchy":
            print(f"\n Skipping {file_path.stem}")
            continue
        sql_code = test_translation(file_path)
        
        if sql_code is not None:
            # Save the result to a file
            output_file = result_dir / f"{file_path.stem}.sql"
            with open(output_file, 'w') as f:
                f.write(sql_code)
            print(f"✓ Saved output to: {output_file}")
        else:
            failed += 1
    
    print(f"\nFailed {failed} files")
    print(f"\nResults saved to: {result_dir}")
    
def check_differences(correct_dir: Path, result_dir: Path):
    # Compare results with correct files
    compare_results_with_correct(result_dir, correct_dir)
    

if __name__ == "__main__":
    test_all_examples()
    correct_dir = Path(__file__).parent / "correct"
    result_dir = Path(__file__).parent / "result"
    check_differences(correct_dir, result_dir)
