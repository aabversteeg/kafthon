import base64
import typing
import datetime
from abc import ABCMeta, abstractstaticmethod

import pandas as pd
import msgpack
import temporenc


class BaseSerializer(metaclass=ABCMeta):
    @abstractstaticmethod
    def serialize(data):
        pass

    @abstractstaticmethod
    def deserialize(data):
        pass


class MsgpackSerializer(BaseSerializer):
    @classmethod
    def serialize(cls, data, as_base64=False):
        packed = msgpack.packb(
            data,
            default=cls.obj_encoder,
            strict_types=True
        )
        if as_base64:
            return base64.b64encode(packed)
        return packed

    @classmethod
    def deserialize(cls, data):
        if isinstance(data, str):
            data = base64.b64decode(data)

        return msgpack.unpackb(
            data,
            object_hook=cls.obj_decoder,
            raw=False
        )

    @staticmethod
    def obj_encoder(obj):
        if isinstance(obj, typing.Mapping):
            return dict(obj)

        if isinstance(obj, pd.DataFrame):
            return dict(
                __type__='pandas.DataFrame',
                __value__=base64.b64encode(
                    obj.to_msgpack()
                )
            )

        if isinstance(obj, datetime.datetime):
            return dict(
                __type__='temporenc.datetime',
                __value__=base64.b64encode(
                    temporenc.packb(obj)
                )
            )

        if isinstance(obj, tuple):
            return list(obj)

        return obj

    @staticmethod
    def obj_decoder(obj):
        if '__type__' in obj:
            _type, value = obj['__type__'], obj['__value__']

            if _type == 'temporenc.datetime':
                obj = temporenc.unpackb(
                    base64.b64decode(value)
                ).datetime()

            elif _type == 'pandas.DataFrame':
                obj = pd.read_msgpack(
                    base64.b64decode(value)
                )

            else:
                raise TypeError('Cannot unpack type: ' + _type)

        return obj
