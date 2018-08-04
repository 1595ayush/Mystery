from bs4 import BeautifulSoup
import urllib.request
import json
import datetime
import os
import re

url_link = "http://www.moneycontrol.com/techmvc/html/earnings/earnings-calender.json"
header = "Stock,MeetingDate\n"
stock_codes = {}
earnings_file_name = "earnings-calender.json"


def get_earnings_json():
    print("Checking if Data is Present in File \"{name}\"".format(name=earnings_file_name))
    if os.path.isfile(earnings_file_name):
        print("File Found. Loading data from File")
        with open(earnings_file_name, "r") as fr:
            json_data = fr.read()
    else:
        print("File not Found. Downloading data from URL")
        with urllib.request.urlopen(url_link) as earnings_urlopen:
            json_data = earnings_urlopen.read().decode()
            with open(earnings_file_name, "w") as fw:
                fw.write(json_data)
    data = json.loads(json_data)
    return data
def get_result_date_string(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d %b %Y')
def get_stock_name(parser):
    return parser.find("div", {"class": "Ohidden"}).text
def load_stock_codes():
    moneycontrol_stock_codes_file = "codes.csv"
    if os.path.isfile(moneycontrol_stock_codes_file):
        with open(moneycontrol_stock_codes_file, "r") as fr:
            row = fr.readline().split(",")
            stock_codes[row[0]] = row[1].lower()
def save_stock_codes():
    moneycontrol_stock_codes_file = "codes.csv"
    with open(moneycontrol_stock_codes_file, "w") as fw:
        for key,value in stock_codes.items():
            fw.write(key + "," + value.lower() + "\n")
def get_stock_short_name(parser):
    href = parser.find("a")["href"]
    if href in stock_codes:
        short_name = stock_codes[href].lower()
    else:
        try:
            with urllib.request.urlopen(href) as urlopen:
                response = urlopen.read().decode()
                x = re.compile("/tech_charts/bse/his/.*csv")
                result = x.findall(response)[0].split(".")[0].split("/")[4]
            short_name = result
            stock_codes[href] = result.lower()
        except Exception as e:
            print(e)
            return None
    return short_name


def parse_prices(response, result_date):
    price_list = response.split("\n")
    line = ''
    count = -1

    for x in range(len(price_list) - 2, 0, -1):
        row = price_list[x].split(",")
        price_date = row[0]

        #if 0 <= count <= 5:
        #    count += 1
        #    close_price = row[4]
        #    line += price_date + "," + close_price + ","

        if result_date >= price_date:
            count = 0
            y = x
            break

    while 0 <= count <= 5 and y >= 0:
        row = price_list[y].split(",")
        price_date = row[0]

        count += 1
        close_price = row[4]
        line += price_date + "," + close_price + ","
        y = y - 1
    return line


def get_last_5_days_price(exchg, stock_name, result_date):
    price_file_name = "prices\\" + stock_name.lower() + ".csv"
    line = None

    if os.path.isfile(price_file_name):
        file_found = True
        with open(price_file_name, "r") as fr:
            response = fr.read()
    else:
        price_url = "http://www.moneycontrol.com/tech_charts/{exchange}/his/{name}.csv".format(exchange=exchg,
                                                                                           name=stock_name.lower())
        try:
            with urllib.request.urlopen(price_url) as urlopen:
                response = urlopen.read().decode()
                with open(price_file_name, "w") as fw:
                    fw.write(response)

            file_found = True
        except:
            file_found = False

    if file_found:
        line = parse_prices(response, result_date=result_date)
    return line


def get_earnings_csv():
    load_stock_codes()
    main_csv = "" + header
    earnings_data = get_earnings_json()

    for entry in earnings_data:

        soup = BeautifulSoup(entry['issue'], 'html.parser')

        result_date = get_result_date_string(entry['date'])
        stock = get_stock_name(soup)
        stock_short_name = get_stock_short_name(soup)
        today = datetime.datetime.today().strftime('%d %b %y')

        if result_date > today:
            if stock_short_name:
                line = get_last_5_days_price(stock_name=stock_short_name, exchg="nse", result_date=result_date)

                if not line:
                    line = get_last_5_days_price(stock_name=stock_short_name, exchg="bse", result_date=result_date)
                    if not line:
                        print("No price data found for " + stock + ":" + stock_short_name + " Ignoring the entry")
                if line:
                    print("Adding data for" + stock + " " + stock_short_name)
                    main_csv += stock + "," + result_date + "," + line + "\n"
                else:
                    main_csv += stock + "," + result_date + "\n"
                with open("abc.csv", "w") as m:
                    m.write(main_csv)
            else:
                print("Ignoring " + stock)
        else:
            print("Price not discovered for" + " " + stock + " " + result_date)
    save_stock_codes()


if __name__ == "__main__":
    get_earnings_csv()
