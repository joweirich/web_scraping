"""
Query boliglaan kurs from various institutes
"""
import datetime
import requests
import scraping_tools as sct

urls = {'totalkredit':\
        'https://netbank.totalkredit.dk/netbank/showStockExchange.do',
        'nordea':\
        'https://bank.nordea.dk/privat/lan/bolig/raadgivning/nordea-kredit-laan-med-fast-rente.flex'
       }
xpaths = {'totalkredit': '//div[@class="box"]/table/tr/td/text()',
          'nordea': '//table[@class="zebra-striped-table"]//text()'}

institute = 'totalkredit'
url = urls.get(institute)
xpath = xpaths.get(institute)

html = requests.get(url)
content_list = sct.parse_content(html.content, xpath)
content_formatted = (sct.format_content(content_list, indices=slice(5*n, 5*(n+1)))
                     for n in range(3))

content_strings = [sct.num_list_to_str(l) for l in content_formatted]
today = datetime.datetime.today()
datestring = today.strftime('%Y-%m-%d')

with sct.PostgreSQLdb() as pgdb:
    query_existing = 'select * from Kurs'
    pgdb.query(query_existing)
    existing_data = pgdb.cursor.fetchall()
    if existing_data[-1][1] == today.date():
        print('Query has already be performed today')
    else:
        print('Appending todays data')
        last_entry_id = existing_data[-1][0]
        for idx, content_str in enumerate(content_strings):
            sql = f"insert into Kurs values({last_entry_id+idx+1},'{datestring}', {content_str})"
            pgdb.query(sql)

        pgdb.commit()
