import re
import unicodedata
from dataclasses import dataclass


class TipoOSNaoMapeadoError(ValueError):
    """O tipo da OS não possui uma corretiva configurada."""


MAPEAMENTO_TIPOS = {
    "INSTALACAO": "Corretiva Instalação",
    "VISITA_TECNICA": "Corretiva Visita Técnica",
    "MUDANCA_DE_ENDERECO": "Corretiva Mudança de Endereço",
    "TROCA_DE_TECNOLOGIA": "Corretiva Troca de Tecnologia",
}


def normalizar_tipo_os(tipo_os: str) -> str:
    texto = unicodedata.normalize("NFD", tipo_os.strip().upper())

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    return re.sub(r"[^A-Z0-9]+", "_", texto).strip("_")


@dataclass(frozen=True)
class DadosCorretiva:
    classificacao_categoria_1: str
    classificacao_categoria_2: str
    catalogo: str
    tipo: str
    motivo_retrabalho: str
    relato: str


class CorretivaService:
    def obter_tipo_corretiva(self, tipo_os: str) -> str:
        tipo_normalizado = normalizar_tipo_os(tipo_os)

        try:
            return MAPEAMENTO_TIPOS[tipo_normalizado]
        except KeyError as erro:
            raise TipoOSNaoMapeadoError(
                f"Não existe mapeamento para o tipo de OS: {tipo_os!r}."
            ) from erro

    def montar_dados(
        self,
        numero_os: str,
        tipo_os: str,
        motivo: str,
    ) -> DadosCorretiva:
        numero_os = numero_os.strip()
        motivo = motivo.strip()

        if not numero_os:
            raise ValueError("O número da OS é obrigatório.")

        if not motivo:
            raise ValueError("O motivo do retrabalho é obrigatório.")

        return DadosCorretiva(
            classificacao_categoria_1="Auditoria",
            classificacao_categoria_2="Ordem de Serviço",
            catalogo="VTAL - Corretiva",
            tipo=self.obter_tipo_corretiva(tipo_os),
            motivo_retrabalho=motivo,
            relato=f"Corretiva referente à OS {numero_os}.",
        )