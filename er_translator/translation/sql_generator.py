from pathlib import Path

from ..data.conceptual import *
from ..data.constraint import *
from ..utils.utils import load_tpl_file, get_primary_keys



SELECTOR_PREFIX = "TYPE_"

CWD = Path(__file__)
PREFIX = CWD.parent.parent
ATTRIBUTE = load_tpl_file(PREFIX.joinpath("templates").joinpath("attribute.tpl"))
CONSTRAINT = load_tpl_file(PREFIX.joinpath("templates").joinpath("contraint.tpl"))
REFERENCE = load_tpl_file(PREFIX.joinpath("templates").joinpath("reference.tpl"))
SELECTOR = load_tpl_file(PREFIX.joinpath("templates").joinpath("selector.tpl"))
TABLE = load_tpl_file(PREFIX.joinpath("templates").joinpath("table.tpl"))
TRIGGER_ONE_CHILD = load_tpl_file(PREFIX.joinpath("templates").joinpath("trigger_one_child.tpl"))
TRIGGER_BOTH_CHILDREN = load_tpl_file(PREFIX.joinpath("templates").joinpath("trigger_both_children.tpl"))
TRIGGER_DOWNWARDS = load_tpl_file(PREFIX.joinpath("templates").joinpath("trigger_downwards.tpl"))

class SQLGenerator:
    @staticmethod
    def create_sql_table(table_name, attributes, selectors, references, primary_keys, constraints) -> str:
        attributes_list = ""
        if attributes:
            attributes_list = ",\n    ".join(attributes)
            attributes_list += ","
        selectors_list = ""
        if selectors:
            selectors_list = ",\n    ".join(selectors)
            selectors_list += ","
        references_list = ""
        if references:
            references_list = ",\n    ".join(references)
            references_list += ","
        primary_keys_list = ",".join(primary_keys)
        if constraints:
            primary_keys_list += "),"
        else:
            primary_keys_list += ")"
        constraints_list = ""
        if constraints:
            constraints_list = ",\n    ".join(constraints)
            constraints_list = constraints_list
        
        params = {
            "table_name": table_name,
            "attributes": attributes_list,
            "selectors": selectors_list,
            "references": references_list,
            "primary_keys": primary_keys_list,
            "constraints": constraints_list,

        }

        return TABLE.format(**params)
    
    @staticmethod
    def create_sql_attribute(attribute_name: str) -> str:
        params = {
                "attribute_name": attribute_name,
                "attribute_type": "VARCHAR(10)",
                "optional": "NOT NULL"
            }
        return ATTRIBUTE.format(**params)

    @staticmethod
    def create_sql_reference(attribute, table_name, primary_key) -> str:
        params = {
            "attribute": attribute,
            "table": table_name,
            "primary_key": primary_key
        }
        return REFERENCE.format(**params)

    @staticmethod
    def create_sql_selector(name: str, values: list[str]) -> str:
        params = {
            "selector_name": name,
            "selector_type": "VARCHAR(50)",
            "optional": "NOT NULL",
            "values": values
        }
        return SELECTOR.format(**params)



    @staticmethod
    def create_sql_constraint(constraint: Constraint) -> str:
        constraint_name = constraint.constraint_name
        selector_name = constraint.selector_name
        conditions = constraint.conditions

        complete_conditions = []
        for condition in conditions:
            selector_value = condition.selector_value
            checks = condition.checks
            complete_checks = []
            for check in checks:
                attribute_name = check.attribute_name
                attribute_value = "NULL" if check.isNull else "NOT NULL"

                complete_check = f"{attribute_name} = {attribute_value}"
                complete_checks.append(complete_check)
            complete_condition = f"{selector_name} + {selector_value} AND {" AND ".join(complete_checks)}"
            complete_conditions.append(complete_condition)
        
        params = {
            "constraint_name": constraint_name,
            "conditions": complete_conditions
        }

        return CONSTRAINT.format(**params)

    @staticmethod
    def create_sql_total_constraint(children_names) -> str:
        constraint_name = "TOTAL_HIERARCHY"
        conditions = []
        
        for name in children_names:
            conditions.append(f"{SELECTOR_PREFIX}{name}=1")
        
        conditions = " OR ".join(conditions)

        params = {
            "constraint_name": constraint_name,
            "conditions": "(" + conditions + ")"
        }

        return CONSTRAINT.format(**params)
    
    @staticmethod
    def create_sql_trigger_before_insert(relationship, table_name, father, connected_child, selector_name, other_child = None) -> str:
        trigger_name = relationship.name + connected_child.name
        primary_keys = get_primary_keys(father)
        conditions = []

        for primary_key in primary_keys:
            condition = f"{table_name}.{primary_key} = N.{primary_key}{relationship.name}"
            conditions.append(condition)
        
        hierarchy = father.hierarchy
        if hierarchy.hierarchy_disjointness == HierarchyDisjointness.DISJOINT:
            selector_value = connected_child.name
        else:
            selector_value = 1
        
        params = {
            "trigger_name": trigger_name,
            "table_name": table_name,
            "conditions": " AND ".join(conditions),
            "selector_name": selector_name,
            "selector_value": selector_value,
            "entity_name": father.name
        }
        
        if other_child:
            params.update({
                "new_selector_value": other_child.name
            })
            return TRIGGER_BOTH_CHILDREN.format(**params)
        
        return TRIGGER_ONE_CHILD.format(**params)

    @staticmethod
    def create_sql_constraint_downwards(constraint_name, values) -> str:
        conditions = " OR ".join(values)

        params = {
            "constraint_name": constraint_name,
            "conditions": conditions
        }

        return CONSTRAINT.format(**params)
    
    @staticmethod
    def create_sql_downwards_trigger(relationship_name, child_name, other_child_name, table_name = None, other_table_name = None) -> str:
        params = {
            "trigger_name": relationship_name + child_name,
            "table_name": table_name if table_name else child_name,
            "reference_child": relationship_name + child_name,
            "other_table_name": other_table_name if other_table_name else other_child_name,
            "reference_other_child": relationship_name + other_child_name,
            "relationship_name": relationship_name
        }
        return TRIGGER_DOWNWARDS.format(**params)
    