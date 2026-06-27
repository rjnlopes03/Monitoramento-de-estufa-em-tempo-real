"""
Camada de persistência (SQLite).

Mantida isolada para que o restante do código não dependa do banco —
amanhã podemos trocar SQLite por PostgreSQL/InfluxDB sem tocar nos
assinantes. Isso faz parte da estratégia de escalabilidade do projeto.
"""
import os
import sqlite3
from contextlib import contextmanager

import config


def init_db():
    os.makedirs(os.path.dirname(config.DB_PATH) or ".", exist_ok=True)
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS leituras (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id   TEXT NOT NULL,
                setor       TEXT NOT NULL,
                temperatura REAL,
                umidade     REAL,
                timestamp   TEXT NOT NULL,
                recebido_em TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        c.execute("CREATE INDEX IF NOT EXISTS idx_sensor ON leituras(sensor_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_ts ON leituras(timestamp)")


@contextmanager
def _conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def salvar_leitura(leitura: dict):
    with _conn() as c:
        c.execute(
            """
            INSERT INTO leituras (sensor_id, setor, temperatura, umidade, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                leitura.get("sensor_id"),
                leitura.get("setor"),
                leitura.get("temperatura"),
                leitura.get("umidade"),
                leitura.get("timestamp"),
            ),
        )


def ultimas_leituras(limite: int = 50):
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM leituras ORDER BY id DESC LIMIT ?", (limite,)
        ).fetchall()
        return [dict(r) for r in rows]


def estado_atual():
    """Última leitura de cada sensor (visão de 'agora')."""
    with _conn() as c:
        rows = c.execute(
            """
            SELECT l.* FROM leituras l
            JOIN (
                SELECT sensor_id, MAX(id) AS max_id
                FROM leituras GROUP BY sensor_id
            ) m ON l.id = m.max_id
            ORDER BY l.setor, l.sensor_id
            """
        ).fetchall()
        return [dict(r) for r in rows]
