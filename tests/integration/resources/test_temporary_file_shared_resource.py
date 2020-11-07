import lime_uow as lu


def test_temporary_file_shared_resource():
    with lu.TempFileSharedResource(prefix="test", file_extension="txt") as file:
        file.add("test this\n")
        file.add("test again")
        assert file.file_path.name.startswith("test")
        assert file.file_path.name.endswith(".txt")
        file.save()
        assert file.all() == "test this\ntest again"
        file.clear()
        assert file.all() == ""
