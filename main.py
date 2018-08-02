from bs4 import BeautifulSoup
import urllib.request, json
import datetime

url_link = "http://www.moneycontrol.com/techmvc/html/earnings/earnings-calender.json"

with urllib.request.urlopen(url_link) as url:
    data = json.loads(url.read().decode())
    print(data)
main_csv = "Stock,MeetingDate\n"
for entry in data:
    result_date = entry['date']
    compare_date = datetime.datetime.strptime(result_date, '%Y-%m-%d').strftime('%d %b %Y')
    soup = BeautifulSoup(entry['issue'])
    stock = soup.find("div", {"class": "Ohidden"}).text
    stock_short = soup.find("a")["href"]
    href_details = stock_short.split('/')[7]
    if(href_details == 'KMB'):
        href_details  = "kmf"
    link = "http://www.moneycontrol.com/tech_charts/bse/his/" + href_details.lower() + ".csv"
    #print(link)

    if(href_details == "TCS"):
        with urllib.request.urlopen(link) as u:
            csv = ""
            print(u)
            data1 = u.read().decode().split("\n")
            count = -1;
            for x in range(len(data1) - 1, 0, -1):
                row = data1[x].split(",")
                rec_date = row[0]
                if (count >= 0 and count <= 5):
                    count += 1
                    csv += rec_date + "," + row[4] + ","
                if(compare_date == rec_date):
                    count = 0
                close_price = row[4]
            main_csv += stock + "," + compare_date + "," + csv + "\n"
    with open("abc.csv", "w") as m:
        m.write(main_csv)
    print(href_details)
    print(stock)
    print(result_date)