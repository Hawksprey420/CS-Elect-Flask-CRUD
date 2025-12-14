from __future__ import annotations

import MySQLdb

from config.config import SystemConfig


def connect_db():
    return MySQLdb.connect(
        host=SystemConfig.MYSQL_HOST,
        user=SystemConfig.MYSQL_USER,
        passwd=SystemConfig.MYSQL_PASSWORD,
        db=SystemConfig.MYSQL_DB,
        port=SystemConfig.MYSQL_PORT,
    )


def next_id(cursor, table: str, id_column: str) -> int:
    cursor.execute(f"SELECT COALESCE(MAX({id_column}), 0) FROM {table}")
    return int(cursor.fetchone()[0]) + 1
