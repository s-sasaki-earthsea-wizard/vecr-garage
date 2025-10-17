import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class DBMemberConnection:
    def __init__(self):
        self.engine = create_engine(self._get_db_url())

    def _get_db_config(self) -> dict:
        return {
            "host": os.getenv("MEMBER_DB_HOST"),
            "port": os.getenv("MEMBER_DB_PORT"),
            "user": os.getenv("MEMBER_DB_USER"),
            "password": os.getenv("MEMBER_DB_PASSWORD"),
            "db_name": os.getenv("MEMBER_DB_NAME"),
        }

    def _get_db_url(self) -> str:
        db_config = self._get_db_config()
        return (
            f"postgresql://"
            f"{db_config['user']}:"
            f"{db_config['password']}@"
            f"{db_config['host']}:"
            f"{db_config['port']}/"
            f"{db_config['db_name']}"
        )

    def db_member_connection_check(self) -> Session:
        try:
            Session = sessionmaker(bind=self.engine)
            print("✅ Database connection established successfully.")
            return Session()
        except Exception as e:
            raise Exception(f"❌ Error establishing database connection: {e}")


def main():
    db_member_connection = DBMemberConnection()
    db_member_connection.db_member_connection_check()


if __name__ == "__main__":
    main()
