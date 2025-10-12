## Master AI Agentic Engineering - construir agentes autônomos de IA

# Configurando o WSL - Subsistema do Windows para Linux

_NOTA 1: Estas instruções presumem que você já executou as instruções de Preparação do PC_

_NOTA 2: No Cursor, lembre-se de clicar com o botão direito neste arquivo no Explorer e escolher "Open Preview" para visualizar a formatação._

Bem-vindo de volta à terra das configurações, pessoal do PC!

Imagino que você esteja aqui porque chegou à Semana 6 e descobriu a notícia desagradável de que os servidores MCP funcionam no Windows apenas sob o WSL.

Sinto muito por fazê-lo passar por isso! A boa notícia é que vários alunos confirmaram que os servidores MCP funcionam no WSL. Além disso, o WSL é amplamente considerado uma excelente maneira de desenvolver no Windows. E outra boa notícia é que você já realizou a configuração uma vez, portanto, é de se esperar que desta vez tudo seja relativamente indolor. Vamos torcer.

### Parte 1: Instale o WSL, caso ainda não o tenha feito

O WSL é a forma recomendada pela Microsoft para executar Linux no seu PC com Windows, conforme descrito aqui:  
https://learn.microsoft.com/en-us/windows/wsl/install

Usaremos a distribuição padrão do Ubuntu, que parece funcionar muito bem. Vamos lá!

1. Abra um PowerShell.
2. Execute: `wsl --install`
3. Autorize permissões elevadas quando solicitado e aguarde a instalação do Ubuntu.
4. Em seguida, execute `wsl` para iniciá-lo e definir seu nome de usuário e senha do Linux.
5. Digite `pwd` e `ls` para ver em qual diretório você está e listar o conteúdo. Depois, digite `cd` para ir ao seu diretório pessoal e repita os comandos.

É importante compreender a diferença entre o seu diretório pessoal do Windows e este novo diretório pessoal no ambiente Linux do WSL.

### Parte 2: Instale o uv e o repositório

1. A partir do PowerShell, execute `ubuntu`. É importante usar `ubuntu`, e não `wsl`, porque isso o coloca diretamente no seu diretório pessoal do Linux.  
2. Siga as instruções para Linux em: https://docs.astral.sh/uv/getting-started/installation/ e execute `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Quando a instalação terminar, digite `exit` para sair do WSL e retornar ao PowerShell, depois digite `ubuntu` para voltar ao Linux, a fim de que as alterações na variável PATH sejam reconhecidas.
4. Agora digite `pwd` para verificar se você está em seu diretório pessoal do Linux. Em caso de dúvida, use `cd ~` e `ls` para conferir.
5. Crie um diretório de projetos com `mkdir projects` e, em seguida, `cd projects` para acessá-lo.
6. Dentro do novo diretório de projetos, clone o repositório com `git clone https://github.com/ed-donner/agents.git`
7. Entre no novo diretório `agents`, o seu diretório raiz do projeto, com `cd agents`
8. Execute o poderoso `uv sync`

Neste ponto, encontrei um erro desagradável de memória. Acredito que esteja relacionado à minha configuração, e você provavelmente não o enfrentará. Caso aconteça, avise-me - tenho uma correção!

### Parte 3: Configure o Cursor executando no seu ambiente de PC

1. Abra o Cursor, como de costume, no seu PC.
2. Abra o painel de Extensões (menu View >> Extensions ou Ctrl+Shift+X), pesquise por WSL, localize o WSL da Anysphere (os criadores do Cursor) e instale-o.
3. Pressione Ctrl+Shift+P, procure por Remote-WSL: New Window e selecione essa opção para abrir uma nova janela configurada para o WSL.
4. Escolha Open Project (então, aproveite para pegar um café), navegue até o novo diretório raiz do projeto "agents" no Linux e clique em Open ou Select Folder.
5. Abra novamente o painel de Extensões (Ctrl+Shift+X) e instale essas extensões no WSL, caso ainda não estejam instaladas: Python (ms-python) e Jupyter (microsoft), clicando no botão "Install in WSL-Ubuntu".

### E pronto para começar!

Você precisará criar um novo arquivo `.env` na pasta `agents` e copiar o seu `.env` do outro projeto. Além disso, será necessário clicar em "Select Kernel" e "Choose python environment...".

Aproveite o MCP!
