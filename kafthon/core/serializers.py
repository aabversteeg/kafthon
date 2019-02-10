import base64
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
    def serialize(cls, data):
        return msgpack.packb(
            data,
            default=cls.obj_encoder,
            strict_types=True,
            encoding="utf-8"
        )

    @classmethod
    def deserialize(cls, data):
        return msgpack.unpackb(
            data,
            object_hook=cls.obj_decoder,
            encoding="utf-8"
        )

    def obj_encoder(obj):
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
