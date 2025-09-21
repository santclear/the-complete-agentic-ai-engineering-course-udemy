from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class MyCustomToolInput(BaseModel):
    """Esquema de entrada para MyCustomTool."""
    argument: str = Field(..., description="Descrição do argumento.")

class MyCustomTool(BaseTool):
    name: str = "Nome da minha ferramenta"
    description: str = (
        "Descrição clara do para que esta ferramenta é útil; seu agente precisará dessa informação para usá-la."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # A implementação vai aqui
        return "este é um exemplo de saída de ferramenta, ignore e siga em frente."
