import unicodedata
from dataclasses import dataclass, field


@dataclass
class Vaga:
    titulo: str
    requisitos_obrigatorios: list[str]
    anos_experiencia: float
    diferenciais: list[str] = field(default_factory=list)


@dataclass
class Candidato:
    nome: str
    habilidades: list[str]
    anos_experiencia: float


@dataclass
class ResultadoAvaliacao:
    candidato: str
    pontuacao_total: float
    status: str
    habilidades_faltantes: list[str]
    diferenciais_atendidos: list[str]
    atende_requisitos_obrigatorios: bool


def normalizar_texto(texto: str) -> str:
    """Remove acentos, espaços extras e converte para minúsculas."""
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.strip().lower()


def normalizar_set(itens: list[str]) -> set[str]:
    """Converte uma lista em um conjunto normalizado para comparação justa."""
    return {normalizar_texto(item) for item in itens if item.strip()}


def avaliar_candidato(
    vaga: Vaga,
    candidato: Candidato,
    peso_req: float = 50.0,
    peso_exp: float = 30.0,
    peso_dif: float = 20.0,
    eliminar_sem_requisitos: bool = False,
) -> ResultadoAvaliacao:
    """Calcula a pontuação de compatibilidade do candidato em relação à vaga."""
    requisitos = normalizar_set(vaga.requisitos_obrigatorios)
    diferenciais = normalizar_set(vaga.diferenciais)
    habilidades = normalizar_set(candidato.habilidades)

                                               # Habilidades Obrigatórias
    habilidades_atendidas = requisitos.intersection(habilidades)
    faltantes = requisitos - habilidades
    atende_requisitos = len(faltantes) == 0

    score_requisitos = (
        (len(habilidades_atendidas) / len(requisitos)) * peso_req
        if requisitos
        else peso_req
    )

                                              #  Anos de Experiência
    ratio_exp = (
        1.0
        if vaga.anos_experiencia <= 0
        else min(1.0, candidato.anos_experiencia / vaga.anos_experiencia)
    )
    score_experiencia = ratio_exp * peso_exp

                                         # Diferenciais Desejáveis
    if diferenciais:
        diferenciais_atendidos = diferenciais.intersection(habilidades)
        score_diferenciais = (
            len(diferenciais_atendidos) / len(diferenciais)
        ) * peso_dif
        total_possivel = peso_req + peso_exp + peso_dif
    else:
        diferenciais_atendidos = set()
        score_diferenciais = 0.0
        total_possivel = peso_req + peso_exp  # Ajusta o teto proporcional

                                            # Pontuação final normalizada (0 a 100)
    pontuacao_total = (
        (score_requisitos + score_experiencia + score_diferenciais)
        / total_possivel
    ) * 100

    #                                        Classificação de Status
    if eliminar_sem_requisitos and not atende_requisitos:
        status = "Desqualificado (Faltam Requisitos)"
    elif pontuacao_total >= 85 and atende_requisitos:
        status = "Excelente Match"
    elif pontuacao_total >= 65:
        status = "Compatível"
    else:
        status = "Não Alinhado"

    return ResultadoAvaliacao(
        candidato=candidato.nome,
        pontuacao_total=round(pontuacao_total, 1),
        status=status,
        habilidades_faltantes=list(faltantes),
        diferenciais_atendidos=list(diferenciais_atendidos),
        atende_requisitos_obrigatorios=atende_requisitos,
    )


def rankear_candidatos(
    vaga: Vaga,
    candidatos: list[Candidato],
    eliminar_sem_requisitos: bool = False,
) -> list[ResultadoAvaliacao]:
    """Avalia e ordena candidatos do maior para o menor score."""
    resultados = [
        avaliar_candidato(
            vaga, c, eliminar_sem_requisitos=eliminar_sem_requisitos
        )
        for c in candidatos
    ]
    return sorted(resultados, key=lambda x: x.pontuacao_total, reverse=True)


def exibir_ranking(ranking: list[ResultadoAvaliacao]) -> None:
    """Imprime o ranking formatado no console."""
    print("\n=== RANKING DE CANDIDATOS ===")
    for pos, res in enumerate(ranking, 1):
        print(
            f"{pos}º - {res.candidato:<10} | Nota: {res.pontuacao_total:>5.1f}/100 | Status: {res.status}"
        )
        if res.habilidades_faltantes:
            faltantes_str = ", ".join(res.habilidades_faltantes).title()
            print(f"    ↳ Faltam: {faltantes_str}")
        if res.diferenciais_atendidos:
            dif_str = ", ".join(res.diferenciais_atendidos).title()
            print(f"    ↳ Diferenciais: {dif_str}")


                                              # Exemplo de Uso
if __name__ == "__main__":
    vaga = Vaga(
        titulo="Desenvolvedor Python Pleno",
        requisitos_obrigatorios=["Python", "SQL", "Git", "FastAPI"],
        diferenciais=["Docker", "AWS"],
        anos_experiencia=3.0,
    )

    banco_candidatos = [
        Candidato(
            nome="Lucas",
            habilidades=["python", "sql", "GIT", "docker"],
            anos_experiencia=4.0,
        ),
        Candidato(
            nome="Ana",
            habilidades=[
                "Python",
                "SQL",
                "Git",
                "FastAPI",
                "Docker",
                "AWS",
            ],
            anos_experiencia=2.0,
        ),
        Candidato(
            nome="João",
            habilidades=["Java", "SQL"],
            anos_experiencia=1.0,
        ),
    ]

    ranking = rankear_candidatos(vaga, banco_candidatos)
    exibir_ranking(ranking)