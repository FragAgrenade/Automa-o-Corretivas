import sqlite3
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, caminho_banco: str | Path):
        self.caminho_banco = Path(caminho_banco)

    def inicializar(self) -> None:
        self.caminho_banco.parent.mkdir(parents=True, exist_ok=True)

        conexao = sqlite3.connect(self.caminho_banco)

        try:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS historico_execucao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_os TEXT NOT NULL,
                    tipo_os TEXT,
                    abriu_corretiva INTEGER NOT NULL DEFAULT 0,
                    motivo TEXT,
                    status TEXT NOT NULL,
                    erro TEXT,
                    data_execucao TEXT NOT NULL
                )
                """
            )
            conexao.commit()
        finally:
            conexao.close()

    def registrar_execucao(
        self,
        numero_os: str,
        tipo_os: str | None,
        abriu_corretiva: bool,
        motivo: str = "",
        status: str = "concluida",
        erro: str = "",
    ) -> None:
        data_execucao = datetime.now().isoformat(timespec="seconds")
        conexao = sqlite3.connect(self.caminho_banco)

        try:
            conexao.execute(
                """
                INSERT INTO historico_execucao
                (numero_os, tipo_os, abriu_corretiva, motivo, status, erro, data_execucao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    numero_os,
                    tipo_os,
                    int(abriu_corretiva),
                    motivo,
                    status,
                    erro,
                    data_execucao,
                ),
            )
            conexao.commit()
        finally:
            conexao.close()

    def listar_execucoes(self) -> list[dict]:
        conexao = sqlite3.connect(self.caminho_banco)

        try:
            conexao.row_factory = sqlite3.Row

            linhas = conexao.execute(
                "SELECT * FROM historico_execucao ORDER BY id DESC"
            ).fetchall()

            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()