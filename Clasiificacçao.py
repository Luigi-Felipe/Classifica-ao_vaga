from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Vaga:
    titulo: str
    requisitos_obrigatorios: List[str]
    anos_experiencia: float
    diferenciais: List[str] = field(default_factory=list)

@dataclass
class Candidato:
    nome: str
    habilidades: List[str]
    anos_experiencia: float

def normalizar_set(itens: List[str]) -> set[str]:
    """Remove espaços extras e converte para minúsculas para comparação justa."""
    return {item.strip().lower() for item in itens if item.strip()}

def avaliar_candidato(
    vaga: Vaga, 
    candidato: Candidato, 
    peso_req: float = 50.0, 
    peso_exp: float = 30.0, 
    peso_dif: float = 20.0
) -> Dict[str, Any]:
    
                                    # Normalização de dados
    requisitos = normalizar_set(vaga.requisitos_obrigatorios)
    diferenciais = normalizar_set(vaga.diferenciais)
    habilidades = normalizar_set(candidato.habilidades)

                      # 1. Habilidades Obrigatórias
    habilidades_atendidas = requisitos.intersection(habilidades)
    score_requisitos = (len(habilidades_atendidas) / len(requisitos)) * peso_req if requisitos else peso_req

                            # 2. Anos de Experiência (com teto relativo de 100%)
    if vaga.anos_experiencia > 0:
        ratio_exp = min(1.0, candidato.anos_experiencia / vaga.anos_experiencia)
    else:
        ratio_exp = 1.0
    score_experiencia = ratio_exp * peso_exp

                       # 3. Diferenciais Desejáveis
    if diferenciais:
        diferenciais_atendidos = diferenciais.intersection(habilidades)
        score_diferenciais = (len(diferenciais_atendidos) / len(diferenciais)) * peso_dif
        total_possivel = peso_req + peso_exp + peso_dif
    else:
        diferenciais_atendidos = set()
        score_diferenciais = 0.0
        total_possivel = peso_req + peso_exp  # Ajusta o teto para 100% proporcional

                     # Normalização da Nota Final (0 a 100)
    pontuacao_total = ((score_requisitos + score_experiencia + score_diferenciais) / total_possivel) * 100

                             # Categorização
    if pontuacao_total >= 85:
        status = "Excelente Match"
    elif pontuacao_total >= 65:
        status = "Compatível"
    else:
        status = "Não Alinhado"

    return {
        "candidato": candidato.nome,
        "pontuacao_total": round(pontuacao_total, 1),
        "status": status,
        "habilidades_faltantes": list(requisitos - habilidades),
        "diferenciais_atendidos": list(diferenciais_atendidos)
    }

def rankear_candidatos(vaga: Vaga, candidatos: List[Candidato]) -> List[Dict[str, Any]]:
    """Avalia e ordena uma lista de candidatos do maior para o menor score."""
    resultados = [avaliar_candidato(vaga, c) for c in candidatos]
    return sorted(resultados, key=lambda x: x["pontuacao_total"], reverse=True)


                        #EXEMPLO 

vaga = Vaga(
    titulo="Desenvolvedor Python Pleno",
    requisitos_obrigatorios=["Python", "SQL", "Git", "FastAPI"],
    diferenciais=["Docker", "AWS"],
    anos_experiencia=3.0
)

banco_candidatos = [
    Candidato(nome="Lucas", habilidades=["python", "sql", "GIT", "docker"], anos_experiencia=4.0),
    Candidato(nome="Ana", habilidades=["Python", "SQL", "Git", "FastAPI", "Docker", "AWS"], anos_experiencia=2.0),
    Candidato(nome="João", habilidades=["Java", "SQL"], anos_experiencia=1.0)
]

                        # Processamento e Impressão em Ranking
ranking = rankear_candidatos(vaga, banco_candidatos)

for pos, c in enumerate(ranking, 1):
    print(f"{pos}º - {c['candidato']} | Nota: {c['pontuacao_total']}/100 | Status: {c['status']}")
    if c['habilidades_faltantes']:
        print(f"   ↳ Faltam: {', '.join(c['habilidades_faltantes'])}")