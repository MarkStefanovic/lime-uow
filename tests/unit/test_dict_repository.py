from lime_uow import *
from tests.conftest import User


def test_dict_repository_all_method():
    d = DictRepository(
        name="test",
        initial_values={1: User(1, "Mark"), 2: User(2, "Mandie")},
        key_fn=lambda user: user.id,
    )
    with d.open() as repo:
        expected = [User(id=1, name="Mark"), User(id=2, name="Mandie")]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [("open", {}), ("all", {})]


def test_dict_repository_add_method():
    d = DictRepository(
        name="test",
        initial_values={1: User(1, "Mark"), 2: User(2, "Mandie")},
        key_fn=lambda user: user.id,
    )
    with d.open() as repo:
        repo.add(User(3, "Terri"))
        expected = [
            User(id=1, name="Mark"),
            User(id=2, name="Mandie"),
            User(id=3, name="Terri"),
        ]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("add", {"item": User(id=3, name="Terri")}),
            ("all", {}),
        ]


def test_dict_repository_delete_method():
    d = DictRepository(
        name="test",
        initial_values={1: User(1, "Mark"), 2: User(2, "Mandie")},
        key_fn=lambda user: user.id,
    )
    with d.open() as repo:
        repo.delete(User(1, "Mark"))
        expected = [
            User(id=2, name="Mandie"),
        ]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("delete", {"item": User(id=1, name="Mark")}),
            ("all", {}),
        ]


def test_dict_repository_get_method():
    d = DictRepository(
        name="test",
        initial_values={1: User(1, "Mark"), 2: User(2, "Mandie")},
        key_fn=lambda user: user.id,
    )
    with d.open() as repo:
        actual = repo.get(1)
        expected = User(id=1, name="Mark")
        assert actual == expected
        assert repo.events == [("open", {}), ("get", {"item_id": 1})]


def test_dict_repository_update_method():
    d = DictRepository(
        name="test",
        initial_values={1: User(1, "Mark"), 2: User(2, "Mandie")},
        key_fn=lambda user: user.id,
    )
    with d.open() as repo:
        repo.update(User(1, "Steve"))
        expected = [
            User(id=1, name="Steve"),
            User(id=2, name="Mandie"),
        ]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("update", {"item": User(id=1, name="Steve")}),
            ("all", {}),
        ]


def test_dict_repository_rollback_method():
    d = DictRepository(
        name="test",
        initial_values={1: User(1, "Mark"), 2: User(2, "Mandie")},
        key_fn=lambda user: user.id,
    )
    with d.open() as repo:
        repo.update(User(1, "Steve"))
        repo.add(User(3, "Bill"))
        repo.delete(User(1, "Steve"))
        repo.rollback()
        expected = [
            User(id=1, name="Mark"),
            User(id=2, name="Mandie"),
        ]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("update", {"item": User(id=1, name="Steve")}),
            ("add", {"item": User(id=3, name="Bill")}),
            ("delete", {"item": User(id=1, name="Steve")}),
            ("rollback", {}),
            ("all", {}),
        ]


def test_dict_repository_save_method():
    d = DictRepository(
        name="test",
        initial_values={1: User(1, "Mark"), 2: User(2, "Mandie")},
        key_fn=lambda user: user.id,
    )
    with d.open() as repo:
        repo.update(User(1, "Steve"))
        repo.add(User(3, "Bill"))
        repo.delete(User(1, "Steve"))
        repo.save()
        expected = [User(id=2, name="Mandie"), User(id=3, name="Bill")]
        actual = repo.all()
        assert actual == expected
        assert repo.events == [
            ("open", {}),
            ("update", {"item": User(id=1, name="Steve")}),
            ("add", {"item": User(id=3, name="Bill")}),
            ("delete", {"item": User(id=1, name="Steve")}),
            ("save", {}),
            ("all", {}),
        ]
