class HierarchyChecks:
    def __init__(self):
        self._selectors = {}
        self._constraints = {}
        self._triggers = []

    @property
    def selectors(self):
        return self._selectors
    
    @property
    def constraints(self):
        return self._constraints
    
    @property
    def triggers(self):
        return self._triggers
    
    def add_selector(self, entity_name: str, selector: str):
        if entity_name in self._selectors:
            self._selectors[entity_name].append(selector)
        else:
            self._selectors[entity_name] = [selector]

    def add_constraint(self, entity_name: str, constraint: str):
        if entity_name in self._constraints:
            self._constraints[entity_name].append(constraint)
        else:
            self._constraints[entity_name] = [constraint]
        

    def add_trigger(self, trigger: str):
        self._triggers.append(trigger)