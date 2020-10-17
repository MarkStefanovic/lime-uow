import abc
import typing

from sqlalchemy import orm

from lime_uow import resources
from tests.conftest import User


class UserRepositoryInterface(resources.Repository[User], abc.ABC):
    @abc.abstractmethod
    def extra_method_a(self) -> str:
        raise NotImplementedError


class SqlAlchemyUserRepository(
    UserRepositoryInterface, resources.SqlAlchemyRepository[User]
):
    @property
    def entity_type(self) -> typing.Type[User]:
        return User

    def __init__(self, session: orm.Session):
        super().__init__(session)

    def extra_method_a(self):
        return "this is a test"


def test_sqlalchemy_repository_add_works(session_factory: orm.sessionmaker) -> None:
    session = session_factory()
    repo = SqlAlchemyUserRepository(session)
    new_user = User(user_id=999, name="Steve")
    repo.add(new_user)
    repo.save()
    actual = repo.session.query(User).all()
    assert actual == [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
        new_user,
    ]


def test_sqlalchemy_repository_resource_name_defaults_to_interface_name(
    session_factory: orm.sessionmaker,
) -> None:
    session = session_factory()
    repo = SqlAlchemyUserRepository(session=session)
    assert repo.resource_name() == "UserRepositoryInterface"


def test_sqlalchemy_repository_entity_type_reflects_type_parameter_of_implementation(
    session_factory: orm.sessionmaker,
) -> None:
    session = session_factory()
    repo = SqlAlchemyUserRepository(session=session)
    assert repo.entity_type == User
