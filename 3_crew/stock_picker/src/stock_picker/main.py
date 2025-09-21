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

from stock_picker.crew import StockPicker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Executa a equipe de pesquisa.
    """
    inputs = {
        'sector': 'Energia',
        "current_date": str(datetime.now())
    }

    # Crie e execute a equipe
    result = StockPicker().crew().kickoff(inputs=inputs)

    # Imprima o resultado
    print("\n\n=== DECISÃO FINAL ===\n\n")
    print(result.raw)


if __name__ == "__main__":
    run()



