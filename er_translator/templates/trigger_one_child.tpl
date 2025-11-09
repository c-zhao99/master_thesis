CREATE TRIGGER {trigger_name}
BEFORE INSERT ON {table_name}
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    NOT EXISTS(
        SELECT * FROM {entity_name}
        WHERE {conditions}
        AND {entity_name}.{selector_name} = {selector_value}
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of {child_name}!')