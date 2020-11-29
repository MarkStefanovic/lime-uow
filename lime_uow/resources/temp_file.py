from __future__ import annotations

import os
import pathlib
import tempfile
import types
import typing

from lime_uow.resources import resource

__all__ = ("TempFileSharedResource",)


class TempFileSharedResource(resource.Resource[typing.IO[bytes]]):
    def __init__(
        self,
        *,
        prefix: typing.Optional[str] = None,
        file_extension: typing.Optional[str] = None,
    ):
        self._prefix = prefix
        self._file_extension = file_extension

        self._file_handle: typing.Optional[typing.IO[bytes]] = None
        self._file_path: typing.Optional[pathlib.Path] = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[types.TracebackType],
    ) -> typing.Literal[False]:
        self.close()
        return False

    def clear(self):
        self.handle.seek(0, 0)  # go to beginning of file
        self.handle.truncate()

    def close(self) -> None:
        self.handle.close()
        os.unlink(self.file_path)

    @property
    def handle(self) -> typing.IO[bytes]:
        if self._file_handle is None:
            self.open()
        return self._file_handle  # type: ignore

    @classmethod
    def interface(cls) -> typing.Type[TempFileSharedResource]:
        return cls

    @property
    def file_path(self) -> pathlib.Path:
        if self._file_path is None:
            self._file_path = pathlib.Path(self.handle.name)
        return self._file_path

    def open(self) -> typing.IO[bytes]:
        ext = f".{self._file_extension}" if self._file_extension else None
        self._file_handle = tempfile.NamedTemporaryFile(
            prefix=self._prefix,
            suffix=ext,
            delete=False,
        )
        return self._file_handle

    def all(self) -> str:
        self.handle.seek(0, 0)  # go to beginning of file
        content = self.handle.read()
        self.handle.seek(0, 2)  # go to end of file
        return content.decode()

    def save(self) -> None:
        self.handle.flush()

    def add(self, content: str) -> None:
        self.handle.write(content.encode())
