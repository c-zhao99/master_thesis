class Table:
    def __init__(self, name: str, primary_key: list["Attribute"], attributes: list["Attribute"]):
        self.name = name
        self.primary_key = primary_key
        self.foreign_key = []
        self.attributes = attributes

    def add_foreign_key(self, foreign_key: "ForeignKey"):
        self.foreign_key.append(foreign_key)

class Attribute:
    def __init__(self, name: str, attribute_type: type, is_optional: bool, is_unique: bool):
        self.name = name
        self.attribute_type = attribute_type
        self.is_optional = is_optional
        self.is_unique = is_unique
    
class ForeignKey(Attribute):
    def __init__(self, name: str, type: type, is_optional: bool, is_unique: bool, 
                 table_ref: Table, primary_key_ref: Attribute):
        super().__init__(name, type, is_optional, is_unique)
        self.table_ref = table_ref
        self.primary_key_ref = primary_key_ref
