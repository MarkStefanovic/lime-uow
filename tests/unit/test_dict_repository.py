from tests.conftest import *


class DummyDictRepository(resources.DictRepository):
    def __init__(self, initial_users: typing.List[User]):
        super(DummyDictRepository, self).__init__(
            initial_values={user.user_id: user for user in initial_users},
            key_fn=lambda user: user.user_id,
        )

    @property
    def resource_name(self) -> str:
        return "dummy_dict_repository"


@pytest.fixture
def dummy_dict() -> DummyDictRepository:
    return DummyDictRepository(
        [User(user_id=1, name="Mark"), User(user_id=2, name="Mandie")]
    )


def test_dict_repository_all_method(dummy_dict: DummyDictRepository):
    actual = dummy_dict.all()
    assert actual == [User(user_id=1, name="Mark"), User(user_id=2, name="Mandie")]
    assert dummy_dict.events == [("all", {})]


def test_dict_repository_add_method(dummy_dict: DummyDictRepository):
    dummy_dict.add(User(3, "Terri"))
    expected = [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
        User(user_id=3, name="Terri"),
    ]
    actual = dummy_dict.all()
    assert actual == expected
    assert dummy_dict.events == [
        ("add", {"item": User(user_id=3, name="Terri")}),
        ("all", {}),
    ]


def test_dict_repository_delete_method(dummy_dict: DummyDictRepository):
    dummy_dict.delete(User(1, "Mark"))
    expected = [
        User(user_id=2, name="Mandie"),
    ]
    actual = dummy_dict.all()
    assert actual == expected
    assert dummy_dict.events == [
        ("delete", {"item": User(user_id=1, name="Mark")}),
        ("all", {}),
    ]


def test_dict_repository_get_method(dummy_dict: DummyDictRepository):
    actual = dummy_dict.get(1)
    expected = User(user_id=1, name="Mark")
    assert actual == expected
    assert dummy_dict.events == [("get", {"item_id": 1})]


def test_dict_repository_update_method(dummy_dict: DummyDictRepository):
    dummy_dict.update(User(1, "Steve"))
    expected = [
        User(user_id=1, name="Steve"),
        User(user_id=2, name="Mandie"),
    ]
    actual = dummy_dict.all()
    assert actual == expected
    assert dummy_dict.events == [
        ("update", {"item": User(user_id=1, name="Steve")}),
        ("all", {}),
    ]


def test_dict_repository_rollback_method(dummy_dict: DummyDictRepository):
    dummy_dict.update(User(1, "Steve"))
    dummy_dict.add(User(3, "Bill"))
    dummy_dict.delete(User(1, "Steve"))
    dummy_dict.rollback()
    expected = [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
    ]
    actual = dummy_dict.all()
    assert actual == expected
    assert dummy_dict.events == [
        ("update", {"item": User(user_id=1, name="Steve")}),
        ("add", {"item": User(user_id=3, name="Bill")}),
        ("delete", {"item": User(user_id=1, name="Steve")}),
        ("rollback", {}),
        ("all", {}),
    ]


def test_dict_repository_save_method(dummy_dict: DummyDictRepository):
    dummy_dict.update(User(1, "Steve"))
    dummy_dict.add(User(3, "Bill"))
    dummy_dict.delete(User(1, "Steve"))
    dummy_dict.save()
    expected = [User(user_id=2, name="Mandie"), User(user_id=3, name="Bill")]
    actual = dummy_dict.all()
    assert actual == expected
    assert dummy_dict.events == [
        ("update", {"item": User(user_id=1, name="Steve")}),
        ("add", {"item": User(user_id=3, name="Bill")}),
        ("delete", {"item": User(user_id=1, name="Steve")}),
        ("save", {}),
        ("all", {}),
    ]
