import abc

import pytest

from lime_uow import exceptions
from lime_uow.resources import _get_next_descendant_of  # noqa


class RedHerring(abc.ABC):
    @abc.abstractmethod
    def distraction(self):
        raise NotImplementedError


class A(abc.ABC):
    ...


class B(A, RedHerring, abc.ABC):
    ...


class C(B, abc.ABC):
    ...


class D(C):
    def distraction(self):
        print("Loud noises!")

    def __init__(self):
        super().__init__()

class E:
    ...


def test_get_next_descendant_of_happy_path():
    next_descendant = _get_next_descendant_of(D, A)
    assert next_descendant is C


def test_get_next_descendant_of_unhappy_path():
    with pytest.raises(exceptions.NoCommonAncestor):
        _get_next_descendant_of(E, C)
