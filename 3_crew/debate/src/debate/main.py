#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from debate.crew import Debate

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Este arquivo principal serve para que você execute sua
# equipe localmente, portanto evite adicionar lógica desnecessária nele.
# Substitua pelas entradas que deseja testar; as informações de tarefas e agentes
# serão interpoladas automaticamente

def run():
    """
    Execute a equipe.
    """
    inputs = {
        'motion': 'É necessário haver leis rigorosas para regular LLMs',
    }

    try:
        result = Debate().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"Ocorreu um erro ao executar a equipe: {e}")
