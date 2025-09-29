from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
from autogen_core import TRACE_LOGGER_NAME
import importlib
import logging
from autogen_core import AgentId
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(TRACE_LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Creator(RoutedAgent):

    # Altere esta mensagem do sistema para refletir as características exclusivas deste agente

    system_message = """
    Você é um agente capaz de criar novos agentes de IA.
    Você recebe um modelo em forma de código Python que cria um agente usando o Autogen Core e o Autogen Agentchat.
    Use esse modelo para criar um novo agente com uma mensagem de sistema própria, distinta do template,
    que reflita as características, os interesses e os objetivos específicos dele.
    Você pode manter o objetivo geral igual ou modificá-lo.
    Você pode levar esse agente em uma direção completamente diferente. O único requisito é que a classe se chame Agent,
    herde de RoutedAgent e possua um método __init__ que receba um parâmetro name.
    Evite interesses ligados ao meio ambiente; diversifique os setores de atuação para que cada agente seja diferente.
    Responda apenas com o código Python, sem texto adicional e sem blocos de markdown.
    """


    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    def get_user_prompt(self):
        prompt = "Por favor, gere um novo agente seguindo rigorosamente este modelo. Preserve a estrutura da classe. \
            Responda apenas com o código Python, sem texto adicional e sem blocos de markdown.\n\n\
            Seja criativo ao levar o agente para uma nova direção, mas não altere as assinaturas dos métodos.\n\n\
            Aqui está o modelo:\n\n"
        with open("agent.py", "r", encoding="utf-8") as f:
            template = f.read()
        return prompt + template   
        

    @message_handler
    async def handle_my_message_type(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        filename = message.content
        agent_name = filename.split(".")[0]
        text_message = TextMessage(content=self.get_user_prompt(), source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.chat_message.content)
        print(f"** O Creator gerou código Python para o agente {agent_name} - prestes a registrá-lo no Runtime")
        module = importlib.import_module(agent_name)
        await module.Agent.register(self.runtime, agent_name, lambda: module.Agent(agent_name))
        logger.info(f"** O agente {agent_name} está ativo")
        result = await self.send_message(messages.Message(content="Me dê uma ideia"), AgentId(agent_name, "default"))
        return messages.Message(content=result.content)
