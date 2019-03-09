from typing import Type, Any, Optional

from .utils import check_type_is_optional


NOT_SET = object()


class Field():
    def __init__(self, field_type: Type, default: Any = NOT_SET, is_required: bool = True):
        self.__field_type = field_type
        self.__default = default

        type_is_optional = check_type_is_optional(field_type)
        if type_is_optional:
            self.__is_required = False
        elif not is_required:
            self.__is_required = False
            self.__field_type = Optional[field_type]
        else:
            self.__is_required = True

    @property
    def field_type(self):
        return self.__field_type

    @property
    def is_required(self):
        return self.__is_required

    def get_default(self):
        if callable(self.__default):
            return self.__default()
        return self.__default
