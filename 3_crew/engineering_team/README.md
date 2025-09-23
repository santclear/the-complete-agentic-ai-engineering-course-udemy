# Equipe EngineeringTeam

Bem-vindo ao projeto Equipe EngineeringTeam, desenvolvido com a [crewAI](https://crewai.com). Este template foi criado para ajudar você a configurar um sistema de IA multiagente com facilidade, aproveitando o framework poderoso e flexível fornecido pela crewAI. Nosso objetivo é permitir que seus agentes colaborem de forma eficaz em tarefas complexas, maximizando a inteligência e as capacidades coletivas.

## Instalação

Garanta que você tenha Python >=3.10 <3.13 instalado no sistema. Este projeto usa o [UV](https://docs.astral.sh/uv/) para gerenciamento de dependências e pacotes, oferecendo uma experiência de configuração e execução simples.

Primeiro, caso ainda não tenha feito isso, instale o uv:

```bash
pip install uv
```

Em seguida, navegue até o diretório do projeto e instale as dependências:

(Opcional) Faça o lock das dependências e instale-as usando o comando da CLI:
```bash
crewai install
```
### Personalização

**Adicione sua `OPENAI_API_KEY` ao arquivo `.env`**

- Modifique `src/engineering_team/config/agents.yaml` para definir seus agentes
- Modifique `src/engineering_team/config/tasks.yaml` para definir suas tarefas
- Modifique `src/engineering_team/crew.py` para adicionar sua própria lógica, ferramentas e argumentos específicos
- Modifique `src/engineering_team/main.py` para adicionar entradas personalizadas para seus agentes e tarefas

## Executando o Projeto

Para iniciar sua equipe de agentes de IA e começar a execução das tarefas, execute o seguinte a partir da pasta raiz do projeto:

```bash
$ crewai run
```

Esse comando inicializa a Crew engineering_team, reunindo os agentes e atribuindo as tarefas conforme definido na configuração.

Este exemplo, sem modificações, criará um arquivo `report.md` com o resultado de uma pesquisa sobre LLMs na pasta raiz.

## Entendendo Sua Equipe

A Crew engineering_team é composta por vários agentes de IA, cada um com papéis, objetivos e ferramentas exclusivos. Esses agentes colaboram em uma série de tarefas, definidas em `config/tasks.yaml`, aproveitando habilidades coletivas para alcançar objetivos complexos. O arquivo `config/agents.yaml` descreve as capacidades e configurações de cada agente da equipe.

## Suporte

Para suporte, dúvidas ou feedback sobre a Crew EngineeringTeam ou a crewAI:
- Visite nossa [documentação](https://docs.crewai.com)
- Entre em contato por meio do [nosso repositório no GitHub](https://github.com/joaomdmoura/crewai)
- [Junte-se ao nosso Discord](https://discord.com/invite/X4JWnZnxPb)
- [Converse com nossa documentação](https://chatg.pt/DWjSBZn)

Vamos criar maravilhas juntos com o poder e a simplicidade da crewAI.
