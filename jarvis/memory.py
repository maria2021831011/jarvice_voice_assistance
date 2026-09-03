import json, os

class Memory:
    def __init__(self, file="data/memory.json"):
        self.file = file
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump([], f)

    def add(self, role, message):
        history = self.get_history()
        history.append({"role": role, "message": message})
        with open(self.file, "w") as f:
            json.dump(history, f, indent=2)

    def get_history(self):
        with open(self.file) as f:
            return json.load(f)

    def clear(self):
        with open(self.file, "w") as f:
            json.dump([], f)
