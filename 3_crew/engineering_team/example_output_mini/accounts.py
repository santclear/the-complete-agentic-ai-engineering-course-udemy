# accounts.py

class Account:
    def __init__(self, username: str, initial_deposit: float):
        """
        Inicializa uma conta com um nome de usuário e um depósito inicial.

        :param username: Nome do usuário da conta.
        :param initial_deposit: Valor inicial depositado na conta.
        """
        self.username = username
        self.balance = initial_deposit
        self.holdings = {}  # {símbolo: quantidade}
        self.transactions = []  # Lista de registros de transações
        self.initial_deposit = initial_deposit

    def deposit(self, amount: float) -> None:
        """
        Deposita fundos na conta.

        :param amount: Valor a ser depositado.
        """
        if amount <= 0:
            raise ValueError("O valor do depósito deve ser positivo.")
        self.balance += amount
        self.transactions.append(f"Depositado: ${amount:.2f}")

    def withdraw(self, amount: float) -> None:
        """
        Saca fundos da conta.

        :param amount: Valor a ser sacado.
        :raises ValueError: Se o saque deixar o saldo negativo.
        """
        if amount <= 0:
            raise ValueError("O valor do saque deve ser positivo.")
        if self.balance - amount < 0:
            raise ValueError("Não é possível sacar, fundos insuficientes.")
        self.balance -= amount
        self.transactions.append(f"Sacado: ${amount:.2f}")

    def buy_shares(self, symbol: str, quantity: int) -> None:
        """
        Compra ações de uma empresa específica.

        :param symbol: Símbolo da ação a ser comprada.
        :param quantity: Número de ações a comprar.
        :raises ValueError: Se tentar comprar mais ações do que o saldo permite.
        """
        if quantity <= 0:
            raise ValueError("A quantidade deve ser positiva.")
        share_price = get_share_price(symbol)
        total_cost = share_price * quantity

        if self.balance < total_cost:
            raise ValueError("Não é possível comprar, fundos insuficientes.")

        self.balance -= total_cost
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
        self.transactions.append(f"Comprado: {quantity} ações de {symbol} a ${share_price:.2f} cada")

    def sell_shares(self, symbol: str, quantity: int) -> None:
        """
        Vende ações de uma empresa específica.

        :param symbol: Símbolo da ação a ser vendida.
        :param quantity: Número de ações a vender.
        :raises ValueError: Se tentar vender mais ações do que possui.
        """
        if quantity <= 0:
            raise ValueError("A quantidade deve ser positiva.")
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            raise ValueError("Não é possível vender, ações insuficientes.")

        share_price = get_share_price(symbol)
        total_sale_value = share_price * quantity

        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]  # Remove o símbolo se não restarem ações
        self.balance += total_sale_value
        self.transactions.append(f"Vendido: {quantity} ações de {symbol} a ${share_price:.2f} cada")

    def portfolio_value(self) -> float:
        """
        Calcula o valor total do portfólio do usuário.

        :return: Valor total das participações mais o saldo.
        """
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def profit_or_loss(self) -> float:
        """
        Calcula o lucro ou prejuízo em relação ao depósito inicial.

        :return: Valor de lucro ou prejuízo.
        """
        return self.portfolio_value() - self.initial_deposit

    def report_holdings(self) -> dict:
        """
        Relata as participações atuais do usuário.

        :return: Dicionário de participações com símbolos e quantidades.
        """
        return self.holdings

    def report_transactions(self) -> list:
        """
        Lista todas as transações realizadas pelo usuário.

        :return: Lista de registros de transações.
        """
        return self.transactions


def get_share_price(symbol: str) -> float:
    """
    Função simulada que retorna o preço atual de uma ação.

    :param symbol: Símbolo da ação para consulta de preço.
    :return: Preço da ação.
    """
    mock_prices = {
        'AAPL': 150.00,  # Apple
        'TSLA': 700.00,  # Tesla
        'GOOGL': 2800.00  # Google
    }
    return mock_prices.get(symbol, 0.0)  # Retorna 0.0 para símbolos desconhecidos
