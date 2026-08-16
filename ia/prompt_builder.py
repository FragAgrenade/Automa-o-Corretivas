def montar_prompt(tipo_os: str, historico: str, observacoes: str) -> str:
    return f"""Você é um analista de corretivas de ordem de serviço.

Analise somente os dados fornecidos. Não invente fatos nem complete lacunas.

Retorne abrir_corretiva como true APENAS se o histórico ou as observações
indicarem explicitamente que a OS foi invalidada. Nesse caso, motivo deve conter
somente o motivo textual da invalidação, de forma objetiva.

Se estiver validada, não houver evidência de invalidação ou houver ambiguidade,
retorne abrir_corretiva como false e motivo como uma string vazia.

TIPO DA OS:
{tipo_os}

HISTÓRICO:
{historico}

OBSERVAÇÕES:
{observacoes}
"""