#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime
from crewai.llm import LLM

def _model_base_name(model_id: str) -> str:
    return model_id.split("/", 1)[-1].lower()

_UNSUPPORTED_STOP_PREFIXES = (
    "gpt-4.1",      # gpt-4.1, gpt-4.1-mini, etc.
    "gpt-5",        # gpt-5, gpt-5-mini
    "o1", "o3",     # reasoning models também não aceitam stop
)

if not getattr(LLM, "_stop_patch_ready", False):
    _orig_supports_stop = LLM.supports_stop_words
    _orig_prepare = LLM._prepare_completion_params

    def _supports_stop_words(self) -> bool:
        model_name = _model_base_name(self.model)
        if model_name.startswith(_UNSUPPORTED_STOP_PREFIXES):
            return False
        return _orig_supports_stop(self)

    def _prepare_completion_params(self, messages, tools=None):
        params = _orig_prepare(self, messages, tools)
        if not self.supports_stop_words() or params.get("stop") in (None, [], ()):
            params.pop("stop", None)
        return params

    LLM.supports_stop_words = _supports_stop_words
    LLM._prepare_completion_params = _prepare_completion_params
    LLM._stop_patch_ready = True

from engineering_team.crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Cria o diretório de saída caso não exista
os.makedirs('output', exist_ok=True)

requirements = """
Um sistema simples de gerenciamento de contas para uma plataforma de simulação de negociações.
O sistema deve permitir que os usuários criem uma conta, depositem fundos e retirem fundos.
O sistema deve permitir que os usuários registrem que compraram ou venderam ações, informando uma quantidade.
O sistema deve calcular o valor total do portfólio do usuário e o lucro ou prejuízo em relação ao depósito inicial.
O sistema deve ser capaz de relatar as participações do usuário em qualquer momento.
O sistema deve ser capaz de relatar o lucro ou prejuízo do usuário em qualquer momento.
O sistema deve ser capaz de listar as transações que o usuário realizou ao longo do tempo.
O sistema deve impedir que o usuário retire fundos que o deixariam com saldo negativo, ou
 que compre mais ações do que pode pagar, ou venda ações que não possui.
 O sistema tem acesso à função get_share_price(symbol), que retorna o preço atual de uma ação e inclui uma implementação de teste que devolve preços fixos para AAPL, TSLA, GOOGL.
"""
module_name = "accounts.py"
class_name = "Account"


def run():
    """
    Executa a equipe de pesquisa.
    """
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }

    # Cria e executa a equipe
    result = EngineeringTeam().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()
