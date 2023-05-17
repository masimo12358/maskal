import csv
import re
from datetime import datetime
from date_utils import extract_first_date
import getopt
import pandas as pd
from rates.usd_ils import UsdToIlsRatesProvider
import sys
from trade import Trade

from date_utils import safe_date

def print_usage_and_exit():
    print(f"Usage: {sys.argv[0]} -i <input report file> -t <report type> -o <output file> -n <output type>")
    print(f"  -t <report type> - can be csv or pdf")
    print(f"  -n <output type> - describe the format of the ouput type, currently the script supports:")
    print(f"    csv1425: generate nispach 1425 in mas hachnasa format ")
    print()
    print(f"  Example:")
    print("  python ib_yearly_to_mas.py -i U1290723_U1290723_20220103_20221230_AS_1275236_0a68b1481f4ded1f86bdb36e60b4b0c0.csv -t csv -o mas1425.csv -n csv1425")
    sys.exit()

def check_args():
    input_file_path = ""
    input_file_type = ""
    output_file_path = ""
    output_file_type = ""
    print(sys.argv)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:t:o:n:", ["input-file=", "input-type=", "output-file=", "output-type="])
    except getopt.GetoptError:
        print_usage_and_exit()
    for opt, arg in opts:
        if opt == '-h':
            print_usage_and_exit()
        elif opt in ("-f", "--input-file"):
            input_file_path = arg
        elif opt in ("-t", "--input-type"):
            input_file_type = arg
        elif opt in ("-o", "--output-file"):
            output_file_path = arg
        elif opt in ("-n", "--output-type"):
            output_file_type = arg
        # elif opt in ("--dry-run"):
        #     dry_run = True
        # elif opt in ("--no-delete"):
        #     no_delete = True
    if input_file_path == '' or input_file_type == '' or output_file_path == '' or output_file_type == '':
        print_usage_and_exit()
    else:
        return(input_file_path, input_file_type.lower(), output_file_path, output_file_type.lower())

def find_first_row(rows: [[str]], starts_with: [str], level: int = 0) -> [str]:
    filtered = [row for row in rows if row[level] == starts_with[0]]
    starts_with.pop(0)
    level += 1
    if len(starts_with) > 0:
        return find_first_row(filtered, starts_with, level)
    else:
        return filtered[0]


def get_report_year(rows: [[str]]) -> int:
    for row in rows:
        if row[0] == "Trades" and row[1] == "Data":
            single_row = ','.join(row)
            return extract_first_date(single_row).year


def process_csv_report(file_path: str):
    output = pd.DataFrame(columns=["row", "symbol", "open date", "open nominal", "close date", "close nominal",
                                   "Realized Pnl", "Calc Pnl", "short", "open rate", "close rate"])
    with open(input_file_path, "r") as input:
        reader = csv.reader(input)
        rows = []
        for row in reader:
            rows.append(row)
        input.close()  # to change file access modes
        print(rows)
        print()
        #print(find_first_row(rows, ["Dividends", "Header"]))
        trades_header_row = find_first_row(rows, ["Trades", "Header"])
        # symbol_index = trades_header_row.index("Symbol")
        # date_index = trades_header_row.index("Date/Time")
        # quantity_index = trades_header_row.index("Quantity")
        # price_index = trades_header_row.index("T. Price")
        # amount_index = trades_header_row.index("Proceeds")
        # pnl_index = trades_header_row.index("Realized P/L")
        Trade.set_descriptor(trades_header_row)
        rates_provider = UsdToIlsRatesProvider(get_report_year(rows))
        # print(rates_provider.rates)
        #print(rates_provider.get_rate(datetime(2022, 3, 1)))
        #print(rates_provider.get_rate(datetime(2022, 3, 2)))
        #print(rates_provider.get_rate(datetime(2022, 3, 3)))
        #print(rates_provider.get_rate(datetime(2022, 3, 4)))

        row_number = 1
        for row in rows:
            if row[0] == "Trades" and row[1] == "Data":
                if row[2] == "Trade":
                    # trade_date = safe_date(row[date_index])
                    # symbol = row[symbol_index]
                    # trade_quantity = row[quantity_index]
                    # price = row[price_index]
                    # amount = row[amount_index]
                    # pnl = row[pnl_index]
                    closing_trade = Trade(row)
                elif row[2] == "ClosedLot":
                    opening_trade = Trade(row)
                    open_rate = rates_provider.get_rate(opening_trade.date)
                    close_rate = rates_provider.get_rate(closing_trade.date)
                    #print("short") if opening_trade.is_short() else print("long")
                    #print("lot is closed") if abs(opening_trade.quantity) == abs(closing_trade.quantity) else print("lot quantity mismatch")
                    calculated_pnl = -opening_trade.quantity * opening_trade.price - closing_trade.quantity * closing_trade.price - 1.3
                    if opening_trade.is_short():
                        line = [row_number, opening_trade.symbol, closing_trade.date, abs(closing_trade.amount),
                                opening_trade.date, abs(opening_trade.basis), closing_trade.pnl, calculated_pnl,
                                opening_trade.is_short(), close_rate, open_rate]
                    else:
                        line = [row_number, opening_trade.symbol, opening_trade.date, abs(closing_trade.basis),
                                closing_trade.date, abs(closing_trade.amount), closing_trade.pnl, calculated_pnl,
                                opening_trade.is_short(), open_rate, close_rate]
                    #print(f"#{row_number}:{opening_trade}")
                    #print(f"#{row_number}:{closing_trade}")
                    output.loc[line[0], :] = line
                    row_number += 1
        output["rate change"] = output["close rate"] / output["open rate"]
        output.sort_values(by=['open date'], inplace=True)

        print(output)
        output.to_csv("output.csv")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    input_file_path, input_file_type, output_file_path, output_file_type = check_args()
    if "csv" == input_file_type:
        process_csv_report(input_file_path)
    elif "pdf" == input_file_type:
        process_csv_report(input_file_path)
    else:
        print(f"Error: input report format {input_file_type} is not supported")




