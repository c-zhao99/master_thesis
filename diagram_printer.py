from data.conceptual import CompositeAttribute
def print_entities(entities):
    for entity in entities:
        print("-------------------")
        print(f" - entity name = {entity.name}")
        print(f" - identifiers")
        print("")
        for identifier in entity.identifier:
            print(f" - - identifier name = {identifier.name}")
            print(f" - - identifier cardinality = {identifier.cardinality}")
            print(f" - - identifier type = {identifier.attribute_type}")
            print("")
            if type(identifier) == CompositeAttribute:
                print("- composite attribute")
                print("")
                for simple_attribute in identifier.simple_attributes:
                    print(f" - - identifier name = {simple_attribute.name}")
                    print(f" - - identifier cardinality = {simple_attribute.cardinality}")
                    print(f" - - identifier type = {simple_attribute.attribute_type}")
                    print("")
                print("- end composite attribute")
                print("")
        print(f" - weak entity = {entity.weak_entity}")
        print(f" - attributes")
        print("")
        for attribute in entity.attributes:
            print(f" - - identifier name = {attribute.name}")
            print(f" - - identifier cardinality = {attribute.cardinality}")
            print(f" - - identifier type = {attribute.attribute_type}")
            print("")
            
            if type(attribute) == CompositeAttribute:
                print("- composite attribute")
                print("")
                for simple_attribute in attribute.simple_attributes:
                    print(f" - - identifier name = {simple_attribute.name}")
                    print(f" - - identifier cardinality = {simple_attribute.cardinality}")
                    print(f" - - identifier type = {simple_attribute.attribute_type}")
                    print("")
                print("- end composite attribute")
                print("")
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
        print(f" - cardinality from = {relationship.cardinality_from}")
        print(f" - cardinality to = {relationship.cardinality_to}")
