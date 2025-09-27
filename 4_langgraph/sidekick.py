from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List, Any, Optional, Dict
from pydantic import BaseModel, Field
from sidekick_tools import playwright_tools, other_tools
import uuid
import asyncio
from datetime import datetime

load_dotenv(override=True)


class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool


class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Feedback sobre a resposta do assistente")
    success_criteria_met: bool = Field(description="Se os critérios de sucesso foram atendidos")
    user_input_needed: bool = Field(
        description="Verdadeiro se forem necessárias mais informações do usuário, esclarecimentos ou se o assistente estiver travado"
    )


class Sidekick:
    def __init__(self):
        self.worker_llm_with_tools = None
        self.evaluator_llm_with_output = None
        self.tools = None
        self.llm_with_tools = None
        self.graph = None
        self.sidekick_id = str(uuid.uuid4())
        self.memory = MemorySaver()
        self.browser = None
        self.playwright = None

    async def setup(self):
        self.tools, self.browser, self.playwright = await playwright_tools()
        self.tools += await other_tools()
        worker_llm = ChatOpenAI(model="gpt-5-mini")
        self.worker_llm_with_tools = worker_llm.bind_tools(self.tools)
        evaluator_llm = ChatOpenAI(model="gpt-5-mini")
        self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
        await self.build_graph()

    def worker(self, state: State) -> Dict[str, Any]:
        system_message = f"""Você é um assistente prestativo que pode usar ferramentas para concluir tarefas.
    Você continua trabalhando em uma tarefa até que tenha uma pergunta ou esclarecimento para o usuário, ou até que os critérios de sucesso sejam atendidos.
    Você tem muitas ferramentas para ajudar, incluindo ferramentas para navegar na internet, navegar e recuperar páginas da web.
    Você tem uma ferramenta para executar código Python, mas observe que precisará incluir uma instrução print() se quiser receber saída.
    A data e hora atuais são {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    Estes são os critérios de sucesso:
    {state["success_criteria"]}
    Você deve responder com uma pergunta para o usuário sobre esta tarefa ou com sua resposta final.
    Se tiver uma pergunta para o usuário, responda declarando claramente sua pergunta. Um exemplo poderia ser:

    Pergunta: por favor esclareça se deseja um resumo ou uma resposta detalhada

    Se você terminou, responda com a resposta final e não faça uma pergunta; simplesmente responda com a resposta.
    """

        if state.get("feedback_on_work"):
            system_message += f"""
    Anteriormente você achou que tinha concluído a tarefa, mas sua resposta foi rejeitada porque os critérios de sucesso não foram atendidos.
    Aqui está o feedback sobre o motivo da rejeição:
    {state["feedback_on_work"]}
    Com esse feedback, continue a tarefa, garantindo que atenda aos critérios de sucesso ou tenha uma pergunta para o usuário."""

        # Adiciona a mensagem de sistema

        found_system_message = False
        messages = state["messages"]
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = system_message
                found_system_message = True

        if not found_system_message:
            messages = [SystemMessage(content=system_message)] + messages

        # Invoca o LLM com ferramentas
        response = self.worker_llm_with_tools.invoke(messages)

        # Retorna o estado atualizado
        return {
            "messages": [response],
        }

    def worker_router(self, state: State) -> str:
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "evaluator"

    def format_conversation(self, messages: List[Any]) -> str:
        conversation = "Histórico da conversa:\n\n"
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation += f"Usuário: {message.content}\n"
            elif isinstance(message, AIMessage):
                text = message.content or "[Uso de ferramentas]"
                conversation += f"Assistente: {text}\n"
        return conversation

    def evaluator(self, state: State) -> State:
        last_response = state["messages"][-1].content

        system_message = """Você é um avaliador que determina se uma tarefa foi concluída com sucesso por um Assistente.
    Avalie a última resposta do Assistente com base nos critérios fornecidos. Responda com seu feedback e sua decisão sobre se os critérios de sucesso foram atendidos,
    e se são necessárias mais informações do usuário."""

        user_message = f"""Você está avaliando uma conversa entre o Usuário e o Assistente. Você decide qual ação tomar com base na última resposta do Assistente.

    Toda a conversa com o assistente, com a solicitação original do usuário e todas as respostas, é:
    {self.format_conversation(state["messages"])}

    Os critérios de sucesso para esta tarefa são:
    {state["success_criteria"]}

    E a resposta final do Assistente que você está avaliando é:
    {last_response}

    Forneça seu feedback e decida se os critérios de sucesso são atendidos por esta resposta.
    Além disso, decida se são necessárias mais informações do usuário, seja porque o assistente tem uma pergunta, precisa de esclarecimento ou parece estar travado e incapaz de responder sem ajuda.

    O Assistente tem acesso a uma ferramenta para escrever arquivos. Se o Assistente disser que escreveu um arquivo, você pode assumir que isso foi feito.
    No geral, você deve dar ao Assistente o benefício da dúvida se ele disser que fez algo. Mas você deve rejeitar se sentir que mais trabalho deve ser feito.

    """
        if state["feedback_on_work"]:
            user_message += f"Além disso, observe que em uma tentativa anterior do Assistente, você forneceu este feedback: {state['feedback_on_work']}\n"
            user_message += "Se você perceber que o Assistente está repetindo os mesmos erros, considere responder que é necessário input do usuário."

        evaluator_messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message),
        ]

        eval_result = self.evaluator_llm_with_output.invoke(evaluator_messages)
        new_state = {
            "messages": [
                {
                    "role": "assistant",
                    "content": f"Feedback do avaliador para esta resposta: {eval_result.feedback}",
                }
            ],
            "feedback_on_work": eval_result.feedback,
            "success_criteria_met": eval_result.success_criteria_met,
            "user_input_needed": eval_result.user_input_needed,
        }
        return new_state

    def route_based_on_evaluation(self, state: State) -> str:
        if state["success_criteria_met"] or state["user_input_needed"]:
            return "END"
        else:
            return "worker"

    async def build_graph(self):
        # Configura o construtor do grafo com o estado
        graph_builder = StateGraph(State)

        # Adiciona nós
        graph_builder.add_node("worker", self.worker)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_node("evaluator", self.evaluator)

        # Adiciona arestas
        graph_builder.add_conditional_edges(
            "worker", self.worker_router, {"tools": "tools", "evaluator": "evaluator"}
        )
        graph_builder.add_edge("tools", "worker")
        graph_builder.add_conditional_edges(
            "evaluator", self.route_based_on_evaluation, {"worker": "worker", "END": END}
        )
        graph_builder.add_edge(START, "worker")

        # Compila o grafo
        self.graph = graph_builder.compile(checkpointer=self.memory)

    async def run_superstep(self, message, success_criteria, history):
        config = {"configurable": {"thread_id": self.sidekick_id}}

        state = {
            "messages": message,
            "success_criteria": success_criteria or "A resposta deve ser clara e precisa",
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False,
        }
        result = await self.graph.ainvoke(state, config=config)
        user = {"role": "user", "content": message}
        reply = {"role": "assistant", "content": result["messages"][-2].content}
        feedback = {"role": "assistant", "content": result["messages"][-1].content}
        return history + [user, reply, feedback]

    def cleanup(self):
        if self.browser:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.browser.close())
                if self.playwright:
                    loop.create_task(self.playwright.stop())
            except RuntimeError:
                # Se nenhum loop estiver em execução, executa diretamente
                asyncio.run(self.browser.close())
                if self.playwright:
                    asyncio.run(self.playwright.stop())
