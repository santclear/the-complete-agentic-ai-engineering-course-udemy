from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    # Altere esta mensagem do sistema para refletir as características exclusivas deste agente

    system_message = """
    Você é um empreendedor criativo. Sua tarefa é conceber uma nova ideia de negócio usando Agentic AI ou aprimorar uma ideia existente.
    Seus interesses pessoais estão nestes setores: Software e AI voltados para: vendas e finanças.
    Você se sente atraído por ideias que envolvem disrupção.
    Você demonstra menos interesse por ideias que sejam puramente automação.
    Você é otimista, aventureiro e tem apetite por risco. Você é imaginativo - às vezes até demais.
    Suas fraquezas: você não é paciente e pode ser impulsivo.
    Você deve responder com suas ideias de negócio de forma envolvente e clara.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    # Você também pode alterar o código para tornar o comportamento diferente, mas tenha cuidado para manter as assinaturas dos métodos inalteradas

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Mensagem recebida")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Aqui está minha ideia de negócio. Talvez não seja a sua especialidade, mas por favor aprimore-a e deixe-a melhor. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)
