import operator
from typing import Dict

import typeguard

from .field import Field
from .exceptions import ValidationError


class FieldMapping():
    def __init__(self, fields: Dict[str, Field]):
        self.__fields = fields

    @property
    def fields(self):
        return self.__fields

    @property
    def all_field_names(self):
        return frozenset(
            self.__fields.keys()
        )

    @property
    def required_field_names(self):
        return frozenset(
            name
            for name, field in self.__fields.items()
            if field.is_required
        )

    def __getitem__(self, field_name):
        if field_name not in self.fields:
            raise KeyError(f'No field present with name {field_name}')
        return self.fields[field_name]

    def validate_event(self, event):
        __tracebackhide__ = operator.methodcaller("errisinstance", ValidationError)
        errors = []
        missing_fields = []
        event_field_names = set(event.keys())

        correct_fields = event_field_names & self.all_field_names
        missing_fields = self.required_field_names - event_field_names
        invalid_fields = event_field_names - self.all_field_names

        for field_name in correct_fields:
            field = self[field_name]
            try:
                event_name = type(event).__name__
                typeguard.check_type(
                    f'{event_name}.{field_name}',
                    event[field_name],
                    field.field_type
                )
            except TypeError as e:
                errors.append(e)

        if missing_fields:
            errors.append(
                KeyError(
                    'Missing event field%s found: %s' % (
                        's' if len(missing_fields) != 1 else '',
                        ', '.join(missing_fields)
                    )
                )
            )

        if invalid_fields:
            errors.append(
                KeyError(
                    '%s, undefined field%s found: %s' % (
                        type(event).__name__,
                        's' if len(invalid_fields) != 1 else '',
                        ', '.join(invalid_fields)
                    )
                )
            )

        if errors:
            raise ValidationError([errors])
