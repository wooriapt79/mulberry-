class Insurer:
    def __init__(self, name: str, has_api: bool):
        self.name = name
        self.has_api = has_api
        print(f"Insurer '{self.name}' initialized. API capability: {self.has_api}")
