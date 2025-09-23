import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from accounts import (
    Account,
    Position,
    Transaction,
    TransactionType,
    quantize_money,
    ensure_positive_amount,
    ensure_positive_quantity,
    normalize_symbol,
    get_share_price,
    PriceUnavailable,
    InvalidAmount,
    InvalidQuantity,
    InsufficientFunds,
    InsufficientShares,
    InvalidOperation,
    _to_decimal,
)


def make_now_provider(start: datetime = None):
    if start is None:
        start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    counter = {"i": -1}

    def _now():
        counter["i"] += 1
        return start + timedelta(seconds=counter["i"])

    return _now


def make_naive_now_provider(start: datetime = None):
    if start is None:
        start = datetime(2024, 1, 1, 12, 0, 0)  # naive
    counter = {"i": -1}

    def _now():
        counter["i"] += 1
        return start + timedelta(seconds=counter["i"])  # naive

    return _now


def make_price_fetcher(prices: dict):
    def _pf(sym: str) -> Decimal:
        sym = sym.upper()
        if sym not in prices:
            raise PriceUnavailable(f"Preço indisponível para símbolo: {sym}")
        return Decimal(str(prices[sym]))

    return _pf


# -----------------------
# Utility functions tests
# -----------------------

def test_quantize_money_round_half_even():
    assert quantize_money(Decimal("0.005")) == Decimal("0.00")
    assert quantize_money(Decimal("0.015")) == Decimal("0.02")


def test__to_decimal_and_ensure_positive_amount_and_quantity():
    # _to_decimal valid and invalid
    assert _to_decimal(5) == Decimal("5")
    assert _to_decimal("3.14") == Decimal("3.14")
    with pytest.raises(InvalidAmount):
        _to_decimal("abc")

    # ensure_positive_amount
    assert ensure_positive_amount(Decimal("1.234")) == Decimal("1.23")
    with pytest.raises(InvalidAmount):
        ensure_positive_amount(0)
    with pytest.raises(InvalidAmount):
        ensure_positive_amount(-1)

    # ensure_positive_quantity
    assert ensure_positive_quantity(3) == 3
    for bad in (0, -1, 1.5, "2"):
        with pytest.raises(InvalidQuantity):
            ensure_positive_quantity(bad)  # type: ignore[arg-type]
    # bool should be rejected even though it's an int subclass
    with pytest.raises(InvalidQuantity):
        ensure_positive_quantity(True)  # type: ignore[arg-type]
    with pytest.raises(InvalidQuantity):
        ensure_positive_quantity(False)  # type: ignore[arg-type]


def test_normalize_symbol():
    assert normalize_symbol(" aapl ") == "AAPL"
    with pytest.raises(InvalidOperation):
        normalize_symbol(123)  # type: ignore[arg-type]
    with pytest.raises(InvalidOperation):
        normalize_symbol("   ")


# -----------------------
# Price function tests
# -----------------------

def test_get_share_price_default_and_error():
    p = get_share_price("aapl")
    assert p == Decimal("190.00")
    with pytest.raises(PriceUnavailable):
        get_share_price("unknown")


# -----------------------
# Account cash operations
# -----------------------

def test_deposit_and_withdraw_updates_balances_and_transactions():
    now = make_now_provider()
    acc = Account("acc-1", now_provider=now)

    tx1 = acc.deposit(Decimal("1000.00"), note="init")
    assert acc.get_cash_balance() == Decimal("1000.00")
    assert tx1.type == TransactionType.DEPOSIT
    assert tx1.amount == Decimal("1000.00")
    assert tx1.cash_after == Decimal("1000.00")
    assert acc._initial_deposit == Decimal("1000.00")
    assert tx1.timestamp.tzinfo is not None

    tx2 = acc.deposit(Decimal("200"), note="topup")
    assert acc.get_cash_balance() == Decimal("1200.00")
    assert tx2.amount == Decimal("200.00")
    assert acc._initial_deposit == Decimal("1000.00")  # unchanged

    tx3 = acc.withdraw(Decimal("150.00"), note="wd")
    assert acc.get_cash_balance() == Decimal("1050.00")
    assert tx3.type == TransactionType.WITHDRAW
    assert tx3.amount == Decimal("-150.00")
    assert tx3.cash_after == Decimal("1050.00")

    # totals
    assert acc._contributions == Decimal("1200.00")
    assert acc._withdrawals == Decimal("150.00")


def test_withdraw_insufficient_and_now_provider_naive_timezone_conversion():
    now = make_naive_now_provider()
    acc = Account("acc-2", now_provider=now)
    acc.deposit(100)
    # timestamp should be made tz-aware (UTC)
    assert acc.list_transactions()[0].timestamp.tzinfo is not None
    with pytest.raises(InsufficientFunds):
        acc.withdraw(Decimal("200"))


# -----------------------
# Trading operations
# -----------------------

def test_buy_and_sell_flow_with_realized_and_unrealized_pnl():
    prices = {"AAPL": Decimal("100")}
    pf = make_price_fetcher(prices)
    now = make_now_provider()
    acc = Account("acc-3", price_fetcher=pf, now_provider=now)

    acc.deposit(Decimal("1000"))
    txb = acc.buy("AAPL", 5)
    assert txb.type == TransactionType.BUY
    assert txb.amount == Decimal("-500.00")
    assert acc.get_cash_balance() == Decimal("500.00")

    pos = acc.get_position("AAPL")
    assert pos is not None
    assert pos.quantity == 5
    assert pos.avg_cost == Decimal("100.00")
    assert pos.total_cost == Decimal("500.00")

    # Pump price to 110
    prices["AAPL"] = Decimal("110")
    hv = acc.get_holdings_value()
    assert hv == Decimal("550.00")
    assert acc.get_portfolio_value() == Decimal("1050.00")
    assert acc.get_pnl() == Decimal("50.00")

    pnlb = acc.get_pnl_breakdown()
    assert pnlb.realized_pnl == Decimal("0.00")
    assert pnlb.unrealized_pnl == Decimal("50.00")
    assert pnlb.total_pnl == Decimal("50.00")

    # Sell 2 at 110
    txs = acc.sell("AAPL", 2)
    assert txs.type == TransactionType.SELL
    assert txs.amount == Decimal("220.00")
    assert acc.get_cash_balance() == Decimal("720.00")

    pos2 = acc.get_position("AAPL")
    assert pos2 is not None
    assert pos2.quantity == 3
    assert pos2.avg_cost == Decimal("100.00")
    assert pos2.total_cost == Decimal("300.00")

    pnlb2 = acc.get_pnl_breakdown()
    assert pnlb2.realized_pnl == Decimal("20.00")
    assert pnlb2.unrealized_pnl == Decimal("30.00")
    assert pnlb2.total_pnl == Decimal("50.00")


def test_buy_with_insufficient_funds_and_sell_without_shares():
    prices = {"AAPL": Decimal("50")}
    pf = make_price_fetcher(prices)
    acc = Account("acc-4", price_fetcher=pf, now_provider=make_now_provider())

    acc.deposit(Decimal("40"))
    with pytest.raises(InsufficientFunds):
        acc.buy("AAPL", 1)

    with pytest.raises(InsufficientShares):
        acc.sell("AAPL", 1)

    acc.deposit(Decimal("100"))
    acc.buy("AAPL", 2)  # cost 100
    with pytest.raises(InsufficientShares):
        acc.sell("AAPL", 3)


def test_get_holdings_returns_copy_not_mutable():
    prices = {"AAPL": Decimal("100")}
    acc = Account("acc-5", price_fetcher=make_price_fetcher(prices), now_provider=make_now_provider())
    acc.deposit(Decimal("1000"))
    acc.buy("AAPL", 5)

    holdings = acc.get_holdings()
    assert len(holdings) == 1
    holdings[0].quantity = 0
    # internal should not change
    pos = acc.get_position("AAPL")
    assert pos is not None and pos.quantity == 5


# -----------------------
# Transactions listing & filters
# -----------------------

def test_list_transactions_filters_order_and_limit():
    prices = {"AAPL": Decimal("100"), "TSLA": Decimal("200")}
    pf = make_price_fetcher(prices)
    start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    now = make_now_provider(start)
    acc = Account("acc-6", price_fetcher=pf, now_provider=now)

    acc.deposit(1000)
    acc.buy("AAPL", 2)
    acc.buy("TSLA", 1)
    acc.sell("AAPL", 1)

    all_txs = acc.list_transactions()
    assert len(all_txs) == 4

    # Filter only BUY and symbol AAPL
    filtered = acc.list_transactions(type_filter={TransactionType.BUY}, symbol_filter={"aapl"})
    assert len(filtered) == 1
    assert filtered[0].type == TransactionType.BUY and filtered[0].symbol == "AAPL"

    # Time range: exclude the first deposit
    s = start + timedelta(seconds=1)  # after first tx
    e = start + timedelta(seconds=2)  # include up to second tx
    ranged = acc.list_transactions(start=s, end=e)
    assert [t.type for t in ranged] == [TransactionType.BUY, TransactionType.BUY]

    # Reverse order and limit
    rev = acc.list_transactions(reverse=True)
    assert rev[0].type == TransactionType.SELL
    limited = acc.list_transactions(limit=2)
    assert len(limited) == 2


# -----------------------
# Serialization round-trip
# -----------------------

def test_account_to_from_dict_roundtrip_and_timestamp_Z():
    prices = {"AAPL": Decimal("100")}
    pf = make_price_fetcher(prices)
    now = make_now_provider(datetime(2024, 1, 2, 9, 0, 0, tzinfo=timezone.utc))
    acc = Account("acc-7", price_fetcher=pf, now_provider=now)

    acc.deposit(500)
    acc.buy("AAPL", 3)
    acc.sell("AAPL", 1)

    data = acc.to_dict()
    # Transform timestamps to Z suffix
    for t in data["transactions"]:
        t["timestamp"] = t["timestamp"].replace("+00:00", "Z")

    acc2 = Account.from_dict(data, price_fetcher=pf, now_provider=now)
    assert acc2.get_portfolio_value() == acc.get_portfolio_value()
    assert acc2.get_cash_balance() == acc.get_cash_balance()
    assert len(acc2.get_holdings()) == len(acc.get_holdings())
    assert len(acc2.list_transactions()) == len(acc.list_transactions())

    # Ensure parsed timestamps are tz-aware
    for t in acc2.list_transactions():
        assert t.timestamp.tzinfo is not None


# -----------------------
# PnL vs initial deposit
# -----------------------

def test_pnl_vs_initial_deposit():
    prices = {"AAPL": Decimal("100")}
    pf = make_price_fetcher(prices)
    acc = Account("acc-8", price_fetcher=pf, now_provider=make_now_provider())

    # No deposit yet => same as get_pnl (0)
    assert acc.get_pnl_vs_initial_deposit() == acc.get_pnl() == Decimal("0.00")

    acc.deposit(1000)
    assert acc.get_pnl_vs_initial_deposit() == Decimal("0.00")

    acc.deposit(200)
    # Equity 1200, initial deposit 1000 => 200
    assert acc.get_pnl_vs_initial_deposit() == Decimal("200.00")

    acc.buy("AAPL", 2)  # spend 200, equity still 1200 at price 100
    assert acc.get_pnl_vs_initial_deposit() == Decimal("200.00")


# -----------------------
# Position class tests
# -----------------------

def test_position_apply_buy_sell_and_values():
    pos = Position(symbol="AAPL")
    pos.apply_buy(3, Decimal("10"))
    assert pos.quantity == 3
    assert pos.total_cost == Decimal("30.00")
    assert pos.avg_cost == Decimal("10.00")

    # Sell 1 at 12 => realized 2.00
    realized = pos.apply_sell(1, Decimal("12"))
    assert realized == Decimal("2.00")
    assert pos.quantity == 2
    assert pos.total_cost == Decimal("20.00")
    assert pos.avg_cost == Decimal("10.00")

    # Market value and unrealized at price 11
    assert pos.market_value(Decimal("11")) == Decimal("22.00")
    assert pos.unrealized_pnl(Decimal("11")) == Decimal("2.00")

    # Sell remaining 2 at 8 => realized -4.00, position reset
    realized2 = pos.apply_sell(2, Decimal("8"))
    assert realized2 == Decimal("-4.00")
    assert pos.quantity == 0
    assert pos.avg_cost == Decimal("0.00")
    assert pos.total_cost == Decimal("0.00")


# -----------------------
# Transaction serialization
# -----------------------

def test_transaction_to_from_dict_roundtrip_and_naive_input():
    ts_naive = datetime(2025, 1, 1, 0, 0, 0)  # naive
    data = {
        "id": "tx-1",
        "timestamp": ts_naive,
        "type": "DEPOSIT",
        "symbol": None,
        "quantity": None,
        "price": None,
        "amount": "10.00",
        "cash_after": "10.00",
        "note": "n",
    }
    tx = Transaction.from_dict(data)
    assert isinstance(tx.timestamp, datetime)
    assert tx.timestamp.tzinfo is not None  # made tz-aware
    d = tx.to_dict()
    assert d["type"] == "DEPOSIT"
    assert d["amount"] == "10.00"
    assert d["cash_after"] == "10.00"


# -----------------------
# set_price_fetcher validation
# -----------------------

def test_set_price_fetcher_validation_and_usage():
    acc = Account("acc-9", now_provider=make_now_provider())
    with pytest.raises(InvalidOperation):
        acc.set_price_fetcher(123)  # type: ignore[arg-type]

    def pf(sym: str) -> Decimal:
        return Decimal("1.00")

    acc.deposit(10)
    acc.set_price_fetcher(pf)
    acc.buy("AAPL", 5)
    # cost 5.00 => cash left 5.00
    assert acc.get_cash_balance() == Decimal("5.00")
