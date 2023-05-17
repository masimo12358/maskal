from datetime import datetime
from date_utils import safe_date


class Trade:
    symbol_index: int = 0
    date_index: int = 0
    quantity_index: int = 0
    price_index: int = 0
    amount_index: int = 0
    basis_index: int = 0
    pnl_index: int = 0

    def __init__(self, date: datetime.date, symbol: str, quantity: float, price: float, amount: float = 0,
                 basis: float = 0, pnl: float = 0):
        self.date = date
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.amount = amount
        self.basis = basis
        self.pnl = pnl

    def __init__(self, row: [str]):
        self.date = safe_date(row[Trade.date_index])
        self.symbol = row[Trade.symbol_index]
        self.quantity = int(row[Trade.quantity_index])
        self.price = float(row[Trade.price_index])
        self.amount = float(row[Trade.amount_index]) if row[Trade.amount_index] != "" else 0
        self.basis = float(row[Trade.basis_index])
        self.pnl = float(row[Trade.pnl_index])

    def __str__(self):
        return f"{self.date} {self.symbol} {self.quantity} {self.price} {self.amount} > {self.basis} - {self.pnl}"

    @classmethod
    def set_descriptor(cls, descriptor: [str]):
        Trade.symbol_index = descriptor.index("Symbol")
        Trade.date_index = descriptor.index("Date/Time")
        Trade.quantity_index = descriptor.index("Quantity")
        Trade.price_index = descriptor.index("T. Price")
        Trade.amount_index = descriptor.index("Proceeds")
        Trade.basis_index = descriptor.index("Basis")
        Trade.pnl_index = descriptor.index("Realized P/L")

    def is_short(self) -> bool:
        return self.quantity < 0