import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ia.prompt_builder import montar_prompt


class ErroOllama(RuntimeError):
    """Erro de comunicação ou de resposta inválida do Ollama."""


@dataclass(frozen=True)
class ResultadoAnalise:
    abrir_corretiva: bool
    motivo: str


SCHEMA_RESPOSTA = {
    "type": "object",
    "properties": {
        "abrir_corretiva": {"type": "boolean"},
        "motivo": {"type": "string"},
    },
    "required": ["abrir_corretiva", "motivo"],
    "additionalProperties": False,
}


class OllamaService:
    def __init__(
        self,
        modelo: str = "qwen3:8b",
        url_base: str = "http://localhost:11434",
        timeout: int = 90,
    ):
        self.modelo = modelo
        self.url_base = url_base.rstrip("/")
        self.timeout = timeout

    def analisar_os(
        self,
        tipo_os: str,
        historico: str,
        observacoes: str,
    ) -> ResultadoAnalise:
        payload = {
            "model": self.modelo,
            "prompt": montar_prompt(tipo_os, historico, observacoes),
            "format": SCHEMA_RESPOSTA,
            "stream": False,
            "options": {"temperature": 0},
        }

        requisicao = Request(
            f"{self.url_base}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(requisicao, timeout=self.timeout) as resposta:
                corpo = json.loads(resposta.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as erro:
            raise ErroOllama(
                f"Falha ao comunicar com o Ollama: {erro}"
            ) from erro

        if not isinstance(corpo, dict) or not isinstance(corpo.get("response"), str):
            raise ErroOllama(
                "A resposta da API do Ollama não possui o campo 'response'."
            )

        return self.interpretar_resposta(corpo["response"])

    @staticmethod
    def interpretar_resposta(resposta: str) -> ResultadoAnalise:
        try:
            dados = json.loads(resposta)
        except json.JSONDecodeError as erro:
            raise ErroOllama(
                "O Ollama não retornou um JSON válido."
            ) from erro

        campos_esperados = {"abrir_corretiva", "motivo"}

        if not isinstance(dados, dict) or set(dados) != campos_esperados:
            raise ErroOllama(
                "O JSON da IA possui campos inválidos ou ausentes."
            )

        if (
            type(dados["abrir_corretiva"]) is not bool
            or not isinstance(dados["motivo"], str)
        ):
            raise ErroOllama(
                "O JSON da IA possui tipos de dados inválidos."
            )

        motivo = dados["motivo"].strip()

        if not dados["abrir_corretiva"]:
            return ResultadoAnalise(
                abrir_corretiva=False,
                motivo="",
            )

        if not motivo:
            raise ErroOllama(
                "A IA pediu corretiva sem informar o motivo."
            )

        return ResultadoAnalise(
            abrir_corretiva=True,
            motivo=motivo,
        )