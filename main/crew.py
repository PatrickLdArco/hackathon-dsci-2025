import asyncio
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain.chat_models import ChatOpenAI
import pandas as pd
import dotenv
import datetime as dt

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
today = dt.datetime.now().strftime("%Y-%m-%d")

# Lê os dados e configura texto e feedback
pdf = ...

dados = pd.DataFrame({"texto": , "feedback": ["A introdução do capítulo está confusa. O texto contém alguns termos técnicos difíceis."]})
texto_original = dados["texto"].iloc[0]
tem_feedback = "feedback" in dados.columns and pd.notna(dados["feedback"].iloc[0])
feedback_texto = dados["feedback"].iloc[0] if tem_feedback else None

# Inicializa o modelo
custom_llm = ChatOpenAI(model="gpt-4.1-2025-04-14", temperature=0.2, openai_api_key=key)
# Inicialização do agente de busca
serperDevTool = SerperDevTool()

# ---------- Função para criar crews por fluxo ----------
def criar_fluxo(agentes_tarefas):
    return Crew(
        agents=agentes_tarefas["agentes"],
        tasks=agentes_tarefas["tarefas"],
        process=Process.sequential,
        llm=custom_llm
    )

def fluxo_outdated(texto):
    goal1 = """Identificar partes desatualizadas, incluindo definições ultrapassadas, dados geográficos como população que já tenham sido atualizadas, situações de conflitos atuais, entre outros. Tudo que potencialmente possa estar desatualizado. 
O output deve estar no formato:
trecho desatualizado 1: texto...
trecho desatualizado 2: texto...
"""
    goal2 = f"""Sugerir correções atualizadas. Tudo que incluir datas ou informações recentes deve ser considerada a data de hoje de {today}.
O output deve estar no formato:
"""
    agente1 = Agent(role="Identificador de Informações Desatualizadas", 
                    goal=goal1,
                    backstory="Especialista em detectar conteúdo obsoleto.", 
                    allow_delegation=False, 
                    llm=custom_llm)
    agente2 = Agent(role="Atualizador de Informações", 
                    goal=goal2, 
                    backstory="Atualiza conteúdo com dados recentes.", 
                    allow_delegation=False, 
                    llm=custom_llm,
                    tools=[serperDevTool])

    tarefa1 = Task(agent=agente1, description="Identifique trechos desatualizados.", expected_output="Lista de partes desatualizadas", context={"text": texto})
    tarefa2 = Task(agent=agente2, description="Sugira atualizações para os trechos.", expected_output="Correções propostas", context={"text": texto, "previous_output": tarefa1.expected_output})

    return {"agentes": [agente1, agente2], "tarefas": [tarefa1, tarefa2]}

def fluxo_estilo(texto):
    agente1 = Agent(role="Identificador de Problemas de Escrita", goal="Detectar problemas de clareza ou estilo", backstory="Especialista em estilo.", allow_delegation=False, llm=custom_llm)
    agente2 = Agent(role="Revisor de Estilo", goal="Sugerir melhorias de escrita", backstory="Aprimora clareza e tom.", allow_delegation=False, llm=custom_llm)

    tarefa1 = Task(agent=agente1, description="Identifique problemas de escrita.", expected_output="Lista de problemas de estilo", context={"text": texto})
    tarefa2 = Task(agent=agente2, description="Sugira melhorias para os trechos.", expected_output="Reescrita sugerida", context={"text": texto, "previous_output": tarefa1.expected_output})

    return {"agentes": [agente1, agente2], "tarefas": [tarefa1, tarefa2]}

def fluxo_feedback(texto, feedback):
    agente1 = Agent(role="Analisador de Feedback", goal="Interpretar feedback", backstory="Especialista em comentários de leitores.", allow_delegation=False, llm=custom_llm)
    agente2 = Agent(role="Corretor baseado em Feedback", goal="Aplicar correções com base no feedback", backstory="Aplica feedbacks diretamente.", allow_delegation=False, llm=custom_llm)

    tarefa1 = Task(agent=agente1, description=f"Analise o feedback: '{feedback}'", expected_output="Problemas apontados", context={"text": texto})
    tarefa2 = Task(agent=agente2, description="Sugira correções com base no feedback.", expected_output="Melhorias sugeridas", context={"text": texto, "previous_output": tarefa1.expected_output})

    return {"agentes": [agente1, agente2], "tarefas": [tarefa1, tarefa2]}

# ---------- Função assíncrona principal ----------
async def executar_pipeline(texto, feedback=None):
    # Cria os sub-crews
    crews = [
        criar_fluxo(fluxo_outdated(texto)),
        criar_fluxo(fluxo_estilo(texto))
    ]
    if feedback:
        crews.append(criar_fluxo(fluxo_feedback(texto, feedback)))

    # Executa os sub-crews em paralelo
    resultados = await asyncio.gather(*[crew.kickoff_async() for crew in crews])

    # Agregador
    agente_agregador = Agent(
        role="Agregador de Sugestões",
        goal="Unificar sugestões sem redundância",
        backstory="Faz a síntese de múltiplas sugestões.",
        allow_delegation=False,
        llm=custom_llm
    )
    tarefa_agregacao = Task(
        agent=agente_agregador,
        description="Agregue todas as sugestões dos fluxos anteriores.",
        expected_output="Sugestões finais unificadas",
        context={"sugestoes": "\n\n".join(resultados)}
    )

    # Editor final
    agente_editor = Agent(
        role="Editor Final",
        goal="Aplicar as sugestões ao texto original",
        backstory="Cria a versão final editada.",
        allow_delegation=False,
        llm=custom_llm
    )
    tarefa_edicao = Task(
        agent=agente_editor,
        description="Aplique as sugestões ao texto original.",
        expected_output="Texto final revisado",
        context={"text": texto, "sugestoes": "\n\n".join(resultados)}
    )

    # Cria crew final sequencial
    crew_final = Crew(
        agents=[agente_agregador, agente_editor],
        tasks=[tarefa_agregacao, tarefa_edicao],
        process=Process.sequential,
        llm=custom_llm
    )

    resultado_final = crew_final.kickoff()
    return resultado_final

# ---------- Rodar o pipeline ----------
resultado = asyncio.run(executar_pipeline(texto_original, feedback_texto if tem_feedback else None))
print(resultado)
