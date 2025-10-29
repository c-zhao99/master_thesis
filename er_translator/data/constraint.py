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
        self.checks += checks

@dataclass
class Constraint:
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
