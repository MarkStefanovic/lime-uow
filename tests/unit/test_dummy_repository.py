import typing

import pytest

from lime_uow import resources
from tests.conftest import User


class TestDummyRepository(resources.DummyRepository[User]):
    def __init__(self, initial_users: typing.List[User]):
        super().__init__(
            initial_values=initial_users,
            key_fn=lambda user: user.user_id,
        )

    @classmethod
    def resource_name(cls) -> str:
        return "dummy_repo_repository"


@pytest.fixture
def dummy_repo() -> TestDummyRepository:
    return TestDummyRepository(
        [User(user_id=1, name="Mark"), User(user_id=2, name="Mandie")]
    )


def test_dummy_repository_add_method(dummy_repo: TestDummyRepository):
    dummy_repo.add(User(3, "Terri"))
    expected = [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
        User(user_id=3, name="Terri"),
    ]
    actual = dummy_repo.all()
    assert actual == expected
    assert dummy_repo.events == [
        ("add", {"item": User(user_id=3, name="Terri")}),
        ("all", {}),
    ]


def test_dummy_repository_add_all_method(dummy_repo: TestDummyRepository):
    new_users = (
        User(user_id=3, name="Terri"),
        User(user_id=4, name="Kellen"),
    )
    dummy_repo.add_all(new_users)
    expected = [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
        User(user_id=3, name="Terri"),
        User(user_id=4, name="Kellen"),
    ]
    actual = dummy_repo.all()
    assert actual == expected
    assert dummy_repo.events == [
        (
            "add_all",
            {
                "items": (
                    User(user_id=3, name="Terri"),
                    User(user_id=4, name="Kellen"),
                )
            },
        ),
        ("all", {}),
    ]


def test_dummy_repository_all_method(dummy_repo: TestDummyRepository):
    actual = dummy_repo.all()
    assert actual == [User(user_id=1, name="Mark"), User(user_id=2, name="Mandie")]
    assert dummy_repo.events == [("all", {})]


def test_dummy_repository_delete_method(dummy_repo: TestDummyRepository):
    dummy_repo.delete(User(1, "Mark"))
    expected = [
        User(user_id=2, name="Mandie"),
    ]
    actual = dummy_repo.all()
    assert actual == expected
    assert dummy_repo.events == [
        ("delete", {"item": User(user_id=1, name="Mark")}),
        ("all", {}),
    ]


def test_dummy_repository_delete_all_method(dummy_repo: TestDummyRepository):
    dummy_repo.delete_all()
    expected = []
    actual = dummy_repo.all()
    assert actual == expected
    assert dummy_repo.events == [
        ("delete_all", {}),
        ("all", {}),
    ]


def test_dummy_repository_get_method(dummy_repo: TestDummyRepository):
    actual = dummy_repo.get(1)
    expected = User(user_id=1, name="Mark")
    assert actual == expected
    assert dummy_repo.events == [("get", {"item_id": 1})]


def test_dummy_repository_update_method(dummy_repo: TestDummyRepository):
    dummy_repo.update(User(1, "Steve"))
    expected = [
        User(user_id=1, name="Steve"),
        User(user_id=2, name="Mandie"),
    ]
    actual = dummy_repo.all()
    assert actual == expected
    assert dummy_repo.events == [
        ("update", {"item": User(user_id=1, name="Steve")}),
        ("all", {}),
    ]


def test_dummy_repository_rollback_method(dummy_repo: TestDummyRepository):
    dummy_repo.update(User(1, "Steve"))
    dummy_repo.add(User(3, "Bill"))
    dummy_repo.delete(User(1, "Steve"))
    dummy_repo.rollback()
    expected = [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
    ]
    actual = dummy_repo.all()
    assert actual == expected
    assert dummy_repo.events == [
        ("update", {"item": User(user_id=1, name="Steve")}),
        ("add", {"item": User(user_id=3, name="Bill")}),
        ("delete", {"item": User(user_id=1, name="Steve")}),
        ("rollback", {}),
        ("all", {}),
    ]


def test_dummy_repository_save_method(dummy_repo: TestDummyRepository):
    dummy_repo.update(User(1, "Steve"))
    dummy_repo.add(User(3, "Bill"))
    dummy_repo.delete(User(1, "Steve"))
    dummy_repo.save()
    expected = [User(user_id=2, name="Mandie"), User(user_id=3, name="Bill")]
    actual = dummy_repo.all()
    assert actual == expected
    assert dummy_repo.events == [
        ("update", {"item": User(user_id=1, name="Steve")}),
        ("add", {"item": User(user_id=3, name="Bill")}),
        ("delete", {"item": User(user_id=1, name="Steve")}),
        ("save", {}),
        ("all", {}),
    ]


def test_dummy_repository_set_all_method(dummy_repo: TestDummyRepository):
    new_users = (
        User(user_id=3, name="Terri"),
        User(user_id=4, name="Kellen"),
    )
    dummy_repo.set_all(new_users)
    expected = [
        User(user_id=3, name="Terri"),
        User(user_id=4, name="Kellen"),
    ]
    actual = dummy_repo.all()
    assert actual == expected
    assert dummy_repo.events == [
        (
            "set_all",
            {
                "items": (
                    User(user_id=3, name="Terri"),
                    User(user_id=4, name="Kellen"),
                )
            },
        ),
        ("all", {}),
    ]
