from pathlib import Path

from ..utils.utils import load_tpl_file

CWD = Path(__file__)
PREFIX = CWD.parent.parent
ATTRIBUTE = load_tpl_file(PREFIX.joinpath("templates").joinpath("attribute.tpl"))
CONSTRAINT = load_tpl_file(PREFIX.joinpath("templates").joinpath("contraint.tpl"))
REFERENCE = load_tpl_file(PREFIX.joinpath("templates").joinpath("reference.tpl"))
SELECTOR = load_tpl_file(PREFIX.joinpath("templates").joinpath("selector.tpl"))
TABLE = load_tpl_file(PREFIX.joinpath("templates").joinpath("table.tpl"))
TRIGGER_ONE_CHILD = load_tpl_file(PREFIX.joinpath("templates").joinpath("trigger_one_child.tpl"))
TRIGGER_BOTH_CHILDREN = load_tpl_file(PREFIX.joinpath("templates").joinpath("trigger_both_children.tpl"))

class SQLGenerator:
    @staticmethod
    def create_sql_attribute(attribute_name: str) -> str:
        params = {
                "attribute_name": attribute_name,
                "attribute_type": "VARCHAR(10)",
                "optional": "NOT NULL"
            }
        return ATTRIBUTE.format(**params)

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
    def create_sql_reference(attribute, table_name, primary_key) -> str:
        params = {
            "attribute": attribute,
            "table": table_name,
            "primary_key": primary_key
        }
        return REFERENCE.format(**params)

    @staticmethod
    def create_sql_constraint(selector_name, values) -> str:
        constraint_name = "".join(values.keys())
        conditions = []
        for key, value in values.items():
            conditions.append(f"({selector_name}={key} AND {value})")
        
        conditions = " OR ".join(conditions)

        params = {
            "constraint_name": constraint_name,
            "conditions": conditions
        }

        return CONSTRAINT.format(**params)

    @staticmethod
    def create_sql_trigger_before_insert(relationship, table, father, child, selector_name, foreign_key, other_child = None) -> str:
        table_name = table.name
        trigger_name = relationship.name + child.name
        primary_key = father.identifiers[0].name
        
        
        selector_value = child.name

        params = {
            "trigger_name": trigger_name,
            "table_name": table_name,
            "foreign_key": foreign_key,
            "primary_key": primary_key,
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