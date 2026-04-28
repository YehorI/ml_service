class HaveNoSessionError(Exception):
    def __init__(self):
        super().__init__("Have no actual session")
