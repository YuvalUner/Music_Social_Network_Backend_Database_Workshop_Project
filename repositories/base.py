from app_conf import db_conn

from typing import Tuple, List


class BaseRepository:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._cursor = db_conn.cursor()

    def _execute_query(self, raw: str, *args) -> List[Tuple]:
        try:
            self._cursor.execute(raw, tuple(args))
            results = self._cursor.fetchall()
        except Exception as e:
            raise Exception(f"error on executing {raw} with args {args}: {str(e)}")
        finally:
            db_conn.commit()
        return results
