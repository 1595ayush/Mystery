from bs4 import BeautifulSoup
import urllib.request, json
import datetime

url_link = "http://www.moneycontrol.com/techmvc/html/earnings/earnings-calender.json"
header = "Stock,MeetingDate\n"
main_csv = "" + header


def get_earnings_json():
    with urllib.request.urlopen(url_link) as earnings_urlopen:
        data = json.loads(earnings_urlopen.read().decode())
        print(data)
        return data


earnings_data = get_earnings_json()

for entry in earnings_data:

    soup = BeautifulSoup(entry['issue'], 'html.parser')

    result_date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%d %b %Y')
    stock = soup.find("div", {"class": "Ohidden"}).text
    href_link = soup.find("a")["href"]
    stock_short_name = href_link.split('/')[7]

    if stock_short_name == 'KMB':
        stock_short_name = "kmf"
    exchange = "bse"
    price_url = "http://www.moneycontrol.com/tech_charts/{exchange}/his/{name}.csv".format(exchange=exchange, name=stock_short_name.lower())

    if stock_short_name == "TCS":
        with urllib.request.urlopen(price_url) as price_urlopen:
            line = ""
            count = -1

            price_data_list = price_urlopen.read().decode().split("\n")

            for x in range(len(price_data_list) - 1, 0, -1):

                row = price_data_list[x].split(",")

                price_date = row[0]

                if 0 <= count <= 5:
                    count += 1
                    close_price = row[4]
                    line += price_date + "," + close_price + ","

                if result_date == price_date:
                    count = 0

            main_csv += stock + "," + result_date + "," + line + "\n"
    with open("abc.csv", "w") as m:
        m.write(main_csv)

    #print(href_details)
    #print(stock)
    #print(result_date)
