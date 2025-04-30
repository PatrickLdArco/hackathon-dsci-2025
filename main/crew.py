import asyncio
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain.chat_models import ChatOpenAI
import pandas as pd
from dotenv import load_dotenv
import datetime as dt
from crewai_tools import SerperDevTool
import markdown
import csv
import os
from tqdm.asyncio import tqdm_asyncio

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
today = dt.datetime.now().strftime("%Y-%m-%d")

# Lê os dados e configura texto e feedback
with open(
    "data/processed/SPE_NV_2025_EM_01_V2_FORGB_BIO_AL_IMP_CROPPED.md",
    "r",
    encoding="utf-8",
) as file:
    cap = markdown.markdown(file.read())
with open("data/feedbacks/ajustes.txt", "r", encoding="utf-8") as file:
    protocolo = file.read()
with open("data/feedbacks/feedback.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    feedback_lines = [
        f"feedback{i + 1}: {line[0]}" for i, line in enumerate(reader) if line
    ]
    feedback = "\n".join(feedback_lines)


# Inicializa o modelo
custom_llm = ChatOpenAI(model="gpt-4.1-2025-04-14", temperature=0.2, openai_api_key=key)
# Inicialização do agente de busca
serperDevTool = SerperDevTool()


# ---------- Função para criar crews por fluxo ----------
def criar_fluxo(agentes_tarefas):
    print("Started flow")
    return Crew(
        agents=agentes_tarefas["agentes"],
        tasks=agentes_tarefas["tarefas"],
        process=Process.sequential,
        llm=custom_llm,
    )


def fluxo_outdated(texto):
    goal1 = """Identificar partes desatualizadas, incluindo definições ultrapassadas, dados geográficos como população que já tenham sido atualizadas, situações de conflitos atuais, entre outros. Tudo que potencialmente possa estar desatualizado. 
O output deve estar no formato:
trecho desatualizado: texto...

trecho desatualizado: texto...
...
"""
    goal2 = f"""Sugerir correções atualizadas. Tudo que incluir datas ou informações recentes deve ser considerada a data de hoje de {today}.
Não fazer alterações além das apontadas, manter os trechos , não alterar o sentido do texto, não adicionar informações que não estão no texto original.
O output deve estar no formato:
"""
    agente1 = Agent(
        role="Identificador de Informações Desatualizadas",
        goal=goal1,
        backstory="Especialista em detectar conteúdo obsoleto.",
        allow_delegation=False,
        llm=custom_llm,
    )
    agente2 = Agent(
        role="Atualizador de Informações",
        goal=goal2,
        backstory="Atualiza conteúdo com dados recentes.",
        allow_delegation=False,
        llm=custom_llm,
        tools=[serperDevTool],
    )

    tarefa1 = Task(
        agent=agente1,
        description="Identifique trechos desatualizados.",
        expected_output="Lista de partes desatualizadas",
        context={"text": texto},
    )
    tarefa2 = Task(
        agent=agente2,
        description="Sugira atualizações para os trechos.",
        expected_output="Correções propostas",
        context={"text": texto, "previous_output": tarefa1.expected_output},
    )

    print("tarefas de atualização concluídas")

    return {"agentes": [agente1, agente2], "tarefas": [tarefa1, tarefa2]}


def fluxo_estilo(texto):
    goal1 = """Identificar partes que não estão de acordo com a diretriz da marca. O protocolo contém informações de tom, estilo e didática de escrita que devem ser seguidas. Identificar as partes que não estão de acordo, incluindo apenas casos claros de violação da marca, sem exagerar nas mudanças de baixo impacto.
O output deve estar no formato:
trecho não adequado: texto...
justificativa: texto...

trecho não adequado: texto...
justificativa: texto...
...
"""
    goal2 = f"""A partir das partes identificadas, sugerir melhorias de escrita. O texto deve ser reescrito de acordo com as diretrizes de estilo e didática informadas no protocolo.
Não fazer alterações além das apontadas, não alterar o sentido do texto, não adicionar informações que não estão no texto original.
O output deve estar no formato:
trecho: texto...
trecho sugerido: texto...


trecho: texto...
trecho sugerido: texto...
...
"""
    agente1 = Agent(
        role="Identificador de Problemas de Escrita",
        goal=goal1,
        backstory="Especialista em estilo de escrita e didática.",
        allow_delegation=False,
        llm=custom_llm,
    )
    agente2 = Agent(
        role="Revisor de Estilo",
        goal=goal2,
        backstory="Identifica trechos que não se enquadram na didática e diretrizes de escrita.",
        allow_delegation=False,
        llm=custom_llm,
    )

    tarefa1 = Task(
        agent=agente1,
        description="Identifique problemas de escrita.",
        expected_output="Lista de problemas de estilo",
        context={"text": texto, "protocolo": protocolo},
    )
    tarefa2 = Task(
        agent=agente2,
        description="Sugira melhorias para os trechos.",
        expected_output="Reescrita sugerida",
        context={
            "text": texto,
            "protocolo": protocolo,
            "previous_output": tarefa1.expected_output,
        },
    )

    print("tarefas de protocolo concluídas")

    return {"agentes": [agente1, agente2], "tarefas": [tarefa1, tarefa2]}


def fluxo_feedback(texto):
    goal1 = """Identificar partes que o feedback cita que estão ruins. Identificar as partes que não estão de acordo, incluindo apenas casos claros que o feedback direciona, sem exagerar nas mudanças de baixo impacto.
O output deve estar no formato:
trecho não adequado: texto...
justificativa: texto...

trecho não adequado: texto...
justificativa: texto...
...
"""
    goal2 = f"""A partir das partes identificadas, sugerir melhorias de escrita. O texto deve ser reescrito de acordo com o feedback providenciado.
Não fazer alterações além das apontadas, não alterar o sentido do texto, não adicionar informações que não estão no texto original.
O output deve estar no formato:
trecho: texto...
trecho sugerido: texto...


trecho: texto...
trecho sugerido: texto...
...
"""
    agente1 = Agent(
        role="Analisador de Feedback",
        goal=goal1,
        backstory="Especialista em comentários de leitores.",
        allow_delegation=False,
        llm=custom_llm,
    )
    agente2 = Agent(
        role="Corretor baseado em Feedback",
        goal=goal2,
        backstory="Aplica feedbacks diretamente.",
        allow_delegation=False,
        llm=custom_llm,
    )

    tarefa1 = Task(
        agent=agente1,
        description=f"Analise o feedback: '{feedback}'",
        expected_output="Problemas apontados",
        context={"text": texto, "feedback": feedback},
    )
    tarefa2 = Task(
        agent=agente2,
        description="Sugira correções com base no feedback.",
        expected_output="Melhorias sugeridas",
        context={
            "text": texto,
            "feedback": feedback,
            "previous_output": tarefa1.expected_output,
        },
    )

    print("tarefas de feedback concluídas")

    return {"agentes": [agente1, agente2], "tarefas": [tarefa1, tarefa2]}


# ---------- Função assíncrona principal ----------
async def executar_pipeline(texto):
    # Cria os sub-crews
    crews = [criar_fluxo(fluxo_outdated(texto)), criar_fluxo(fluxo_estilo(texto))]
    if feedback:
        crews.append(criar_fluxo(fluxo_feedback(texto)))

    # Executa os sub-crews em paralelo
    resultados = await tqdm_asyncio.gather(*[crew.kickoff_async() for crew in crews])

    # Agregador
    agente_agregador = Agent(
        role="Agregador de Sugestões",
        goal="Unificar sugestões sem redundância. Sugestões para um mesmo trecho devem ser unificadas.",
        backstory="Faz a síntese de múltiplas sugestões.",
        allow_delegation=False,
        llm=custom_llm,
    )
    tarefa_agregacao = Task(
        agent=agente_agregador,
        description="Agregue todas as sugestões dos fluxos anteriores.",
        expected_output="Sugestões finais unificadas",
        context={"sugestoes": "\n\n".join(resultados)},
    )

    # Editor final
    agente_editor = Agent(
        role="Editor Final",
        goal="Aplicar as sugestões ao texto original",
        backstory="Cria a versão final editada.",
        allow_delegation=False,
        llm=custom_llm,
    )
    tarefa_edicao = Task(
        agent=agente_editor,
        description="Aplique as sugestões ao texto original.",
        expected_output="Texto final revisado",
        context={"text": texto, "sugestoes": tarefa_agregacao.expected_output},
    )

    # Cria crew final sequencial
    crew_final = Crew(
        agents=[agente_agregador, agente_editor],
        tasks=[tarefa_agregacao, tarefa_edicao],
        process=Process.sequential,
        llm=custom_llm,
    )

    resultado_final = crew_final.kickoff()
    return resultado_final


# ---------- Rodar o pipeline ----------
resultado = asyncio.run(executar_pipeline(cap))
print(resultado)
