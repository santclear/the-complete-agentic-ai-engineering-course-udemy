# Equipe FinancialResearcher

Bem-vindo ao projeto da Equipe FinancialResearcher, desenvolvido com [crewAI](https://crewai.com). Este template foi criado para ajudar você a configurar, com facilidade, um sistema de IA multiagente, aproveitando o framework poderoso e flexível fornecido pelo crewAI. Nosso objetivo é permitir que seus agentes colaborem de forma eficaz em tarefas complexas, maximizando sua inteligência coletiva e capacidades.

## Instalação

Garanta que você tenha Python >=3.10 <3.13 instalado no seu sistema. Este projeto usa o [UV](https://docs.astral.sh/uv/) para gerenciamento de dependências e pacotes, oferecendo uma experiência de configuração e execução simples.

Primeiro, se ainda não o fez, instale o uv:

```bash
pip install uv
```

Em seguida, navegue até o diretório do seu projeto e instale as dependências:

(Opcional) Faça o lock das dependências e instale-as usando o comando da CLI:
```bash
crewai install
```
### Personalização

**Adicione sua `OPENAI_API_KEY` ao arquivo `.env`**

- Modifique `src/financial_researcher/config/agents.yaml` para definir seus agentes
- Modifique `src/financial_researcher/config/tasks.yaml` para definir suas tarefas
- Modifique `src/financial_researcher/crew.py` para adicionar sua própria lógica, ferramentas e argumentos específicos
- Modifique `src/financial_researcher/main.py` para adicionar entradas personalizadas para seus agentes e tarefas

## Executando o Projeto

Para iniciar sua equipe de agentes de IA e começar a execução das tarefas, execute a partir da pasta raiz do seu projeto:

```bash
$ crewai run
```

Este comando inicializa a equipe financial_researcher, reunindo os agentes e atribuindo tarefas conforme definido na sua configuração.

Este exemplo, sem modificações, criará um arquivo `report.md` com o resultado de uma pesquisa sobre LLMs na pasta raiz.

## Entendendo sua Equipe

A equipe financial_researcher é composta por vários agentes de IA, cada um com papéis, objetivos e ferramentas exclusivos. Esses agentes colaboram em uma série de tarefas, definidas em `config/tasks.yaml`, aproveitando suas habilidades coletivas para alcançar objetivos complexos. O arquivo `config/agents.yaml` descreve as capacidades e configurações de cada agente da sua equipe.

## Suporte

Para suporte, dúvidas ou feedback sobre a Equipe FinancialResearcher ou o crewAI:
- Visite nossa [documentação](https://docs.crewai.com)
- Fale conosco pelo nosso [repositório no GitHub](https://github.com/joaomdmoura/crewai)
- [Entre no nosso Discord](https://discord.com/invite/X4JWnZnxPb)
- [Converse com nossa documentação](https://chatg.pt/DWjSBZn)

Vamos criar maravilhas juntos com o poder e a simplicidade do crewAI.
