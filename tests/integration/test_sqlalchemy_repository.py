from tests.conftest import *


def test_sqlalchemy_repository_add_works(
    user_repo: UserRepository,
):
    new_user = User(user_id=999, name="Steve")
    user_repo.add(new_user)
    user_repo.save()

    actual = user_repo.session.query(User).all()
    assert actual == [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
        new_user,
    ]


def test_sqlalchemy_repository_resource_name_defaults_to_interface_name(
    session_factory: orm.sessionmaker
):
    session = session_factory()
    assert UserRepository(session=session).resource_name() == "AbstractUserRepository"
