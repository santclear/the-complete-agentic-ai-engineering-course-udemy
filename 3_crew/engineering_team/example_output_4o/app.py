import gradio as gr
from accounts import Account, get_share_price

# Inicializa uma conta
account = Account("user1")

def create_account(deposit_amount):
    """Cria uma conta com depósito inicial"""
    if account.deposit(float(deposit_amount)):
        return f"Conta criada com ID: {account.account_id}. Depósito inicial: ${deposit_amount}"
    else:
        return "Falha ao criar a conta. O valor do depósito deve ser positivo."

def deposit_funds(amount):
    """Deposita fundos na conta"""
    if account.deposit(float(amount)):
        return f"Depósito de ${amount} realizado com sucesso. Novo saldo: ${account.balance:.2f}"
    else:
        return "Falha ao depositar. O valor deve ser positivo."

def withdraw_funds(amount):
    """Saca fundos da conta"""
    if account.withdraw(float(amount)):
        return f"Saque de ${amount} realizado com sucesso. Novo saldo: ${account.balance:.2f}"
    else:
        return "Falha ao sacar. Saldo insuficiente ou valor inválido."

def buy_stock(symbol, quantity):
    """Compra ações de um ativo"""
    try:
        quantity = int(quantity)
        if account.buy_shares(symbol, quantity, get_share_price):
            return f"Compra de {quantity} ações de {symbol} realizada a ${get_share_price(symbol):.2f} por ação. Novo saldo: ${account.balance:.2f}"
        else:
            return "Falha ao comprar ações. Saldo insuficiente ou quantidade inválida."
    except ValueError:
        return "A quantidade deve ser um número inteiro válido."

def sell_stock(symbol, quantity):
    """Vende ações de um ativo"""
    try:
        quantity = int(quantity)
        if account.sell_shares(symbol, quantity, get_share_price):
            return f"Venda de {quantity} ações de {symbol} realizada a ${get_share_price(symbol):.2f} por ação. Novo saldo: ${account.balance:.2f}"
        else:
            return "Falha ao vender ações. Ações insuficientes ou quantidade inválida."
    except ValueError:
        return "A quantidade deve ser um número inteiro válido."

def get_portfolio():
    """Obtém as participações e o valor do portfólio"""
    holdings = account.get_holdings()
    if not holdings:
        return "Você ainda não possui ações."
    
    result = "Portfólio Atual:\n"
    total_value = 0
    
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        total_value += value
        result += f"{symbol}: {quantity} ações a ${price:.2f} cada = ${value:.2f}\n"
    
    result += f"\nValor Total do Portfólio: ${total_value:.2f}"
    result += f"\nSaldo em Caixa: ${account.balance:.2f}"
    result += f"\nValor Total da Conta: ${(total_value + account.balance):.2f}"
    
    profit_loss = account.get_profit_or_loss(get_share_price)
    if profit_loss > 0:
        result += f"\nLucro: ${profit_loss:.2f}"
    else:
        result += f"\nPrejuízo: ${-profit_loss:.2f}"
    
    return result

def list_transactions():
    """Lista todas as transações realizadas pelo usuário"""
    transactions = account.get_transactions()
    if not transactions:
        return "Nenhuma transação registrada."
    
    result = "Histórico de Transações:\n"
    for idx, tx in enumerate(transactions, 1):
        if tx['type'] == 'deposit':
            result += f"{idx}. Depósito: ${tx['amount']:.2f}, Saldo: ${tx['balance']:.2f}\n"
        elif tx['type'] == 'withdraw':
            result += f"{idx}. Saque: ${tx['amount']:.2f}, Saldo: ${tx['balance']:.2f}\n"
        elif tx['type'] == 'buy':
            result += f"{idx}. Compra: {tx['quantity']} {tx['symbol']} a ${tx['price']:.2f}, Total: ${tx['total']:.2f}, Saldo: ${tx['balance']:.2f}\n"
        elif tx['type'] == 'sell':
            result += f"{idx}. Venda: {tx['quantity']} {tx['symbol']} a ${tx['price']:.2f}, Total: ${tx['total']:.2f}, Saldo: ${tx['balance']:.2f}\n"
    
    return result

def check_price(symbol):
    """Verifica o preço atual de um ativo"""
    price = get_share_price(symbol)
    if price > 0:
        return f"Preço atual de {symbol}: ${price:.2f}"
    else:
        return f"Ativo {symbol} não encontrado. Ações disponíveis: AAPL, TSLA, GOOGL"

# Cria a interface Gradio
with gr.Blocks(title="Plataforma de Simulação de Negociações") as demo:
    gr.Markdown("# Plataforma de Simulação de Negociações")
    
    with gr.Tab("Criar Conta"):
        with gr.Row():
            deposit_input = gr.Number(label="Valor do Depósito Inicial ($)", value=1000)
            create_btn = gr.Button("Criar Conta")
        create_output = gr.Textbox(label="Resultado")
        create_btn.click(create_account, inputs=[deposit_input], outputs=[create_output])
    
    with gr.Tab("Depósito/Saque"):
        with gr.Row():
            with gr.Column():
                deposit_amount = gr.Number(label="Valor do Depósito ($)")
                deposit_btn = gr.Button("Depositar")
            with gr.Column():
                withdraw_amount = gr.Number(label="Valor do Saque ($)")
                withdraw_btn = gr.Button("Sacar")
        fund_output = gr.Textbox(label="Resultado")
        deposit_btn.click(deposit_funds, inputs=[deposit_amount], outputs=[fund_output])
        withdraw_btn.click(withdraw_funds, inputs=[withdraw_amount], outputs=[fund_output])
    
    with gr.Tab("Negociar Ações"):
        with gr.Row():
            with gr.Column():
                buy_symbol = gr.Dropdown(label="Símbolo", choices=["AAPL", "TSLA", "GOOGL"])
                buy_quantity = gr.Number(label="Quantidade", precision=0)
                buy_btn = gr.Button("Comprar Ações")
            with gr.Column():
                sell_symbol = gr.Dropdown(label="Símbolo", choices=["AAPL", "TSLA", "GOOGL"])
                sell_quantity = gr.Number(label="Quantidade", precision=0)
                sell_btn = gr.Button("Vender Ações")
        trade_output = gr.Textbox(label="Resultado")
        buy_btn.click(buy_stock, inputs=[buy_symbol, buy_quantity], outputs=[trade_output])
        sell_btn.click(sell_stock, inputs=[sell_symbol, sell_quantity], outputs=[trade_output])
    
    with gr.Tab("Consultar Preço"):
        with gr.Row():
            price_symbol = gr.Dropdown(label="Símbolo", choices=["AAPL", "TSLA", "GOOGL"])
            price_btn = gr.Button("Verificar Preço")
        price_output = gr.Textbox(label="Resultado")
        price_btn.click(check_price, inputs=[price_symbol], outputs=[price_output])
    
    with gr.Tab("Portfólio"):
        portfolio_btn = gr.Button("Ver Portfólio")
        portfolio_output = gr.Textbox(label="Detalhes do Portfólio")
        portfolio_btn.click(get_portfolio, inputs=[], outputs=[portfolio_output])
    
    with gr.Tab("Histórico de Transações"):
        transaction_btn = gr.Button("Ver Transações")
        transaction_output = gr.Textbox(label="Histórico de Transações")
        transaction_btn.click(list_transactions, inputs=[], outputs=[transaction_output])

if __name__ == "__main__":
    demo.launch()
