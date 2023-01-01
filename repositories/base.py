from app_conf import db_conn

from typing import Tuple, List


class BaseRepository:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def _execute_query(self, raw: str, *args) -> List[Tuple]:
        with db_conn.cursor() as session:
            try:
                session.execute(raw, tuple(args))
                results = session.fetchall()
            except Exception as e:
                raise Exception(f"error on executing {raw} with args {args}: {str(e)}")
            finally:
                db_conn.commit()

        return results
