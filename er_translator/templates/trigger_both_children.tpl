CREATE TRIGGER {trigger_name}
BEFORE INSERT ON {table_name}
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    N.{selector_name} = {new_selector_value} AND NOT EXISTS(
        SELECT * FROM {entity_name}
        WHERE {entity_name}.{primary_key} = N.{foreign_key}
        AND {entity_name}.{selector_name} = {selector_value}
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of {selector_value}!')