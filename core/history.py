class HistoryManager:
    def __init__(self, limit=50):
        self.limit = limit
        self.data = []

    def add(self, entry):
        self.data.insert(0, entry)
        self.data = self.data[:self.limit]

    def get_all(self):
        return self.data
