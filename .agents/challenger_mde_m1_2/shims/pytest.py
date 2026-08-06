"""
Minimal pytest shim for running test_mde_ontology.py when pytest is not installed.
"""

class RaisesContext:
    def __init__(self, expected_exc):
        self.expected_exc = expected_exc
        self.exc_value = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"Expected exception {self.expected_exc.__name__} but none was raised.")
        if issubclass(exc_type, self.expected_exc):
            self.exc_value = exc_val
            return True
        return False

def raises(expected_exception):
    return RaisesContext(expected_exception)

def fixture(func):
    func._is_fixture = True
    return func
