import unittest
from unittest.mock import Mock, patch

class TestGetSharePrice(unittest.TestCase):
    """Testes para a função get_share_price"""
    
    def test_known_symbols(self):
        """Testa se símbolos conhecidos retornam os preços esperados"""
        from accounts import get_share_price
        
        self.assertEqual(get_share_price('AAPL'), 150.0)
        self.assertEqual(get_share_price('TSLA'), 800.0)
        self.assertEqual(get_share_price('GOOGL'), 2500.0)
        
    def test_unknown_symbol(self):
        """Testa se símbolos desconhecidos retornam 0.0"""
        from accounts import get_share_price
        
        self.assertEqual(get_share_price('UNKNOWN'), 0.0)


class TestAccount(unittest.TestCase):
    """Testes para a classe Account"""
    
    def setUp(self):
        """Configura uma conta de teste antes de cada teste"""
        from accounts import Account
        self.account = Account('test123')
        
    def test_init(self):
        """Testa a inicialização da conta"""
        self.assertEqual(self.account.account_id, 'test123')
        self.assertEqual(self.account.balance, 0.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])
        self.assertEqual(self.account.initial_deposit, 0.0)
    
    def test_deposit_valid(self):
        """Testa depósito válido"""
        result = self.account.deposit(1000.0)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0]['type'], 'deposit')
        self.assertEqual(self.account.transactions[0]['amount'], 1000.0)
        
        # Adiciona outro depósito
        result = self.account.deposit(500.0)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 1500.0)
        # O depósito inicial deve continuar sendo o primeiro depósito
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(len(self.account.transactions), 2)
    
    def test_deposit_invalid(self):
        """Testa depósitos inválidos (valores zero ou negativos)"""
        result = self.account.deposit(0.0)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 0.0)
        self.assertEqual(len(self.account.transactions), 0)
        
        result = self.account.deposit(-100.0)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 0.0)
        self.assertEqual(len(self.account.transactions), 0)

    def test_withdraw_valid(self):
        """Testa saque válido"""
        self.account.deposit(1000.0)
        result = self.account.withdraw(500.0)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]['type'], 'withdraw')
        self.assertEqual(self.account.transactions[1]['amount'], 500.0)
    
    def test_withdraw_insufficient_funds(self):
        """Testa saque com saldo insuficiente"""
        self.account.deposit(100.0)
        result = self.account.withdraw(200.0)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(len(self.account.transactions), 1)  # Apenas a transação de depósito
    
    def test_withdraw_negative_amount(self):
        """Testa saque com valor negativo"""
        self.account.deposit(100.0)
        result = self.account.withdraw(-50.0)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(len(self.account.transactions), 1)  # Apenas a transação de depósito

    def test_buy_shares_valid(self):
        """Testa compra de ações com saldo suficiente"""
        from accounts import get_share_price
        
        self.account.deposit(1000.0)
        result = self.account.buy_shares('AAPL', 5, get_share_price)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 250.0)  # 1000 - (5 * 150)
        self.assertEqual(self.account.holdings['AAPL'], 5)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]['type'], 'buy')
        self.assertEqual(self.account.transactions[1]['symbol'], 'AAPL')
        self.assertEqual(self.account.transactions[1]['quantity'], 5)
        
        # Compra mais do mesmo ativo
        result = self.account.buy_shares('AAPL', 1, get_share_price)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 100.0)  # 250 - (1 * 150)
        self.assertEqual(self.account.holdings['AAPL'], 6)

    def test_buy_shares_insufficient_funds(self):
        """Testa compra de ações com saldo insuficiente"""
        from accounts import get_share_price
        
        self.account.deposit(100.0)
        result = self.account.buy_shares('AAPL', 5, get_share_price)  # Custa 750.0
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(len(self.account.transactions), 1)  # Apenas a transação de depósito

    def test_buy_shares_invalid_quantity(self):
        """Testa compra de ações com quantidade inválida"""
        from accounts import get_share_price
        
        self.account.deposit(1000.0)
        result = self.account.buy_shares('AAPL', 0, get_share_price)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.holdings, {})
        
        result = self.account.buy_shares('AAPL', -5, get_share_price)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.holdings, {})

    def test_sell_shares_valid(self):
        """Testa venda de ações que o usuário possui"""
        from accounts import get_share_price
        
        self.account.deposit(1000.0)
        self.account.buy_shares('AAPL', 5, get_share_price)
        result = self.account.sell_shares('AAPL', 2, get_share_price)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 550.0)  # 250 + (2 * 150)
        self.assertEqual(self.account.holdings['AAPL'], 3)
        self.assertEqual(len(self.account.transactions), 3)
        self.assertEqual(self.account.transactions[2]['type'], 'sell')
        
        # Vende as ações restantes
        result = self.account.sell_shares('AAPL', 3, get_share_price)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 1000.0)  # 550 + (3 * 150)
        self.assertNotIn('AAPL', self.account.holdings)  # Todas as ações vendidas

    def test_sell_shares_insufficient_shares(self):
        """Testa venda de mais ações do que o usuário possui"""
        from accounts import get_share_price
        
        self.account.deposit(1000.0)
        self.account.buy_shares('AAPL', 5, get_share_price)
        result = self.account.sell_shares('AAPL', 10, get_share_price)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 250.0)  # Sem alterações
        self.assertEqual(self.account.holdings['AAPL'], 5)  # Sem alterações

    def test_sell_shares_invalid_quantity(self):
        """Testa venda de quantidade inválida de ações"""
        from accounts import get_share_price
        
        self.account.deposit(1000.0)
        self.account.buy_shares('AAPL', 5, get_share_price)
        result = self.account.sell_shares('AAPL', 0, get_share_price)
        self.assertFalse(result)
        self.assertEqual(self.account.holdings['AAPL'], 5)  # Sem alterações
        
        result = self.account.sell_shares('AAPL', -2, get_share_price)
        self.assertFalse(result)
        self.assertEqual(self.account.holdings['AAPL'], 5)  # Sem alterações

    def test_get_portfolio_value(self):
        """Testa a obtenção do valor do portfólio"""
        from accounts import get_share_price, Account
        
        # Cria uma conta real com participações
        account = Account('test')
        account.holdings = {'AAPL': 5, 'TSLA': 2}
        
        # Calcula o valor esperado: (5 * 150) + (2 * 800) = 750 + 1600 = 2350
        expected_value = 2350.0
        actual_value = account.get_portfolio_value(get_share_price)
        
        self.assertEqual(actual_value, expected_value)

    def test_get_profit_or_loss(self):
        """Testa o cálculo de lucro ou prejuízo"""
        from accounts import Account, get_share_price
        
        account = Account('test')
        account.deposit(1000.0)  # Depósito inicial
        
        # Sem ações, ainda sem lucro/prejuízo
        self.assertEqual(account.get_profit_or_loss(get_share_price), 0.0)
        
        # Compra algumas ações
        account.buy_shares('AAPL', 5, get_share_price)  # Custa 750
        
        # Situação atual: 250 de saldo + (5 * 150) em ações = 1000, portanto o lucro/prejuízo é 0
        self.assertEqual(account.get_profit_or_loss(get_share_price), 0.0)
        
        # Simula a mudança de preço usando uma função personalizada
        def higher_prices(symbol):
            prices = {
                'AAPL': 200.0,  # Aumentou de 150
                'TSLA': 800.0,
                'GOOGL': 2500.0
            }
            return prices.get(symbol, 0.0)
        
        # Com preços maiores: 250 de saldo + (5 * 200) em ações = 1250, então o lucro é 250
        self.assertEqual(account.get_profit_or_loss(higher_prices), 250.0)

    def test_get_holdings(self):
        """Testa a obtenção de uma cópia das participações do usuário"""
        from accounts import Account, get_share_price
        
        account = Account('test')
        account.deposit(1000.0)
        account.buy_shares('AAPL', 5, get_share_price)
        
        holdings = account.get_holdings()
        self.assertEqual(holdings, {'AAPL': 5})
        
        # Verifica se é uma cópia alterando o dicionário retornado
        holdings['AAPL'] = 10
        self.assertEqual(account.holdings['AAPL'], 5)  # Original inalterado

    def test_get_transactions(self):
        """Testa a obtenção de uma cópia das transações do usuário"""
        from accounts import Account, get_share_price
        
        account = Account('test')
        account.deposit(1000.0)
        account.buy_shares('AAPL', 5, get_share_price)
        
        transactions = account.get_transactions()
        self.assertEqual(len(transactions), 2)
        
        # Verifica se é uma cópia alterando a lista retornada
        transactions.append({'fake': 'transaction'})
        self.assertEqual(len(account.transactions), 2)  # Original inalterado

    def test_can_withdraw(self):
        """Testa o método de verificação can_withdraw"""
        from accounts import Account
        
        account = Account('test')
        account.deposit(100.0)
        
        self.assertTrue(account.can_withdraw(50.0))
        self.assertTrue(account.can_withdraw(100.0))
        self.assertFalse(account.can_withdraw(150.0))
        self.assertFalse(account.can_withdraw(0.0))
        self.assertFalse(account.can_withdraw(-50.0))

    def test_can_buy_shares(self):
        """Testa o método de verificação can_buy_shares"""
        from accounts import Account, get_share_price
        
        account = Account('test')
        account.deposit(1000.0)
        
        # Pode comprar ações com saldo suficiente
        self.assertTrue(account.can_buy_shares('AAPL', 6, get_share_price))  # 6 * 150 = 900
        self.assertTrue(account.can_buy_shares('AAPL', 6.5, get_share_price))  # 6.5 * 150 = 975
        
        # Não pode comprar ações com saldo insuficiente
        self.assertFalse(account.can_buy_shares('AAPL', 7, get_share_price))  # 7 * 150 = 1050
        
        # Não pode comprar quantidades inválidas
        self.assertFalse(account.can_buy_shares('AAPL', 0, get_share_price))
        self.assertFalse(account.can_buy_shares('AAPL', -5, get_share_price))
        
        # Não pode comprar ações com preço 0
        self.assertFalse(account.can_buy_shares('UNKNOWN', 5, get_share_price))

    def test_can_sell_shares(self):
        """Testa o método de verificação can_sell_shares"""
        from accounts import Account, get_share_price
        
        account = Account('test')
        account.deposit(1000.0)
        account.buy_shares('AAPL', 5, get_share_price)
        
        # Pode vender ações que o usuário possui
        self.assertTrue(account.can_sell_shares('AAPL', 3))
        self.assertTrue(account.can_sell_shares('AAPL', 5))
        
        # Não pode vender mais ações do que o usuário possui
        self.assertFalse(account.can_sell_shares('AAPL', 6))
        
        # Não pode vender ações que o usuário não possui
        self.assertFalse(account.can_sell_shares('TSLA', 1))
        
        # Não pode vender quantidades inválidas
        self.assertFalse(account.can_sell_shares('AAPL', 0))
        self.assertFalse(account.can_sell_shares('AAPL', -1))


if __name__ == '__main__':
    unittest.main()
