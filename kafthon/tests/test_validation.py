import pytest

from kafthon.core.exceptions import ValidationError
from .fixture import MyEvent, app


def test_validation_success():
    MyEvent(x=0, y=0).validate()


def test_validation_fail_type():
    with pytest.raises(ValidationError):
        MyEvent(x='1', y=0).validate()


def test_validation_fail_missing_key():
    with pytest.raises(ValidationError):
        MyEvent(y=0).validate()


def test_validation_fail_invalid_key():
    with pytest.raises(ValidationError):
        MyEvent(x=0, y=0, q=2).validate()


def test_validation_skip_when_sent(monkeypatch):
    monkeypatch.setattr(app, 'validate_events', False)
    MyEvent(x='1').send()
