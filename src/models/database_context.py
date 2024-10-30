import sqlite3
from pathlib import Path
from types import TracebackType
from typing import Optional, Union, overload


class DatabaseConnection:
    """Simple context manager for sqlite3 databases"""

    def __init__(self, path: Union[Path, str]):
        self.path: Union[Path, str] = path
        self.conn: sqlite3.Connection
        self.cursor: sqlite3.Cursor

    def __enter__(self) -> sqlite3.Cursor:
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys=ON;")
        return self.cursor

    @overload
    def __exit__(self, exc_type: None, exc_val: None, exc_tb: None) -> None: ...

    @overload
    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ): ...

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        self.conn.commit()
        self.conn.close()
