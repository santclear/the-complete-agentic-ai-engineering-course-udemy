from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation as DecimalInvalidOperation
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import uuid

# ==========================
# Constantes e Tipos
# ==========================

MONEY_PLACES = Decimal("0.01")

DEFAULT_PRICES: Dict[str, Decimal] = {
    "AAPL": Decimal("190"),
    "TSLA": Decimal("250"),
    "GOOGL": Decimal("140"),
}

PriceFetcher = Callable[[str], Decimal]
NowProvider = Callable[[], datetime]

# ==========================
# Exceções
# ==========================

class AccountError(Exception):
    pass

class InvalidAmount(AccountError):
    pass

class InvalidQuantity(AccountError):
    pass

class InsufficientFunds(AccountError):
    pass

class InsufficientShares(AccountError):
    pass

class PriceUnavailable(AccountError):
    pass

class InvalidOperation(AccountError):
    pass

# ==========================
# Funções utilitárias
# ==========================

def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        # Avoid binary float issues by converting via string when possible
        if isinstance(value, (int, str)):
            return Decimal(str(value))
        elif isinstance(value, float):
            return Decimal(str(value))
        else:
            return Decimal(value)
    except (DecimalInvalidOperation, ValueError, TypeError):
        raise InvalidAmount(f"Valor monetário inválido: {value}")

def normalize_symbol(symbol: str) -> str:
    if not isinstance(symbol, str):
        raise InvalidOperation("Símbolo deve ser string")
    s = symbol.strip().upper()
    if not s:
        raise InvalidOperation("Símbolo inválido: vazio")
    return s

def quantize_money(amount: Decimal) -> Decimal:
    d = _to_decimal(amount)
    return d.quantize(MONEY_PLACES, rounding=ROUND_HALF_EVEN)

def ensure_positive_amount(amount: Decimal) -> Decimal:
    d = quantize_money(_to_decimal(amount))
    if d <= Decimal("0"):
        raise InvalidAmount("Valor deve ser positivo e maior que zero")
    return d

def ensure_positive_quantity(quantity: int) -> int:
    if isinstance(quantity, bool):
        # bool is subclass of int; disallow
        raise InvalidQuantity("Quantidade deve ser um inteiro positivo")
    if not isinstance(quantity, int):
        raise InvalidQuantity("Quantidade deve ser um inteiro positivo")
    if quantity <= 0:
        raise InvalidQuantity("Quantidade deve ser > 0")
    return quantity

# ==========================
# Entidades
# ==========================

class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Transaction:
    id: str
    timestamp: datetime
    type: TransactionType
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[Decimal] = None
    amount: Optional[Decimal] = None  # cash delta: + increases cash, - decreases
    cash_after: Decimal = Decimal("0.00")
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type.value,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": str(self.price) if self.price is not None else None,
            "amount": str(self.amount) if self.amount is not None else None,
            "cash_after": str(self.cash_after),
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        ts_raw = data.get("timestamp")
        if isinstance(ts_raw, str):
            # Support Z suffix
            ts_raw = ts_raw.replace("Z", "+00:00")
            timestamp = datetime.fromisoformat(ts_raw)
        elif isinstance(ts_raw, datetime):
            timestamp = ts_raw
        else:
            raise InvalidOperation("Timestamp inválido na transação")
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        ttype = data.get("type")
        if isinstance(ttype, TransactionType):
            tx_type = ttype
        else:
            tx_type = TransactionType(str(ttype))

        price = data.get("price")
        amount = data.get("amount")
        cash_after = data.get("cash_after")
        return cls(
            id=str(data.get("id")),
            timestamp=timestamp,
            type=tx_type,
            symbol=data.get("symbol"),
            quantity=int(data["quantity"]) if data.get("quantity") is not None else None,
            price=_to_decimal(price) if price is not None else None,
            amount=_to_decimal(amount) if amount is not None else None,
            cash_after=_to_decimal(cash_after) if cash_after is not None else Decimal("0.00"),
            note=data.get("note", ""),
        )

@dataclass
class Position:
    symbol: str
    quantity: int = 0
    avg_cost: Decimal = Decimal("0.00")
    total_cost: Decimal = Decimal("0.00")

    def apply_buy(self, quantity: int, price: Decimal) -> None:
        q = ensure_positive_quantity(quantity)
        p = ensure_positive_amount(price)
        # total cost add
        add_cost = quantize_money(p * q)
        new_total_cost = quantize_money(self.total_cost + add_cost)
        new_qty = self.quantity + q
        self.quantity = new_qty
        self.total_cost = new_total_cost
        # avg cost recompute
        self.avg_cost = quantize_money(self.total_cost / Decimal(self.quantity))

    def apply_sell(self, quantity: int, price: Decimal) -> Decimal:
        q = ensure_positive_quantity(quantity)
        if q > self.quantity:
            raise InsufficientShares("Quantidade para venda excede posição disponível")
        p = ensure_positive_amount(price)
        # Realized PnL based on current avg cost
        realized = quantize_money((p - self.avg_cost) * q)
        # Reduce total cost by avg_cost * q
        reduce_cost = quantize_money(self.avg_cost * q)
        self.total_cost = quantize_money(self.total_cost - reduce_cost)
        self.quantity -= q
        if self.quantity == 0:
            self.avg_cost = Decimal("0.00")
            self.total_cost = Decimal("0.00")
        else:
            # Keep avg_cost consistent from remaining total_cost
            self.avg_cost = quantize_money(self.total_cost / Decimal(self.quantity))
        return realized

    def market_value(self, price: Decimal) -> Decimal:
        p = ensure_positive_amount(price)
        return quantize_money(p * self.quantity)

    def unrealized_pnl(self, price: Decimal) -> Decimal:
        p = ensure_positive_amount(price)
        return quantize_money((p - self.avg_cost) * self.quantity)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "avg_cost": str(self.avg_cost),
            "total_cost": str(self.total_cost),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Position":
        symbol = normalize_symbol(data.get("symbol", ""))
        quantity = int(data.get("quantity", 0))
        avg_cost = _to_decimal(data.get("avg_cost", "0.00"))
        total_cost = _to_decimal(data.get("total_cost", "0.00"))
        return cls(symbol=symbol, quantity=quantity, avg_cost=avg_cost, total_cost=total_cost)

@dataclass
class PnLBreakdown:
    cash: Decimal
    holdings_value: Decimal
    equity: Decimal
    contributions: Decimal
    withdrawals: Decimal
    net_contributions: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_pnl: Decimal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cash": str(self.cash),
            "holdings_value": str(self.holdings_value),
            "equity": str(self.equity),
            "contributions": str(self.contributions),
            "withdrawals": str(self.withdrawals),
            "net_contributions": str(self.net_contributions),
            "realized_pnl": str(self.realized_pnl),
            "unrealized_pnl": str(self.unrealized_pnl),
            "total_pnl": str(self.total_pnl),
        }

# ==========================
# Função de preço
# ==========================

def get_share_price(symbol: str) -> Decimal:
    sym = normalize_symbol(symbol)
    price = DEFAULT_PRICES.get(sym)
    if price is None:
        raise PriceUnavailable(f"Preço indisponível para símbolo: {sym}")
    return quantize_money(price)

# ==========================
# Classe Principal: Account
# ==========================

class Account:
    def __init__(
        self,
        account_id: str,
        user_name: Optional[str] = None,
        base_currency: str = "USD",
        price_fetcher: Optional[PriceFetcher] = None,
        now_provider: Optional[NowProvider] = None,
    ) -> None:
        if not isinstance(account_id, str) or not account_id.strip():
            raise InvalidOperation("account_id inválido")
        self.account_id: str = account_id.strip()
        self.user_name: Optional[str] = user_name
        self.base_currency: str = base_currency
        self._cash: Decimal = Decimal("0.00")
        self._positions: Dict[str, Position] = {}
        self._transactions: List[Transaction] = []
        self._contributions: Decimal = Decimal("0.00")
        self._withdrawals: Decimal = Decimal("0.00")
        self._realized_pnl: Decimal = Decimal("0.00")
        self._initial_deposit: Optional[Decimal] = None
        self._price_fetcher: PriceFetcher = price_fetcher or get_share_price
        self._now_provider: NowProvider = now_provider or (lambda: datetime.now(timezone.utc))

    # -------------
    # Internals
    # -------------
    def _now(self) -> datetime:
        dt = self._now_provider()
        if not isinstance(dt, datetime):
            raise InvalidOperation("now_provider retornou valor inválido")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def _record_transaction(
        self,
        ttype: TransactionType,
        amount: Optional[Decimal] = None,
        symbol: Optional[str] = None,
        quantity: Optional[int] = None,
        price: Optional[Decimal] = None,
        note: str = "",
    ) -> Transaction:
        tx = Transaction(
            id=str(uuid.uuid4()),
            timestamp=self._now(),
            type=ttype,
            symbol=symbol,
            quantity=quantity,
            price=quantize_money(price) if price is not None else None,
            amount=quantize_money(amount) if amount is not None else None,
            cash_after=quantize_money(self._cash),
            note=note or "",
        )
        self._transactions.append(tx)
        return tx

    # -------------
    # Operações de Caixa
    # -------------
    def deposit(self, amount: Decimal, note: str = "") -> Transaction:
        amt = ensure_positive_amount(amount)
        self._cash = quantize_money(self._cash + amt)
        self._contributions = quantize_money(self._contributions + amt)
        if self._initial_deposit is None:
            self._initial_deposit = amt
        return self._record_transaction(TransactionType.DEPOSIT, amount=amt, note=note)

    def withdraw(self, amount: Decimal, note: str = "") -> Transaction:
        amt = ensure_positive_amount(amount)
        if amt > self._cash:
            raise InsufficientFunds("Saque excede o saldo de caixa disponível")
        self._cash = quantize_money(self._cash - amt)
        self._withdrawals = quantize_money(self._withdrawals + amt)
        return self._record_transaction(TransactionType.WITHDRAW, amount=-amt, note=note)

    # -------------
    # Operações de Negociação
    # -------------
    def buy(self, symbol: str, quantity: int, note: str = "") -> Transaction:
        sym = normalize_symbol(symbol)
        q = ensure_positive_quantity(quantity)
        price = self._price_fetcher(sym)
        price = ensure_positive_amount(price)
        cost = quantize_money(price * q)
        if cost > self._cash:
            raise InsufficientFunds("Compra excede o saldo de caixa disponível")
        pos = self._positions.get(sym)
        if pos is None:
            pos = Position(symbol=sym)
            self._positions[sym] = pos
        pos.apply_buy(q, price)
        self._cash = quantize_money(self._cash - cost)
        return self._record_transaction(TransactionType.BUY, amount=-cost, symbol=sym, quantity=q, price=price, note=note)

    def sell(self, symbol: str, quantity: int, note: str = "") -> Transaction:
        sym = normalize_symbol(symbol)
        q = ensure_positive_quantity(quantity)
        pos = self._positions.get(sym)
        if pos is None or pos.quantity < q:
            raise InsufficientShares("Venda excede a quantidade de ações em carteira")
        price = self._price_fetcher(sym)
        price = ensure_positive_amount(price)
        proceeds = quantize_money(price * q)
        realized = pos.apply_sell(q, price)
        self._realized_pnl = quantize_money(self._realized_pnl + realized)
        if pos.quantity == 0:
            # limpar posição vazia
            self._positions.pop(sym, None)
        self._cash = quantize_money(self._cash + proceeds)
        return self._record_transaction(TransactionType.SELL, amount=proceeds, symbol=sym, quantity=q, price=price, note=note)

    # -------------
    # Consultas de Estado
    # -------------
    def get_cash_balance(self) -> Decimal:
        return quantize_money(self._cash)

    def get_position(self, symbol: str) -> Optional[Position]:
        sym = normalize_symbol(symbol)
        pos = self._positions.get(sym)
        if pos is None:
            return None
        # return a shallow copy to avoid external mutation
        return Position(symbol=pos.symbol, quantity=pos.quantity, avg_cost=pos.avg_cost, total_cost=pos.total_cost)

    def get_holdings(self) -> List[Position]:
        return [Position(symbol=p.symbol, quantity=p.quantity, avg_cost=p.avg_cost, total_cost=p.total_cost) for p in self._positions.values()]

    def get_holdings_value(self) -> Decimal:
        total = Decimal("0.00")
        for sym, pos in self._positions.items():
            price = self._price_fetcher(sym)
            price = ensure_positive_amount(price)
            total = quantize_money(total + quantize_money(price * pos.quantity))
        return quantize_money(total)

    def get_portfolio_value(self, include_cash: bool = True) -> Decimal:
        holdings_value = self.get_holdings_value()
        if include_cash:
            return quantize_money(self._cash + holdings_value)
        return holdings_value

    def get_pnl(self) -> Decimal:
        holdings_value = self.get_holdings_value()
        equity = quantize_money(self._cash + holdings_value)
        net_contributions = quantize_money(self._contributions - self._withdrawals)
        total_pnl = quantize_money(equity - net_contributions)
        return total_pnl

    def get_pnl_breakdown(self) -> PnLBreakdown:
        cash = quantize_money(self._cash)
        holdings_value = self.get_holdings_value()
        equity = quantize_money(cash + holdings_value)
        contributions = quantize_money(self._contributions)
        withdrawals = quantize_money(self._withdrawals)
        net_contributions = quantize_money(contributions - withdrawals)
        # unrealized per position
        unrealized = Decimal("0.00")
        for sym, pos in self._positions.items():
            price = self._price_fetcher(sym)
            price = ensure_positive_amount(price)
            unrealized = quantize_money(unrealized + pos.unrealized_pnl(price))
        realized = quantize_money(self._realized_pnl)
        total_pnl = quantize_money(equity - net_contributions)
        return PnLBreakdown(
            cash=cash,
            holdings_value=holdings_value,
            equity=equity,
            contributions=contributions,
            withdrawals=withdrawals,
            net_contributions=net_contributions,
            realized_pnl=realized,
            unrealized_pnl=unrealized,
            total_pnl=total_pnl,
        )

    def get_pnl_vs_initial_deposit(self) -> Decimal:
        # If no initial deposit, return standard PnL
        if self._initial_deposit is None:
            return self.get_pnl()
        holdings_value = self.get_holdings_value()
        equity = quantize_money(self._cash + holdings_value)
        return quantize_money(equity - self._initial_deposit)

    # -------------
    # Histórico de Transações
    # -------------
    def list_transactions(
        self,
        limit: Optional[int] = None,
        reverse: bool = False,
        type_filter: Optional[Set[TransactionType]] = None,
        symbol_filter: Optional[Set[str]] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Transaction]:
        items = list(self._transactions)

        # Normalize filters
        tf: Optional[Set[TransactionType]] = None
        if type_filter is not None:
            tf = set(type_filter)

        sf: Optional[Set[str]] = None
        if symbol_filter is not None:
            sf = {normalize_symbol(s) for s in symbol_filter}

        def in_range(ts: datetime) -> bool:
            s_ok = True
            e_ok = True
            if start is not None:
                s = start
                if s.tzinfo is None:
                    s = s.replace(tzinfo=timezone.utc)
                s_ok = ts >= s
            if end is not None:
                e = end
                if e.tzinfo is None:
                    e = e.replace(tzinfo=timezone.utc)
                e_ok = ts <= e
            return s_ok and e_ok

        filtered: List[Transaction] = []
        for tx in items:
            if tf is not None and tx.type not in tf:
                continue
            if sf is not None:
                if tx.symbol is None or normalize_symbol(tx.symbol) not in sf:
                    continue
            if not in_range(tx.timestamp):
                continue
            filtered.append(tx)

        filtered.sort(key=lambda t: t.timestamp, reverse=reverse)

        if limit is not None:
            return filtered[: max(0, int(limit))]
        return filtered

    # -------------
    # Serialização e Configuração
    # -------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "user_name": self.user_name,
            "base_currency": self.base_currency,
            "cash": str(self._cash),
            "contributions": str(self._contributions),
            "withdrawals": str(self._withdrawals),
            "realized_pnl": str(self._realized_pnl),
            "initial_deposit": str(self._initial_deposit) if self._initial_deposit is not None else None,
            "positions": [p.to_dict() for p in self._positions.values()],
            "transactions": [t.to_dict() for t in self._transactions],
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        price_fetcher: Optional[PriceFetcher] = None,
        now_provider: Optional[NowProvider] = None,
    ) -> "Account":
        acct = cls(
            account_id=str(data.get("account_id")),
            user_name=data.get("user_name"),
            base_currency=str(data.get("base_currency", "USD")),
            price_fetcher=price_fetcher,
            now_provider=now_provider,
        )
        acct._cash = _to_decimal(data.get("cash", "0.00"))
        acct._contributions = _to_decimal(data.get("contributions", "0.00"))
        acct._withdrawals = _to_decimal(data.get("withdrawals", "0.00"))
        acct._realized_pnl = _to_decimal(data.get("realized_pnl", "0.00"))
        init_dep = data.get("initial_deposit")
        acct._initial_deposit = _to_decimal(init_dep) if init_dep is not None else None
        acct._positions = {}
        for p in data.get("positions", []):
            pos = Position.from_dict(p)
            if pos.quantity > 0:
                acct._positions[pos.symbol] = pos
        acct._transactions = [Transaction.from_dict(t) for t in data.get("transactions", [])]
        return acct

    def set_price_fetcher(self, price_fetcher: PriceFetcher) -> None:
        if not callable(price_fetcher):
            raise InvalidOperation("price_fetcher deve ser chamável")
        self._price_fetcher = price_fetcher


# -----------------
# Quick self-test
# -----------------
if __name__ == "__main__":
    acc = Account(account_id="acc-1", user_name="Alice")
    acc.deposit(Decimal("1000"), note="initial")
    print("Cash after deposit:", acc.get_cash_balance())
    acc.buy("AAPL", 3)
    print("Cash after buying 3 AAPL:", acc.get_cash_balance())
    acc.buy("TSLA", 1)
    print("Cash after buying 1 TSLA:", acc.get_cash_balance())
    acc.sell("AAPL", 1)
    print("Cash after selling 1 AAPL:", acc.get_cash_balance())
    print("Holdings value:", acc.get_holdings_value())
    print("Portfolio value:", acc.get_portfolio_value())
    print("PnL:", acc.get_pnl())
    pnlb = acc.get_pnl_breakdown()
    print("PnL Breakdown:", pnlb.to_dict())
    # Serialization round trip
    data = acc.to_dict()
    acc2 = Account.from_dict(data)
    print("Roundtrip portfolio value:", acc2.get_portfolio_value())
    print("Transactions count:", len(acc2.list_transactions()))
