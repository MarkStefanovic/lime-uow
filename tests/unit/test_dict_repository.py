from tests.conftest import *


class DummyDictRepository(resources.DictRepository):
    __resource_name__ = "dummy_dict_repository"

    def __init__(self, initial_users: typing.List[User]):
        super(DummyDictRepository, self).__init__(
            initial_values={user.user_id: user for user in initial_users},
            key_fn=lambda user: user.user_id,
        )


def test_dict_repository_all_method(initial_users: typing.List[User]):
    d = DummyDictRepository(initial_users)
    with d.open() as repo:
        actual = repo.all()
        assert actual == initial_users
        assert repo.events == [("open", {}), ("all", {})]


def test_dict_repository_add_method(initial_users: typing.List[User]):
    d = DummyDictRepository(initial_users)
    with d.open() as repo:
        repo.add(User(3, "Terri"))
        expected = [
            User(user_id=1, name="Mark"),
            User(user_id=2, name="Mandie"),
            User(user_id=3, name="Terri"),
        ]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("add", {"item": User(user_id=3, name="Terri")}),
            ("all", {}),
        ]


def test_dict_repository_delete_method(initial_users: typing.List[User]):
    d = DummyDictRepository(initial_users)
    with d.open() as repo:
        repo.delete(User(1, "Mark"))
        expected = [
            User(user_id=2, name="Mandie"),
        ]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("delete", {"item": User(user_id=1, name="Mark")}),
            ("all", {}),
        ]


def test_dict_repository_get_method(initial_users: typing.List[User]):
    d = DummyDictRepository(initial_users)
    with d.open() as repo:
        actual = repo.get(1)
        expected = User(user_id=1, name="Mark")
        assert actual == expected
        assert repo.events == [("open", {}), ("get", {"item_id": 1})]


def test_dict_repository_update_method(initial_users: typing.List[User]):
    d = DummyDictRepository(initial_users)
    with d.open() as repo:
        repo.update(User(1, "Steve"))
        expected = [
            User(user_id=1, name="Steve"),
            User(user_id=2, name="Mandie"),
        ]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("update", {"item": User(user_id=1, name="Steve")}),
            ("all", {}),
        ]


def test_dict_repository_rollback_method(initial_users: typing.List[User]):
    d = DummyDictRepository(initial_users)
    with d.open() as repo:
        repo.update(User(1, "Steve"))
        repo.add(User(3, "Bill"))
        repo.delete(User(1, "Steve"))
        repo.rollback()
        expected = [
            User(user_id=1, name="Mark"),
            User(user_id=2, name="Mandie"),
        ]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("update", {"item": User(user_id=1, name="Steve")}),
            ("add", {"item": User(user_id=3, name="Bill")}),
            ("delete", {"item": User(user_id=1, name="Steve")}),
            ("rollback", {}),
            ("all", {}),
        ]


def test_dict_repository_save_method(initial_users: typing.List[User]):
    d = DummyDictRepository(initial_users)
    with d.open() as repo:
        repo.update(User(1, "Steve"))
        repo.add(User(3, "Bill"))
        repo.delete(User(1, "Steve"))
        repo.save()
        expected = [User(user_id=2, name="Mandie"), User(user_id=3, name="Bill")]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("update", {"item": User(user_id=1, name="Steve")}),
            ("add", {"item": User(user_id=3, name="Bill")}),
            ("delete", {"item": User(user_id=1, name="Steve")}),
            ("save", {}),
            ("all", {}),
        ]
