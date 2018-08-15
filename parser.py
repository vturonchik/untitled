import csv
from urllib import request
from datetime import datetime
import re
from multiprocessing import Pool
from bs4 import BeautifulSoup


def main(file):
    all_links = get_all_links()
    all_products = []
    with Pool(30) as p:
        all_products_1 = p.map(parse_product_page, all_links)
    for product in all_products_1:
        if product != []:
            all_products.extend(product)
    save_csv(all_products, file)


def get_all_category_page_links():
    page_count = get_page_count(get_html(BASE_URL))
    all_links = []
    for page in range(1, page_count + 1):
        all_links.append(BASE_URL + '?p={}'.format(page))
    return all_links


def get_all_links():
    category_links = get_all_category_page_links()
    all_links = []
    with Pool(10) as p:
        all_links_1 = p.map(get_links_page, category_links)
    for link in all_links_1:
        all_links.extend(link)
    return all_links


def get_html(url):
    response = request.urlopen(url)
    return response.read()


def get_links_page(url):                                       # Собрать все ссылки на товар на одной странице категории
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    goods_page = soup.find('div', class_='product_list')
    goods_links = []
    for good in goods_page.find_all('div', class_='ajax_block_product'):
        link = good.find('a').get('href')
        goods_links.append(link)
    return goods_links


def get_page_count(html):
    soup = BeautifulSoup(html, 'lxml')
    pagination = soup.find('ul', class_='pagination')
    return int(pagination.find_all('li')[-2].text)


def parse_product_page(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    title_search = soup.find('h1').text.strip()
    title_re = re.split('\n', title_search)[-1]
    img = soup.find('img', id='bigpic').get('src')
    price_and_weight = soup.find_all('ul', class_='attribute_labels_lists')
    all_products = []
    for pw in price_and_weight:
        price = pw.find('span', class_='attribute_price').text.strip()
        weight = pw.find('span', class_='attribute_name').text.strip()
        title = '{} - {}'.format(title_re, weight)
        all_products.append({
            'title': title,
            'price': price,
            'image': img})
    return all_products


def save_csv(products, path):
    with open(path, 'w', encoding='utf-16', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(('Title',
                         'Price',
                         'Image'))
        for product in products:
            writer.writerow((product['title'],
                             product['price'],
                             product['image']))


if __name__ == '__main__':
    BASE_URL = input('Enter url: ')
    FILE_NAME = '{}.csv'.format(input('File name (without .csv): '))
    start = datetime.now()
    main(FILE_NAME)
    end = datetime.now()
    print(end - start)
