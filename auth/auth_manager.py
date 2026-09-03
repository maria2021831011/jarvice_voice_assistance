import json, os, hashlib

class AuthManager:
    def __init__(self, path="data/users.json"):
        self.path = path
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump({}, f)

    def _hash(self, pwd):
        return hashlib.sha256(pwd.encode()).hexdigest()

    def register(self, user, pwd):
        users = self._load()
        if user in users:
            return False
        users[user] = self._hash(pwd)
        self._save(users)
        return True

    def login(self, user, pwd):
        users = self._load()
        return users.get(user) == self._hash(pwd)

    def _load(self):
        with open(self.path) as f:
            return json.load(f)

    def _save(self, users):
        with open(self.path, "w") as f:
            json.dump(users, f, indent=2)
