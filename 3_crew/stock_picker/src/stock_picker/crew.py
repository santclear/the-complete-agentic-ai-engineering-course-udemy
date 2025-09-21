from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List
from .tools.push_tool import PushNotificationTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

class TrendingCompany(BaseModel):
    """ Empresa que aparece nas notícias e atrai atenção """
    name: str = Field(description="Nome da empresa")
    ticker: str = Field(description="Símbolo do ticker da ação")
    reason: str = Field(description="Motivo pelo qual essa empresa está em destaque nas notícias")

class TrendingCompanyList(BaseModel):
    """ Lista de várias empresas em destaque nas notícias """
    companies: List[TrendingCompany] = Field(description="Lista de empresas em destaque nas notícias")

class TrendingCompanyResearch(BaseModel):
    """ Pesquisa detalhada sobre uma empresa """
    name: str = Field(description="Nome da empresa")
    market_position: str = Field(description="Posição atual de mercado e análise competitiva")
    future_outlook: str = Field(description="Perspectiva futura e potencial de crescimento")
    investment_potential: str = Field(description="Potencial e adequação para investimento")

class TrendingCompanyResearchList(BaseModel):
    """ Lista de pesquisas detalhadas sobre todas as empresas """
    research_list: List[TrendingCompanyResearch] = Field(description="Pesquisa abrangente sobre todas as empresas em destaque")


@CrewBase
class StockPicker():
    """Equipe StockPicker"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(config=self.agents_config['trending_company_finder'],
                     tools=[SerperDevTool()], memory=True)
    
    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config=self.agents_config['financial_researcher'], 
                     tools=[SerperDevTool()])

    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config['stock_picker'], 
                     tools=[PushNotificationTool()], memory=True)
    
    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList,
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList,
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
        )
    



    @crew
    def crew(self) -> Crew:
        """Cria a equipe StockPicker"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )
            
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,
            # Memória de longo prazo para armazenamento persistente entre sessões
            long_term_memory = LongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path="./memory/long_term_memory_storage.db"
                )
            ),
            # Memória de curto prazo para o contexto atual usando RAG
            short_term_memory = ShortTermMemory(
                storage = RAGStorage(
                        embedder_config={
                            "provider": "openai",
                            "config": {
                                "model": 'text-embedding-3-small'
                            }
                        },
                        type="short_term",
                        path="./memory/"
                    )
                ),            # Memória de entidades para acompanhar informações chave sobre entidades
            entity_memory = EntityMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {
                            "model": 'text-embedding-3-small'
                        }
                    },
                    type="short_term",
                    path="./memory/"
                )
            ),
        )


