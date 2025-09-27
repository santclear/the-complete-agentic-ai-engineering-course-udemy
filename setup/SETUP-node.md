# Detalhes extras de configuração para NodeJS e Playwright

_No Cursor, clique com o botão direito neste arquivo no Explorer e selecione "Open Preview" para vê-lo com formatação, ou veja a versão online no Github._

Nas semanas 4 e 6, usaremos o NodeJS em seu computador.  

Usuários de PC, atenção: se estiver usando WSL (o que será necessário na Semana 6), nesse momento você precisará instalar o Node novamente no lado do Ubuntu.

## Instruções para instalar o Node

Verifique se você tem o Node instalado – deve ser a versão v22 ou posterior:  
`!node --version`

Aqui estão instruções super claras de instalação, cortesia do nosso amigo IA:

https://chatgpt.com/share/68103af2-e2dc-8012-b259-bc135a23273b

Na maioria dos casos, isso envolve simplesmente visitar https://nodejs.org e seguir as instruções. Usuários de PC no WSL, lembrem-se de seguir as instruções para Linux.

Quando terminar, verifique se funciona no notebook. Pode ser necessário sair e reiniciar o Cursor (também feche quaisquer terminais abertos no Cursor).  

`!node --version`  
`!npx --version`

## Instalando o Playwright

Playwright é o software de automação de navegador da Microsoft que usamos nas semanas 4 e 6.

No Mac / PC:  
`uv run playwright install`

No Linux / WSL:  
`uv run playwright install --with-deps chromium`

## Solução de problemas – se servidores MCP baseados em Node travarem no Windows / WSL

Para alguns usuários de WSL, rodar servidores MCP baseados em npx parece travar. Aqui está a correção!

Primeiro, saia e reinicie o Cursor para aplicar quaisquer mudanças desde que instalou o Node. Também feche todos os Terminais abertos no Cursor e abra um novo terminal.

No terminal, execute:  
`which node`

Isso deve fornecer o caminho do Node rodando no seu subsistema WSL. Suponha que seja algo como:  
`/home/user/.nvm/versions/node/v22.18.0/bin`

Então, execute este comando, substituindo cuidadosamente o caminho pelo seu:  
`!export PATH="/home/user/.nvm/versions/node/v22.18.0/bin:$PATH"`

E também este, novamente substituindo o caminho pelo seu:  
`os.environ["PATH"] = "/home/user/.nvm/versions/node/v22.18.0/bin:" + os.environ["PATH"]`

Depois, tente rodar novamente a célula anterior.  
E se ainda não funcionar, tente mudar os parâmetros do MCP para o caminho completo do npx:
```python
playwright_params = {"command": "/home/user/.nvm/versions/node/v22.18.0/bin/npx","args": [ "@playwright/mcp@latest"]}
```

E / ou esta abordagem:

```python
env = {"PATH": "/home/user/.nvm/versions/node/v22.18.0/bin:" + os.environ["PATH"]}
playwright_params = {"command": "npx","args": [ "@playwright/mcp@latest"], "env": env}
```

Se isso não funcionar, me avise! Um sincero agradecimento a Radoslav R. e André R. por batalharem com isso, encontrarem as soluções e compartilharem!