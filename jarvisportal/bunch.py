class Bunch:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = Bunch(value)
            self.__dict__[key] = value

