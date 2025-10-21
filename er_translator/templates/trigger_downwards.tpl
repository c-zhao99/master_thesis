CREATE TRIGGER {trigger_name}
BEFORE INSERT ON {table_name}
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    EXISTS(
        SELECT *
        FROM {other_table_name}
        WHERE N.{reference_child} = {other_table_name}.{reference_other_child}
    )
)
SIGNAL SQLSTATE '70001' ('Only one relationship active at a time for {relationship_name}!')