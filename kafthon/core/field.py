from typing import Type, Any


NOT_SET = object()


class Field():
    def __init__(self, field_type: Type, default: Any = NOT_SET):
        self.__field_type = field_type
        self.__default = default

    @property
    def field_type(self):
        return self.__field_type

    def get_default(self):
        if callable(self.__default):
            return self.__default()
        return self.__default
