class NonUniqueEntryError(Exception):
    def __init__(self, value):
        self.value = value

class InvalidEntryError(Exception):
    def __init__(self, value):
        self.value = value

class AnnotationConflictException(Exception):
    def __init__(self, value=None):
        print value
        self.value = value
