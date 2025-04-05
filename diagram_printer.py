from data.conceptual import CompositeAttribute
def print_entities(entities):
    for entity in entities:
        print("-------------------")
        print(f" - entity name = {entity.name}")
        print(f" - identifiers = ")
        for identifier in entity.identifier:
            print(f" - - identifier name = {identifier.name}")
            print(f" - - identifier cardinality = ({identifier.cardinality.min_cardinality}, {identifier.cardinality.max_cardinality})")
            print(f" - - identifier type = {identifier.attribute_type}")
            if type(identifier) == CompositeAttribute:
                print("- - - composite attribute = ")
                for simple_attribute in identifier.simple_attributes:
                    print(f" - - - identifier name = {simple_attribute.name}")
                    print(f" - - - identifier cardinality = ({simple_attribute.cardinality.min_cardinality}, {simple_attribute.cardinality.max_cardinality})")
                    print(f" - - - identifier type = {simple_attribute.attribute_type}")
                    print("")
                print("- - - end composite attribute")
            print("")
        print(f" - end identifiers")
        print(f" - weak entity = {entity.weak_entity}")
        print(f" - attributes = ")
        for attribute in entity.attributes:
            print(f" - - attribute name = {attribute.name}")
            print(f" - - attribute cardinality = ({attribute.cardinality.min_cardinality}, {attribute.cardinality.max_cardinality})")
            print(f" - - attribute type = {attribute.attribute_type}")
            if type(attribute) == CompositeAttribute:
                print("- - - composite attribute = ")
                for simple_attribute in attribute.simple_attributes:
                    print(f" - - - attribute name = {simple_attribute.name}")
                    print(f" - - - attribute cardinality = ({simple_attribute.cardinality.min_cardinality}, {simple_attribute.cardinality.max_cardinality})")
                    print(f" - - - attribute type = {simple_attribute.attribute_type}")
                    print("")
                print("- - - end composite attribute")
            print("")
        print(f" - end attributes")
        print(f" - hierarchy")
        hierarchy = entity.hierarchy
        if hierarchy:
            for child in hierarchy.children:
                print(f" - - child name = {child}")
            print(f" - - hierarchy completeness = {hierarchy.hierarchy_completeness}")
            print(f" - - hierarchy disjointness = {hierarchy.hierarchy_disjointness}")

def print_relationships(relationships):
    for relationship in relationships:
        print("-------------------")
        print(f" - relationship name = {relationship.name}")
        print(f" - entity from = {relationship.entity_from}")
        print(f" - entity to = {relationship.entity_to}")
        print(f" - cardinality from = ({relationship.cardinality_from.min_cardinality}, {relationship.cardinality_from.max_cardinality})")
        print(f" - cardinality to = ({relationship.cardinality_to.min_cardinality}, {relationship.cardinality_to.max_cardinality})")
        print(f" - attributes = ")
        for attribute in relationship.attributes:
            print(f" - - attribute name = {attribute.name}")
            print(f" - - attribute cardinality = ({attribute.cardinality.min_cardinality}, {attribute.cardinality.max_cardinality})")
            print(f" - - attribute type = {attribute.attribute_type}")
            if type(attribute) == CompositeAttribute:
                print("- - - composite attribute = ")
                for simple_attribute in attribute.simple_attributes:
                    print(f" - - - attribute name = {simple_attribute.name}")
                    print(f" - - - attribute cardinality = ({simple_attribute.cardinality.min_cardinality}, {simple_attribute.cardinality.max_cardinality})")
                    print(f" - - - attribute type = {simple_attribute.attribute_type}")
                    print("")
                print("- - - end composite attribute")
            print("")
        print(f" - end attributes")
