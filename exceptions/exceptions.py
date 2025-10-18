class NoHierarchyExcpetion(Exception):
    def __init__(self, message="This entity has no hierarchy!"):
        self.message = message
        super().__init__(self.message)