class HierarchyChecks:
    def __init__(self):
        self._selectors = []
        self._constraints = []
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
    
    def add_selector(self, selector: str):
        self._selectors.append(selector)

    def add_constraint(self, constraint: str):
        self._constraints.append(constraint)

    def add_trigger(self, trigger: str):
        self._triggers.append(trigger)