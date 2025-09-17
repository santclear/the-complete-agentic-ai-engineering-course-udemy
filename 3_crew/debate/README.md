# Debate Crew

Bem-vindo ao projeto Debate Crew, desenvolvido com a tecnologia [crewAI](https://crewai.com). Este template foi criado para ajudá-lo a configurar com facilidade um sistema de IA multiagente, aproveitando a estrutura poderosa e flexível fornecida pela crewAI. Nosso objetivo é permitir que seus agentes colaborem de forma eficaz em tarefas complexas, maximizando sua inteligência e capacidades coletivas.

## Instalação

Certifique-se de ter o Python >=3.10 <3.13 instalado em seu sistema. Este projeto usa o [UV](https://docs.astral.sh/uv/) para gerenciamento de dependências e pacotes, oferecendo uma experiência de configuração e execução simplificada.

Primeiro, se ainda não o fez, instale o uv:

```bash
pip install uv
```

Em seguida, navegue até o diretório do projeto e instale as dependências:

(Opcional) Trave as dependências e instale-as usando o comando de CLI:
```bash
crewai install
```
### Personalização

**Adicione sua `OPENAI_API_KEY` ao arquivo `.env`**

- Modifique `src/debate/config/agents.yaml` para definir seus agentes
- Modifique `src/debate/config/tasks.yaml` para definir suas tarefas
- Modifique `src/debate/crew.py` para adicionar sua própria lógica, ferramentas e argumentos específicos
- Modifique `src/debate/main.py` para adicionar entradas personalizadas para seus agentes e tarefas

## Executando o Projeto

Para iniciar sua equipe de agentes de IA e começar a execução das tarefas, execute o seguinte a partir da pasta raiz do seu projeto:

```bash
$ crewai run
```

Esse comando inicializa a equipe de debate, reunindo os agentes e atribuindo-lhes tarefas conforme definido na sua configuração.

Este exemplo, sem modificações, criará um arquivo `report.md` com o resultado de uma pesquisa sobre LLMs na pasta raiz.

## Entendendo Sua Equipe

A equipe de debate é composta por vários agentes de IA, cada um com papéis, objetivos e ferramentas únicos. Esses agentes colaboram em uma série de tarefas, definidas em `config/tasks.yaml`, aproveitando suas habilidades coletivas para alcançar objetivos complexos. O arquivo `config/agents.yaml` descreve as capacidades e configurações de cada agente da sua equipe.

## Suporte

Para suporte, dúvidas ou feedback sobre o Debate Crew ou a crewAI:
- Visite nossa [documentação](https://docs.crewai.com)
- Entre em contato conosco por meio do nosso [repositório no GitHub](https://github.com/joaomdmoura/crewai)
- [Entre no nosso Discord](https://discord.com/invite/X4JWnZnxPb)
- [Converse com nossa documentação](https://chatg.pt/DWjSBZn)

Vamos criar maravilhas juntos com o poder e a simplicidade da crewAI.
