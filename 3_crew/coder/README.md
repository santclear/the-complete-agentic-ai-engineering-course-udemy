# Coder Crew

Bem-vindo ao projeto Coder Crew, desenvolvido com [crewAI](https://crewai.com). Este template foi criado para ajudar você a configurar com facilidade um sistema de IA multiagente, aproveitando a estrutura poderosa e flexível fornecida pela crewAI. Nosso objetivo é permitir que seus agentes colaborem de forma eficaz em tarefas complexas, maximizando sua inteligência coletiva e capacidades.

## Instalação

Garanta que você tenha Python >=3.10 <3.13 instalado em seu sistema. Este projeto usa [UV](https://docs.astral.sh/uv/) para gerenciamento de dependências e pacotes, oferecendo uma experiência de configuração e execução perfeita.

Primeiro, se ainda não o fez, instale o uv:

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

- Modifique `src/coder/config/agents.yaml` para definir seus agentes
- Modifique `src/coder/config/tasks.yaml` para definir suas tarefas
- Modifique `src/coder/crew.py` para adicionar sua própria lógica, ferramentas e argumentos específicos
- Modifique `src/coder/main.py` para adicionar entradas personalizadas para seus agentes e tarefas

## Executando o Projeto

Para iniciar sua equipe de agentes de IA e começar a execução das tarefas, rode isto a partir da pasta raiz do projeto:

```bash
$ crewai run
```

Esse comando inicializa a Coder Crew, reunindo os agentes e atribuindo-lhes tarefas conforme definido na configuração.

Esse exemplo, sem modificações, vai gerar o arquivo `report.md` com o resultado de uma pesquisa sobre LLMs na pasta raiz.

## Entendendo Sua Equipe

A Coder Crew é composta por vários agentes de IA, cada um com funções, objetivos e ferramentas exclusivas. Esses agentes colaboram em uma série de tarefas, definidas em `config/tasks.yaml`, aproveitando suas habilidades coletivas para alcançar objetivos complexos. O arquivo `config/agents.yaml` descreve as capacidades e configurações de cada agente da sua equipe.

## Suporte

Para suporte, dúvidas ou feedback sobre a Coder Crew ou a crewAI.
- Visite nossa [documentação](https://docs.crewai.com)
- Entre em contato por meio do nosso [repositório no GitHub](https://github.com/joaomdmoura/crewai)
- [Entre no nosso Discord](https://discord.com/invite/X4JWnZnxPb)
- [Converse com nossa documentação](https://chatg.pt/DWjSBZn)

Vamos criar maravilhas juntos com o poder e a simplicidade da crewAI.
