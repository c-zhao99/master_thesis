class Table:
    def __init__(self, name: str, primary_keys: list["Attribute"], attributes: list["Attribute"]):
        self.name = name
        self.primary_keys = primary_keys
        self.foreign_keys = []
        self.attributes = attributes

    def add_foreign_key(self, foreign_key: "ForeignKey") -> None:
        self.foreign_keys.append(foreign_key)

    def add_attribute(self, attribute: "Attribute") -> None:
        self.attributes.append(attribute)

class Attribute:
    def __init__(self, name: str, is_optional: bool, is_unique: bool):
        self.name = name
        self.is_optional = is_optional
        self.is_unique = is_unique
    
class ForeignKey(Attribute):
    def __init__(self, name: str, is_optional: bool, is_unique: bool, 
                 table_ref: Table, primary_key_ref: Attribute):
        super().__init__(name, is_optional, is_unique)
        self.table_ref = table_ref
        self.primary_key_ref = primary_key_ref
