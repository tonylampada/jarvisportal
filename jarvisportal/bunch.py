class Bunch:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = Bunch(value)
            self.__dict__[key] = value

    def __iter__(self):
        for key, value in self.__dict__.items():
            if isinstance(value, Bunch):
                value = dict(value)
            yield (key, value)

    def __repr__(self):
        return f"Bunch({self.__dict__})"