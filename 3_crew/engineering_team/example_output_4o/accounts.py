def get_share_price(symbol):
    """Implementação de teste que retorna preços fixos para AAPL, TSLA, GOOGL"""
    prices = {
        'AAPL': 150.0,
        'TSLA': 800.0,
        'GOOGL': 2500.0
    }
    return prices.get(symbol, 0.0)

class Account:
    def __init__(self, account_id: str):
        """
        Inicializa uma nova conta com um account_id exclusivo.
        
        Parâmetros:
            account_id: Identificador exclusivo para a conta
        """
        self.account_id = account_id
        self.balance = 0.0
        self.holdings = {}  # Símbolo -> Quantidade
        self.transactions = []
        self.initial_deposit = 0.0
        
    def deposit(self, amount: float) -> bool:
        """
        Adiciona fundos à conta do usuário.
        
        Parâmetros:
            amount: Valor a ser depositado
            
        Retorna:
            True se for bem-sucedido, False para operações inválidas
        """
        if amount <= 0:
            return False
            
        self.balance += amount
        
        # Se este for o primeiro depósito, define como depósito inicial
        if not self.transactions:
            self.initial_deposit = amount
            
        # Registra a transação
        self.transactions.append({
            'type': 'deposit',
            'amount': amount,
            'balance': self.balance
        })
        
        return True
        
    def withdraw(self, amount: float) -> bool:
        """
        Remove fundos da conta do usuário.
        
        Parâmetros:
            amount: Valor a ser sacado
            
        Retorna:
            True se for bem-sucedido, False caso contrário
        """
        if not self.can_withdraw(amount):
            return False
            
        self.balance -= amount
        
        # Registra a transação
        self.transactions.append({
            'type': 'withdraw',
            'amount': amount,
            'balance': self.balance
        })
        
        return True
        
    def buy_shares(self, symbol: str, quantity: int, get_share_price: callable) -> bool:
        """
        Compra ações do símbolo fornecido.
        
        Parâmetros:
            symbol: Símbolo da ação
            quantity: Número de ações a comprar
            get_share_price: Função que obtém o preço atual de uma ação
            
        Retorna:
            True se for bem-sucedido, False caso contrário
        """
        if not self.can_buy_shares(symbol, quantity, get_share_price):
            return False
            
        price = get_share_price(symbol)
        cost = price * quantity
        
        self.balance -= cost
        
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
            'total': cost,
            'balance': self.balance
        })
        
        return True
        
    def sell_shares(self, symbol: str, quantity: int, get_share_price: callable) -> bool:
        """
        Vende ações do símbolo fornecido.
        
        Parâmetros:
            symbol: Símbolo da ação
            quantity: Número de ações a vender
            get_share_price: Função que obtém o preço atual de uma ação
            
        Retorna:
            True se for bem-sucedido, False caso contrário
        """
        if not self.can_sell_shares(symbol, quantity):
            return False
            
        price = get_share_price(symbol)
        revenue = price * quantity
        
        self.balance += revenue
        
        # Atualiza as participações
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
            
        # Registra a transação
        self.transactions.append({
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': revenue,
            'balance': self.balance
        })
        
        return True
        
    def get_portfolio_value(self, get_share_price: callable) -> float:
        """
        Calcula o valor total atual do portfólio do usuário.
        
        Parâmetros:
            get_share_price: Função que obtém o preço atual de uma ação
            
        Retorna:
            Valor total do portfólio
        """
        value = 0.0
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            value += price * quantity
            
        return value
        
    def get_profit_or_loss(self, get_share_price: callable) -> float:
        """
        Calcula o lucro ou prejuízo do usuário em relação ao depósito inicial.
        
        Parâmetros:
            get_share_price: Função que obtém o preço atual de uma ação
            
        Retorna:
            Valor de lucro ou prejuízo
        """
        current_total = self.balance + self.get_portfolio_value(get_share_price)
        return current_total - self.initial_deposit
        
    def get_holdings(self) -> dict:
        """
        Retorna as participações atuais do usuário.
        
        Retorna:
            Um dicionário mapeando símbolo -> quantidade
        """
        return self.holdings.copy()
        
    def get_transactions(self) -> list:
        """
        Retorna a lista de todas as transações realizadas pelo usuário.
        
        Retorna:
            Uma lista de dicionários de transações
        """
        return self.transactions.copy()
        
    def can_withdraw(self, amount: float) -> bool:
        """
        Verifica se o usuário pode sacar o valor especificado.
        
        Parâmetros:
            amount: Valor a verificar
            
        Retorna:
            True se o saque for possível, False caso contrário
        """
        return amount > 0 and self.balance >= amount
        
    def can_buy_shares(self, symbol: str, quantity: int, get_share_price: callable) -> bool:
        """
        Verifica se o usuário pode comprar as ações especificadas.
        
        Parâmetros:
            symbol: Símbolo da ação
            quantity: Número de ações a verificar
            get_share_price: Função que obtém o preço atual de uma ação
            
        Retorna:
            True se a compra for possível, False caso contrário
        """
        if quantity <= 0:
            return False
            
        price = get_share_price(symbol)
        return price > 0 and self.balance >= price * quantity
        
    def can_sell_shares(self, symbol: str, quantity: int) -> bool:
        """
        Verifica se o usuário possui ações suficientes para vender.
        
        Parâmetros:
            symbol: Símbolo da ação
            quantity: Número de ações a verificar
            
        Retorna:
            True se a venda for possível, False caso contrário
        """
        if quantity <= 0:
            return False
            
        return symbol in self.holdings and self.holdings[symbol] >= quantity
