import gradio as gr
from accounts import Account, get_share_price

# Inicializa uma única conta
account = None

def create_account(user_id, initial_deposit):
    global account
    if not user_id:
        return "Erro: ID de usuário é obrigatório.", None

    try:
        initial_deposit = float(initial_deposit)
    except ValueError:
        return "Erro: O depósito inicial deve ser um número.", None

    if initial_deposit <= 0:
        return "Erro: O depósito inicial deve ser positivo.", None

    account = Account(user_id, initial_deposit)
    return f"Conta criada para {user_id} com depósito inicial de ${initial_deposit:.2f}", get_account_info()

def deposit(amount):
    if account is None:
        return "Erro: Nenhuma conta existe. Crie uma conta primeiro.", None

    try:
        amount = float(amount)
    except ValueError:
        return "Erro: O valor deve ser um número.", None

    if amount <= 0:
        return "Erro: O valor do depósito deve ser positivo.", None

    account.deposit_funds(amount)
    return f"Depósito de ${amount:.2f} realizado com sucesso", get_account_info()

def withdraw(amount):
    if account is None:
        return "Erro: Nenhuma conta existe. Crie uma conta primeiro.", None

    try:
        amount = float(amount)
    except ValueError:
        return "Erro: O valor deve ser um número.", None

    if amount <= 0:
        return "Erro: O valor do saque deve ser positivo.", None

    if account.withdraw_funds(amount):
        return f"Saque de ${amount:.2f} realizado com sucesso", get_account_info()
    else:
        return "Erro: Saldo insuficiente para o saque.", None

def buy_shares(symbol, quantity):
    if account is None:
        return "Erro: Nenhuma conta existe. Crie uma conta primeiro.", None

    try:
        quantity = int(quantity)
    except ValueError:
        return "Erro: A quantidade deve ser um número inteiro.", None

    if quantity <= 0:
        return "Erro: A quantidade deve ser positiva.", None

    symbol = symbol.upper()
    price = get_share_price(symbol)

    if price == 0.0:
        return f"Erro: Símbolo {symbol} não encontrado.", None

    if account.buy_shares(symbol, quantity):
        return f"Compra de {quantity} ações de {symbol} realizada a ${price:.2f} cada.", get_account_info()
    else:
        return "Erro: Saldo insuficiente para comprar as ações.", None

def sell_shares(symbol, quantity):
    if account is None:
        return "Erro: Nenhuma conta existe. Crie uma conta primeiro.", None

    try:
        quantity = int(quantity)
    except ValueError:
        return "Erro: A quantidade deve ser um número inteiro.", None

    if quantity <= 0:
        return "Erro: A quantidade deve ser positiva.", None

    symbol = symbol.upper()

    if account.sell_shares(symbol, quantity):
        return f"Venda de {quantity} ações de {symbol} realizada com sucesso.", get_account_info()
    else:
        return "Erro: Ações insuficientes para vender.", None

def get_portfolio_value():
    if account is None:
        return "Erro: Nenhuma conta existe. Crie uma conta primeiro."

    value = account.calculate_portfolio_value()
    return f"Valor total do portfólio: ${value:.2f}"

def get_profit_loss():
    if account is None:
        return "Erro: Nenhuma conta existe. Crie uma conta primeiro."

    pnl = account.calculate_profit_or_loss()
    if pnl >= 0:
        return f"Lucro: ${pnl:.2f}"
    else:
        return f"Prejuízo: ${-pnl:.2f}"

def get_holdings():
    if account is None:
        return "Erro: Nenhuma conta existe. Crie uma conta primeiro."

    holdings = account.get_holdings()
    if not holdings:
        return "Nenhuma participação encontrada."

    result = "Participações atuais:\n"
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        result += f"{symbol}: {quantity} ações a ${price:.2f} cada = ${value:.2f}\n"

    return result

def get_transactions():
    if account is None:
        return "Erro: Nenhuma conta existe. Crie uma conta primeiro."

    transactions = account.get_transactions()
    if not transactions:
        return "Nenhuma transação encontrada."

    result = "Histórico de transações:\n"
    for i, tx in enumerate(transactions, 1):
        if tx['type'] == 'deposit':
            result += f"{i}. Depósito: ${tx['amount']:.2f}\n"
        elif tx['type'] == 'withdrawal':
            result += f"{i}. Saque: ${tx['amount']:.2f}\n"
        elif tx['type'] == 'buy':
            result += f"{i}. Compra: {tx['quantity']} ações de {tx['symbol']} a ${tx['price']:.2f} = ${tx['total']:.2f}\n"
        elif tx['type'] == 'sell':
            result += f"{i}. Venda: {tx['quantity']} ações de {tx['symbol']} a ${tx['price']:.2f} = ${tx['total']:.2f}\n"

    return result

def get_account_info():
    if account is None:
        return "Nenhuma conta existe. Crie uma conta primeiro."

    report = account.get_report()

    result = f"ID do usuário: {report['user_id']}\n"
    result += f"Saldo em caixa: ${report['balance']:.2f}\n"
    result += f"Valor do portfólio: ${report['portfolio_value']:.2f}\n"

    pnl = report['profit_or_loss']
    if pnl >= 0:
        result += f"Lucro: ${pnl:.2f}\n"
    else:
        result += f"Prejuízo: ${-pnl:.2f}\n"

    result += "\nParticipações:\n"
    if not report['holdings']:
        result += "Nenhuma participação\n"
    else:
        for symbol, quantity in report['holdings'].items():
            price = get_share_price(symbol)
            value = price * quantity
            result += f"{symbol}: {quantity} ações a ${price:.2f} cada = ${value:.2f}\n"

    return result

with gr.Blocks(title="Plataforma de Simulação de Negociações") as demo:
    gr.Markdown("# Plataforma de Simulação de Negociações")

    with gr.Tab("Gerenciamento de Conta"):
        with gr.Group():
            gr.Markdown("### Criar Conta")
            with gr.Row():
                user_id_input = gr.Textbox(label="ID do Usuário")
                initial_deposit_input = gr.Textbox(label="Depósito Inicial ($)")
            create_btn = gr.Button("Criar Conta")

        with gr.Group():
            gr.Markdown("### Depositar/Sacar Fundos")
            with gr.Row():
                deposit_input = gr.Textbox(label="Valor do Depósito ($)")
                deposit_btn = gr.Button("Depositar")
            with gr.Row():
                withdraw_input = gr.Textbox(label="Valor do Saque ($)")
                withdraw_btn = gr.Button("Sacar")

    with gr.Tab("Negociações"):
        with gr.Group():
            gr.Markdown("### Comprar Ações")
            with gr.Row():
                buy_symbol_input = gr.Textbox(label="Símbolo (AAPL, TSLA, GOOGL)")
                buy_quantity_input = gr.Textbox(label="Quantidade")
            buy_btn = gr.Button("Comprar Ações")

        with gr.Group():
            gr.Markdown("### Vender Ações")
            with gr.Row():
                sell_symbol_input = gr.Textbox(label="Símbolo")
                sell_quantity_input = gr.Textbox(label="Quantidade")
            sell_btn = gr.Button("Vender Ações")

    with gr.Tab("Relatórios"):
        with gr.Group():
            gr.Markdown("### Resumo da Conta")
            portfolio_btn = gr.Button("Valor do Portfólio")
            portfolio_output = gr.Textbox(label="Valor do Portfólio")

            profit_btn = gr.Button("Lucro/Prejuízo")
            profit_output = gr.Textbox(label="Lucro/Prejuízo")

            holdings_btn = gr.Button("Participações Atuais")
            holdings_output = gr.Textbox(label="Participações")

            transactions_btn = gr.Button("Histórico de Transações")
            transactions_output = gr.Textbox(label="Transações", max_lines=20)

    # Área geral de saída para resultados das operações
    result_output = gr.Textbox(label="Resultado da Operação")
    account_info = gr.Textbox(label="Informações da Conta", max_lines=20)

    # Associação de eventos
    create_btn.click(
        fn=create_account,
        inputs=[user_id_input, initial_deposit_input],
        outputs=[result_output, account_info]
    )

    deposit_btn.click(
        fn=deposit,
        inputs=[deposit_input],
        outputs=[result_output, account_info]
    )

    withdraw_btn.click(
        fn=withdraw,
        inputs=[withdraw_input],
        outputs=[result_output, account_info]
    )

    buy_btn.click(
        fn=buy_shares,
        inputs=[buy_symbol_input, buy_quantity_input],
        outputs=[result_output, account_info]
    )

    sell_btn.click(
        fn=sell_shares,
        inputs=[sell_symbol_input, sell_quantity_input],
        outputs=[result_output, account_info]
    )

    portfolio_btn.click(
        fn=get_portfolio_value,
        inputs=[],
        outputs=[portfolio_output]
    )

    profit_btn.click(
        fn=get_profit_loss,
        inputs=[],
        outputs=[profit_output]
    )

    holdings_btn.click(
        fn=get_holdings,
        inputs=[],
        outputs=[holdings_output]
    )

    transactions_btn.click(
        fn=get_transactions,
        inputs=[],
        outputs=[transactions_output]
    )

if __name__ == "__main__":
    demo.launch()
