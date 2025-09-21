# Equipe StockPicker

Bem-vindo ao projeto StockPicker Crew, impulsionado por [crewAI](https://crewai.com). Este modelo foi criado para ajudar você a configurar um sistema de IA multiagente com facilidade, aproveitando o framework poderoso e flexível fornecido pela crewAI. Nosso objetivo é permitir que seus agentes colaborem de forma eficaz em tarefas complexas, maximizando a inteligência e as capacidades coletivas.

## Instalação

Garanta que você tenha Python >=3.10 <3.13 instalado em seu sistema. Este projeto usa [UV](https://docs.astral.sh/uv/) para gerenciamento de dependências e pacotes, oferecendo uma experiência de configuração e execução sem atritos.

Primeiro, se ainda não fez isso, instale o uv:

```bash
pip install uv
```

Em seguida, navegue até o diretório do projeto e instale as dependências:

(Opcional) Trave as dependências e instale-as usando o comando da CLI:
```bash
crewai install
```
### Personalização

**Adicione sua `OPENAI_API_KEY` no arquivo `.env`**

- Modifique `src/stock_picker/config/agents.yaml` para definir seus agentes
- Modifique `src/stock_picker/config/tasks.yaml` para definir suas tarefas
- Modifique `src/stock_picker/crew.py` para adicionar sua própria lógica, ferramentas e argumentos específicos
- Modifique `src/stock_picker/main.py` para adicionar entradas personalizadas para seus agentes e tarefas

## Executando o Projeto

Para iniciar sua equipe de agentes de IA e começar a execução das tarefas, execute isto a partir da pasta raiz do seu projeto:

```bash
$ crewai run
```

Este comando inicializa a equipe stock_picker, reunindo os agentes e atribuindo tarefas conforme definido em sua configuração.

Este exemplo, sem modificações, criará um arquivo `report.md` com o resultado de uma pesquisa sobre LLMs na pasta raiz.

## Entendendo Sua Equipe

A equipe stock_picker é composta por vários agentes de IA, cada um com papéis, objetivos e ferramentas únicos. Esses agentes colaboram em uma série de tarefas, definidas em `config/tasks.yaml`, aproveitando suas habilidades coletivas para atingir objetivos complexos. O arquivo `config/agents.yaml` descreve as capacidades e configurações de cada agente em sua equipe.

## Suporte

Para suporte, dúvidas ou feedback sobre a StockPicker Crew ou sobre a crewAI.
- Visite nossa [documentação](https://docs.crewai.com)
- Fale conosco por meio do nosso [repositório no GitHub](https://github.com/joaomdmoura/crewai)
- [Entre no nosso Discord](https://discord.com/invite/X4JWnZnxPb)
- [Converse com nossa documentação](https://chatg.pt/DWjSBZn)

Vamos criar maravilhas juntos com o poder e a simplicidade da crewAI.