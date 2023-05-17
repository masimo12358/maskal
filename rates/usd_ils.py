from bisect import bisect, bisect_left, bisect_right
import csv
from datetime import datetime
from date_utils import safe_date
from operator import attrgetter
import requests
import re

# https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/RER_USD_ILS?format=csv&startperiod=2022-01-01&endperiod=2022-12-31
# https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/?c%5BDATA_TYPE%5D=OF00&startperiod=2008-01-01&endperiod=2008-01-02&format=csv

class UsdToIlsRatesProvider:

    def __init__(self, year: int):
        self.year = year
        self.rates = UsdToIlsRatesProvider.get_dollar_to_shekel_rates_for_year(year)
        # for rate in self.rates:
        #     print(rate)

    @classmethod
    def get_dollar_to_shekel_rates_for_year(cls, year: int) -> { datetime.date:float }:
        url = f"https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/RER_USD_ILS?format=csv&startperiod={year}-01-01&endperiod={year}-12-31"
        response = requests.get(url)
        reader = csv.reader(response.content.decode("utf-8").splitlines())
        rates = []
        for row in reader:
            try:
                rates.append([safe_date(row[12]).toordinal(), float(row[13])])
            except (ValueError, AttributeError):
                pass
        return rates

    def get_rate(self, date: datetime.date) -> float:
        by_year = attrgetter('released')
        keys = [r[0] for r in self.rates]
        position = bisect_left(keys, date.toordinal())
        return self.rates[position][1]
