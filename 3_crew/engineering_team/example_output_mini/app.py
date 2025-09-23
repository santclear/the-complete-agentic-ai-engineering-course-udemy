import gradio as gr
from accounts import Account

# Cria uma instância da classe Account para demonstração
account = Account("DemoUser", initial_deposit=1000.0)

def create_account(username: str, initial_deposit: float):
    global account
    account = Account(username, initial_deposit)
    return f"Conta criada para {username} com depósito inicial de ${initial_deposit:.2f}"

def deposit_funds(amount: float):
    account.deposit(amount)
    return f"Depositado: ${amount:.2f}. Saldo atual: ${account.balance:.2f}"

def withdraw_funds(amount: float):
    try:
        account.withdraw(amount)
        return f"Sacado: ${amount:.2f}. Saldo atual: ${account.balance:.2f}"
    except ValueError as e:
        return str(e)

def buy_shares(symbol: str, quantity: int):
    try:
        account.buy_shares(symbol, quantity)
        return f"Comprado: {quantity} ações de {symbol}."
    except ValueError as e:
        return str(e)

def sell_shares(symbol: str, quantity: int):
    try:
        account.sell_shares(symbol, quantity)
        return f"Vendido: {quantity} ações de {symbol}."
    except ValueError as e:
        return str(e)

def view_portfolio():
    return f"Portfólio atual: {account.report_holdings()}"

def view_profit_or_loss():
    return f"Lucro/Prejuízo: ${account.profit_or_loss():.2f}"

def view_transactions():
    return "\n".join(account.report_transactions())

def total_portfolio_value():
    return f"Valor total do portfólio: ${account.portfolio_value():.2f}"

with gr.Blocks() as app:
    gr.Markdown("# Gerenciamento de Conta da Simulação de Negociações")

    with gr.Group():
        username_input = gr.Textbox(label="Nome de Usuário")
        initial_deposit_input = gr.Number(label="Depósito Inicial")
        create_button = gr.Button("Criar Conta")
        create_output = gr.Textbox(label="Resultado", interactive=False)
        create_button.click(create_account, inputs=[username_input, initial_deposit_input], outputs=create_output)

    with gr.Group():
        deposit_input = gr.Number(label="Valor do Depósito")
        deposit_button = gr.Button("Depositar Fundos")
        deposit_output = gr.Textbox(label="Resultado", interactive=False)
        deposit_button.click(deposit_funds, inputs=deposit_input, outputs=deposit_output)

    with gr.Group():
        withdraw_input = gr.Number(label="Valor do Saque")
        withdraw_button = gr.Button("Sacar Fundos")
        withdraw_output = gr.Textbox(label="Resultado", interactive=False)
        withdraw_button.click(withdraw_funds, inputs=withdraw_input, outputs=withdraw_output)

    with gr.Group():
        buy_symbol_input = gr.Textbox(label="Símbolo da Ação")
        buy_quantity_input = gr.Number(label="Quantidade")
        buy_button = gr.Button("Comprar Ações")
        buy_output = gr.Textbox(label="Resultado", interactive=False)
        buy_button.click(buy_shares, inputs=[buy_symbol_input, buy_quantity_input], outputs=buy_output)

    with gr.Group():
        sell_symbol_input = gr.Textbox(label="Símbolo da Ação")
        sell_quantity_input = gr.Number(label="Quantidade")
        sell_button = gr.Button("Vender Ações")
        sell_output = gr.Textbox(label="Resultado", interactive=False)
        sell_button.click(sell_shares, inputs=[sell_symbol_input, sell_quantity_input], outputs=sell_output)

    with gr.Group():
        portfolio_button = gr.Button("Ver Portfólio")
        portfolio_output = gr.Textbox(label="Resultado", interactive=False)
        portfolio_button.click(view_portfolio, outputs=portfolio_output)

    with gr.Group():
        profit_loss_button = gr.Button("Ver Lucro/Prejuízo")
        profit_loss_output = gr.Textbox(label="Resultado", interactive=False)
        profit_loss_button.click(view_profit_or_loss, outputs=profit_loss_output)

    with gr.Group():
        transaction_button = gr.Button("Ver Transações")
        transaction_output = gr.Textbox(label="Resultado", interactive=False)
        transaction_button.click(view_transactions, outputs=transaction_output)

    with gr.Group():
        portfolio_value_button = gr.Button("Valor Total do Portfólio")
        portfolio_value_output = gr.Textbox(label="Resultado", interactive=False)
        portfolio_value_button.click(total_portfolio_value, outputs=portfolio_value_output)

if __name__ == "__main__":
    app.launch()
