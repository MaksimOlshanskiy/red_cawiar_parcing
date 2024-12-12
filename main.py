import requests
from bs4 import BeautifulSoup
import re
import datetime
import psycopg2

# URL страницы, которую вы хотите парсить
url = 'https://www.delikateska.ru/catalog/ikra-krasnaya/r/page/'  # замените на нужный URL
headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
shop_name = "delikateska.ru" # название магазина
titles_list = []
weight_list = []
prices_list = []

# Отправляем GET-запрос к странице
for page_number in range(1, 3):
    if page_number == 1:
        url = 'https://www.delikateska.ru/catalog/ikra-krasnaya'
    else:
        url = 'https://www.delikateska.ru/catalog/ikra-krasnaya/r/page/'+str(page_number)
    print(url)
    response = requests.get(url, headers=headers)
    src = response.text
    soup = BeautifulSoup(src, "lxml")
    titles = soup.find_all(class_="product-card-new__title")
    for i in titles:
        titles_list.append(i.text.strip())

    weights = soup.find_all(class_="product-card-new__measure")
    for i in weights:
        weight = int(re.sub("[^0-9]", "", i.text))
        if not weight:
            weight = 0
        if "кг" in str(i):
            weight *= 100
        print(f'Вес: {weight}, Тип данных: {type(weight)}')
        weight_list.append(weight)

    prices = soup.find_all(class_="product-card-new__price")
    for i in prices:
        i = re.sub("[^0-9]", "", i.text)
        prices_list.append(i)
    print(titles_list)


# with open("ikra.html", "w", encoding="utf-8-sig") as file:
#    file.write(src)

# with open("ikra.html", encoding="utf-8-sig") as file:
#    src = file.read()


result = []
current_date = datetime.date.today().isoformat()

for i in range(len(prices_list)):
    result.append([shop_name, titles_list[i], weight_list[i], prices_list[i], current_date])

print(result)

try:
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect('postgresql://postgres:1234@localhost:5433/postgres')
    print('OK')

except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')

for i in result:
    cursor = conn.cursor()
    cursor.execute('INSERT INTO red_caviar VALUES (%s, %s, %s, %s, %s)', i)

conn.commit()
cursor.close()  # закрываем курсор
conn.close()  # закрываем соединение

