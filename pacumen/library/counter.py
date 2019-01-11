class Counter(dict):
    def total_count(self):
        """
        Returns the sum of counts for all keys.
        """
        return sum(self.values())

    def normalize(self):
        """
        Edits the counter such that the total count of all keys sums to 1.
        The ratio of counts for all keys will remain the same. Note that
        normalizing an empty Counter will result in an error.
        """
        total = float(self.total_count())

        if total == 0:
            return

        for key in list(self.keys()):
            self[key] = self[key] / total

    def __getitem__(self, idx):
        self.setdefault(idx, 0)
        return dict.__getitem__(self, idx)
