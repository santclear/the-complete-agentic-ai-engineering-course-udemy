#!/usr/bin/env python
# src/financial_researcher/main.py
import os
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

from financial_researcher.crew import ResearchCrew


# Cria o diretório de saída se não existir
os.makedirs('output', exist_ok=True)

def run():
    """
    Executa a equipe de pesquisa.
    """
    inputs = {
        'company': 'VALE'
    }

    # Cria e executa a equipe
    result = ResearchCrew().crew().kickoff(inputs=inputs)

    # Imprime o resultado
    print("\n\n=== RELATÓRIO FINAL ===\n\n")
    print(result.raw)

    print("\n\nRelatório foi salvo em output/report.md")

if __name__ == "__main__":
    run()
