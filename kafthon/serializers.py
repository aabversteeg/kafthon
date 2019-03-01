import base64
import typing
import datetime
from abc import ABCMeta, abstractstaticmethod

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

    def obj_encoder(obj):
        if isinstance(obj, typing.Mapping):
            obj = dict(obj)

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

    def obj_decoder(obj):
        if '__type__' in obj:
            if obj['__type__'] == 'temporenc.datetime':
                moment = temporenc.unpackb(
                    base64.b64decode(obj['__value__'])
                )
                obj = moment.datetime()
            else:
                raise TypeError('Cannot unpack type: ' + obj['__type__'])

        return obj
