from er_translator.data.conceptual import *

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
    
    e1 = Entity("E1")
    e1.add_identifier(Attribute("E1_ID1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True))
    e2 = Entity("E2")
    e2.add_identifier(Attribute("E2_ID1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True))
    e3 = Entity("E3")
    e3.add_identifier(Attribute("E3_ID1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True))

    r1_from = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
    r1_to = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
    r1 = Relationship("R1", "E1", "E2", r1_from, r1_to)
    r2_from = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
    r2_to = Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE)
    r2 = Relationship("R2", "E2", "E3", r2_from, r2_to)

    entities["E1"] = e1
    entities["E2"] = e2
    entities["E3"] = e3
    relationships["R1"] = r1
    relationships["R2"] = r2
    
    '''
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
    
    attr3 = CompositeAttribute("Child3-CompositeAttr", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    simple_attr1 = Attribute("Child3-SimpleAttr1-ATTR1", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    simple_attr2 = Attribute("Child3-SimpleAttr2-ATTR2", Cardinality(MinimumCardinality.ONE, MaximumCardinality.ONE), True)
    attr3.add_simple_attribute(simple_attr1)
    attr3.add_simple_attribute(simple_attr2)
    child3.add_identifier(attr3)
    child3.add_attribute(attr2)
    
    #hierarchy
    hierarchy = Hierarchy(HierarchyCompleteness.TOTAL, HierarchyDisjointness.DISJOINT)
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
    '''
    return entities, relationships