from pathlib import Path

from er_translator.data.conceptual import *
from er_translator.parsers.erdplus_parser import *
from er_translator.printers.diagram_printer import *
from er_translator.translation.hierarchy_translation import HierachyTranslator

def parse_erd_plus():
    file_path = Path(__file__).parent.joinpath('er_translator/examples/every_possibility_no_hierarchy.erdplus')

    erdplus_parser = ERDPLUS_Parser()
    erdplus_parser.parse_erdplus_diagram(file_path)

    print_entities(erdplus_parser.entities.values())
    print_relationships(erdplus_parser.relationships.values())

def create_diagram():
    # from E1 to E2
    r1_from = Cardinality(MinimumCardinality.ONE, MaximumCardinality.MANY)
    r1_to = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
    # from E2 to E2
    r2_from = Cardinality(MinimumCardinality.ONE, MaximumCardinality.MANY)
    r2_to = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
    # from E2 to E3
    r3_from = Cardinality(MinimumCardinality.ONE, MaximumCardinality.MANY)
    r3_to = Cardinality(MinimumCardinality.ONE, MaximumCardinality.MANY)
    # from E1 to E4
    r4_from = Cardinality(MinimumCardinality.ONE, MaximumCardinality.MANY)
    r4_to = Cardinality(MinimumCardinality.ONE, MaximumCardinality.MANY)

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
    father = Entity("E1")
    attribute_father = Attribute("A1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    father.add_identifier(attribute_father)
    
    #child1
    child1 = Entity("E2")
    attribute_child1 = Attribute("A2", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    child1.add_identifier(attribute_child1)

    #child2
    child2 = Entity("E3")
    attribute_child2 = Attribute("A3", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    child2.add_identifier(attribute_child2)
    
    #hierarchy
    hierarchy = Hierarchy(HierarchyCompleteness.TOTAL, HierarchyDisjointness.OVERLAPPING)
    hierarchy.add_child(child1)
    hierarchy.add_child(child2)
    father.set_hierarchy(hierarchy)

    #entity4
    entity4 = Entity("E4")
    attribute_entity4 = Attribute("A4", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    entity4.add_identifier(attribute_entity4)

    #add entitites
    entities["E1"] = father
    entities["E2"] = child1
    entities["E3"] = child2
    entities["E4"] = entity4

    #relationship R1
    r1 = Relationship("R1", "E1", "E2", r1_from, r1_to)
    #r2 = Relationship("R2", "E2", "E2", r2_from, r2_to)
    #r3 = Relationship("R3", "E2", "E3", r3_from, r3_to)
    #r4 = Relationship("R4", "E1", "E4", r4_from, r4_to)

    #add relationships
    relationships["R1"] = r1
    #relationships["R2"] = r2
    #relationships["R3"] = r3
    #relationships["R4"] = r4

    return entities, relationships


if __name__ == "__main__":
    #parse_erd_plus()
    entities, relationships = create_diagram()

    hieararchy_translator = HierachyTranslator(entities, relationships)
    hieararchy_translator.translate_hierarchies()
    print("------- SELECTORS -------")
    for selector in hieararchy_translator.hierarchy_checks.selectors:
        print(selector)
        print()
    print("------- CONSTRAINTS -------")
    for constraint in hieararchy_translator.hierarchy_checks.constraints:
        print(constraint)
        print()
    print("------- TRIGGERS -------")
    for trigger in hieararchy_translator.hierarchy_checks.triggers:
        print(trigger)
        print()