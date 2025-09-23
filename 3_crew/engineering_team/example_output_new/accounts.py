def get_share_price(symbol):
    """Retorna o preço atual de uma ação para o símbolo informado.

    Esta é uma implementação simulada que devolve preços fixos para símbolos de teste.

    Parâmetros:
        symbol (str): Símbolo da ação para obter o preço

    Retorna:
        float: Preço atual da ação
    """
    prices = {
        'AAPL': 150.0,
        'TSLA': 800.0,
        'GOOGL': 2500.0
    }
    return prices.get(symbol, 0.0)

class Account:
    """Classe que modela a conta de um usuário em uma plataforma de simulação de negociações.

    Ela lida com gestão de fundos, transações de ações e oferece métodos para gerar relatórios
    sobre as atividades financeiras do usuário.
    """

    def __init__(self, user_id, initial_deposit):
        """Inicializa um novo objeto Account.

        Parâmetros:
            user_id (str): Identificador exclusivo do usuário
            initial_deposit (float): Valor do depósito inicial na criação da conta
        """
        self.user_id = user_id
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.holdings = {}
        self.transactions = []

        # Registra o depósito inicial como uma transação
        self.transactions.append({
            'type': 'deposit',
            'amount': initial_deposit,
            'timestamp': 'initial deposit'
        })

    def deposit_funds(self, amount):
        """Adiciona o valor especificado ao saldo da conta do usuário.

        Parâmetros:
            amount (float): Valor a ser depositado
        """
        self.balance += amount

        # Registra a transação
        self.transactions.append({
            'type': 'deposit',
            'amount': amount,
            'timestamp': 'now'  # Em um sistema real, usaríamos um carimbo de data adequado
        })

    def withdraw_funds(self, amount):
        """Tenta sacar o valor especificado do saldo do usuário.

        Parâmetros:
            amount (float): Valor a ser sacado

        Retorna:
            bool: True se bem-sucedido, False caso contrário
        """
        if amount > self.balance:
            return False

        self.balance -= amount

        # Registra a transação
        self.transactions.append({
            'type': 'withdrawal',
            'amount': amount,
            'timestamp': 'now'  # Em um sistema real, usaríamos um carimbo de data adequado
        })

        return True

    def buy_shares(self, symbol, quantity):
        """Compra a quantidade especificada de ações para o símbolo fornecido.

        Parâmetros:
            symbol (str): Símbolo da ação
            quantity (int): Número de ações a comprar

        Retorna:
            bool: True se bem-sucedido, False caso contrário
        """
        price = get_share_price(symbol)
        total_cost = price * quantity

        if total_cost > self.balance:
            return False

        self.balance -= total_cost

        # Atualiza as participações
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity

        # Registra a transação
        self.transactions.append({
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_cost,
            'timestamp': 'now'  # Em um sistema real, usaríamos um carimbo de data adequado
        })

        return True

    def sell_shares(self, symbol, quantity):
        """Vende a quantidade especificada de ações para o símbolo fornecido.

        Parâmetros:
            symbol (str): Símbolo da ação
            quantity (int): Número de ações a vender

        Retorna:
            bool: True se bem-sucedido, False caso contrário
        """
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            return False

        price = get_share_price(symbol)
        total_revenue = price * quantity

        self.balance += total_revenue

        # Atualiza as participações
        self.holdings[symbol] -= quantity

        # Remove o símbolo das participações se a quantidade chegar a 0
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]

        # Registra a transação
        self.transactions.append({
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_revenue,
            'timestamp': 'now'  # Em um sistema real, usaríamos um carimbo de data adequado
        })

        return True

    def calculate_portfolio_value(self):
        """Calcula o valor total do portfólio do usuário.

        Retorna:
            float: Valor total do portfólio
        """
        total_value = self.balance

        for symbol, quantity in self.holdings.items():
            total_value += get_share_price(symbol) * quantity

        return total_value

    def calculate_profit_or_loss(self):
        """Calcula o lucro ou prejuízo atual do usuário desde o depósito inicial.

        Retorna:
            float: Lucro ou prejuízo
        """
        return self.calculate_portfolio_value() - self.initial_deposit

    def get_holdings(self):
        """Retorna um dicionário com as participações atuais e respectivas quantidades.

        Retorna:
            dict: Dicionário que mapeia símbolos de ações para quantidades
        """
        return self.holdings.copy()

    def get_transactions(self):
        """Retorna uma lista de todas as transações realizadas pelo usuário.

        Retorna:
            list: Lista com todas as transações
        """
        return self.transactions.copy()

    def get_report(self):
        """Retorna um relatório completo da conta do usuário.

        Retorna:
            dict: Dicionário contendo informações da conta
        """
        return {
            'user_id': self.user_id,
            'balance': self.balance,
            'holdings': self.get_holdings(),
            'portfolio_value': self.calculate_portfolio_value(),
            'profit_or_loss': self.calculate_profit_or_loss()
        }
