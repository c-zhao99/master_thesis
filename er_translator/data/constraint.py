from dataclasses import dataclass

@dataclass
class Check:
    attribute_name: str
    isNull: bool

@dataclass
class Condition:
    selector_value: str
    checks: list[Check]

    def add_checks(self, checks: list[Check]):
        for new_check in checks:
            found = False
            for check in self.checks:
                if new_check.attribute_name == check.attribute_name:
                    found = True
                    break
            if not found:
                self.checks.append(new_check)
        

@dataclass
class Constraint:
    entity_name: str
    constraint_name: str
    selector_name: str
    conditions: list[Condition]

    def add_conditions(self, new_conditions: list[Condition]):
        for new_condition in new_conditions:
            found = False
            for condition in self.conditions:
                if new_condition.selector_value == condition.selector_value:
                    condition.add_checks(new_condition.checks)
                    found = True
                    break
            if not found:
                self.conditions.append(new_condition)
