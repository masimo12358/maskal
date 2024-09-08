from datetime import datetime
from date_utils import safe_date
from rates.usd_ils import UsdToIlsRatesProvider


class Trade:
    symbol_index: int = 0
    date_index: int = 0
    quantity_index: int = 0
    price_index: int = 0
    amount_index: int = 0
    basis_index: int = 0
    pnl_index: int = 0
    code_index: int = 0
    commission_index = 0

    def __init__(self, date: datetime.date, symbol: str, quantity: float, price: float, amount: float = 0,
                 basis: float = 0, pnl: float = 0, code:str = "", commission: float = 0):
        self.date = date
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.amount = amount
        self.basis = basis
        self.pnl = pnl
        self.code = code
        self.commission = commission

    def __init__(self, row: [str]):
        self.date = safe_date(row[Trade.date_index])
        self.symbol = row[Trade.symbol_index]
        self.quantity = int(row[Trade.quantity_index])
        self.price = float(row[Trade.price_index])
        self.amount = float(row[Trade.amount_index]) if row[Trade.amount_index] != "" else 0
        self.basis = float(row[Trade.basis_index])
        self.pnl = float(row[Trade.pnl_index])
        self.code = row[Trade.code_index]
        self.commission = float(row[Trade.commission_index]) if row[Trade.commission_index] else 0.0

    def __str__(self):
        return f"{self.date} {self.symbol} {self.quantity} {self.price} {self.amount} > {self.basis} - {self.pnl} [{self.code} > {self.commission}]"

    @classmethod
    def set_descriptor(cls, descriptor: [str]):
        Trade.symbol_index = descriptor.index("Symbol")
        Trade.date_index = descriptor.index("Date/Time")
        Trade.quantity_index = descriptor.index("Quantity")
        Trade.price_index = descriptor.index("T. Price")
        Trade.amount_index = descriptor.index("Proceeds")
        Trade.basis_index = descriptor.index("Basis")
        Trade.pnl_index = descriptor.index("Realized P/L")
        Trade.code_index = descriptor.index("Code")
        Trade.commission_index = descriptor.index("Comm/Fee")

    def is_short(self) -> bool:
        return self.quantity < 0

    def is_open(self) -> bool:
        return "O" in self.code

    def is_close(self) -> bool:
        return "C" in self.code

    def is_partial(self) -> bool:
        return "P" in self.code


class LotTracker:
    symbol: str
    open_trades: list[Trade]
    close_trades: list[Trade]
    closed_lot: Trade

    def __init__(self, rates_provider: UsdToIlsRatesProvider):
        self.rates_provider = rates_provider
        self.reset()

    def reset(self):
        self.symbol = ""
        self.open_trades = []
        self.close_trades = []
        self.closed_lot = None

    def reset_partial_close(self):
        self.close_trades = []
        self.closed_lot = None

    def add_trade(self, trade: Trade):
        if trade.symbol != self.symbol:
            print('-' * 50)
            print(f"New symbol {trade.symbol} - resetting")
            self.reset()
            self.symbol = trade.symbol
        print(f"Added trade: {trade}")
        if trade.is_open():
            self.open_trades.append(trade)
        elif trade.is_close():
            self.close_trades.append(trade)

    def add_lot(self, lot: Trade):
        print(f"Added lot: {lot}")
        self.closed_lot = lot

    # def add_open_trade(self, trade: Trade):
    #     if trade.symbol != self.symbol:
    #         self.reset()
    #         self.symbol = trade.symbol
    #         self.open_date = trade.date
    #         self.open_quantity = trade.quantity
    #         self.open_price = trade.price
    #         self.open_rate = self.rates_provider.get_rate(trade.date)
    #     else:
    #         if self.open_date != trade.date:
    #             print(f"fWarning: trade open date {trade.date} not as previous open date {self.open_date}")
    #         self.open_date = trade.date
    #         self.open_quantity += trade.quantity
    #     self.open_trades.append(trade)
    #     self.pnl -= trade.quantity * trade.price + trade.commission
    #     self.commissions += trade.commission
    #
    # def add_close_trade(self, trade: Trade):
    #     self.close_trade = trade
    #     self.close_rate = self.rates_provider.get_rate(trade.date)
    #     self.commissions += trade.commission
    #     self.pnl -= trade.quantity * trade.price + trade.commission
    #     self.symbol = trade.symbol
    #
    # def calculate_pnl(self) -> float:
    #     open = 0.0
    #     commission = 0.0
    #     for trade in self.open_trades:
    #         open += trade.quantity * trade.price
    #         commission += trade.commission
    #     close = self.close_trade.quantity * self.close_trade.price
    #     commission += self.close_trade.commission
    #     # buy quantity is negative, commissions are negative
    #     return commission - close - open
    #     # else:
    #     #     return commission + close + open
    #
    # def __str__(self):
    #     return f"transaction: {self.symbol} {self.pnl} {self.open_rate} {self.close_rate} [{self.commissions}]"

    def calc(self):
        print("Calculating closed lot properties:")
        print("*" * 50)
        print(f"Open date: {self.closed_lot.date}")
        print(f"Open basis: {self.closed_lot.basis}")
        
        print(f"Close proceed: {self.close_trades[0].amount}")
        print(f"Close comm: {self.close_trades[0].commission}")
        print(f"pnl: {self.closed_lot.pnl}")
        print("*" * 50)


        print("Calculating closed lot properties 1:")
        open_dates = set()
        open_prices = set()
        open_quantity = 0.0
        open_value = 0.0
        for trade in self.open_trades:
            open_dates.add(trade.date)
            open_quantity += trade.quantity
            open_value += trade.amount + trade.commission
        open_date = open_dates.pop()
        open_rate = self.rates_provider.get_rate(open_date)
        open_value_ils = open_value * open_rate
        # print(f"Open dates: {open_dates} prices {open_prices} quantity {open_quantity}")
        close_dates = set()
        close_prices = set()
        close_quantity = 0.0
        close_value = 0.0
        for trade in self.close_trades:
            close_dates.add(trade.date)
            close_prices.add(trade.price)
            close_quantity += trade.quantity
            close_value += trade.amount + trade.commission
        close_date = close_dates.pop()
        # assert close_date == self.closed_lot.date
        print(f"close date {close_date} lot date {self.closed_lot.date}")
        close_rate = self.rates_provider.get_rate(close_date)
        close_value_ils = close_value * close_rate
        # print(f"Close dates: {close_dates} prices {close_prices} quantity {close_quantity}")
        self.fully_closed_lot = abs(close_quantity) == abs(open_quantity) and abs(self.closed_lot.quantity) == abs(open_quantity)
        if self.fully_closed_lot:
            print(f"lot fully closed with quantity {self.closed_lot.quantity}")
        if self.closed_lot.quantity < 0:
            print(f"lot is short trade")
            madad_ratio = open_rate / close_rate
            close_value_ils_metoam = close_value_ils * madad_ratio
            print("=" * 20)
            print(f"  symbol: {self.symbol}")
            print(f"  sell value: {abs(open_value)}$")
            print(f"  purchase date: {close_date}")
            print(f"  cost: {abs(close_value)}$")
            print(f"  original_price {abs(close_value_ils)}NIS")
            print(f"  $ on purchase: {close_rate}")
            print(f"  $ on sell: {open_rate}")
            print(f"  $ ratio: {madad_ratio}")
            print(f"  price metoam: {abs(close_value_ils_metoam)}NIS")
            print(f"  sell date: {open_date}")
            print(f"  tmura: {abs(open_value_ils)}")
            pnl1 = abs(open_value) - abs(close_value)
            print(f"pnl1 $ = {pnl1}")
            pnl2 = abs(open_value_ils) - abs(close_value_ils)
            print(f"pnl2 NIS = {pnl2}")

            print("=" * 20)
        else:
            print(f"lot is long trade")
            madad_ratio = close_rate / open_rate
            open_value_ils_metoam = open_value_ils * madad_ratio
            print("=" * 20)
            print(f"  symbol: {self.symbol}")
            print(f"  sell value: {abs(close_value)}$")
            print(f"  purchase date: {open_date}")
            print(f"  cost: {abs(open_value)}$")
            print(f"  original_price {abs(open_value_ils)}NIS")
            print(f"  $ on purchase: {open_rate}")
            print(f"  $ on sell: {close_rate}")
            print(f"  $ ratio: {madad_ratio}")
            print(f"  price metoam: {abs(open_value_ils_metoam)}NIS")
            print(f"  sell date: {close_date}")
            print(f"  tmura: {abs(close_value_ils)}")
            pnl1 = abs(close_value) - abs(open_value)
            print(f"pnl1 $ = {pnl1}")
            pnl2 = abs(close_value_ils) - abs(open_value_ils)
            print(f"pnl2 NIS = {pnl2}")

            print("=" * 20)

        if self.fully_closed_lot:
            print("fully closed lot - resetting")
            self.reset()
        else:
            print("partially closed lot - resetting partially")
            self.reset_partial_close()
