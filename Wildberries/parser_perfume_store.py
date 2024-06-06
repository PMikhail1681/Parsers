import requests
import csv

from models import Items, Feedback

class ParseWB:
    def __init__(self, url: str):
        self.seller_id = self.__get_seller_id(url)

    def __get_seller_id(self, url):        # Retrieving seller ID directly via seller URL/Извлекаем seller_id напрямую из URL продавца
        seller_id = url.split('/')[-1]
        return int(seller_id)

    def parse(self):
        _page = 1
        self.__create_csv()
        while True:
            params = {
                'appType': '1',
                'curr': 'rub',
                'dest': '-1257786',
                'sort': 'popular',
                'spp': 99,
                'supplier': self.seller_id,
                'page': _page
            }
            response = requests.get('https://catalog.wb.ru/sellers/v2/catalog', params=params)
            if response.status_code != 200:
                break
            items_info = Items.model_validate(response.json()['data'])
            if not items_info.products:
                break
            self.__get_images(items_info)
            self.__feedback(items_info)
            self.__save_csv(items_info)
            _page += 1

    @staticmethod
    def __remove_quotes(name: str) -> str:          # For better readability and to avoid errors when writing to CSV, remove quotes/
        return name.replace('"', '')    # Для лучшей читабельности и для избежания ошибок при записи в CSV-файл удаляем кавычки

    @staticmethod
    def __create_csv():
        with open('wb_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                ['id', 'name', 'price', 'brand', 'rating', 'volume', 'id_seller', 'image', 'reviews_with_text', 'valuation'])

    @staticmethod
    def __save_csv(items: Items):
        with open('wb_data.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for product in items.products:
                product_name = ParseWB.__remove_quotes(product.name)
                writer.writerow([product.id,
                                 product_name,
                                 product.total,
                                 product.brand,
                                 product.rating,
                                 product.volume,
                                 product.supplierId,
                                 product.image_links,
                                 product.feedback_count,
                                 product.valuation
                                 ])


    @staticmethod
    def __get_images(items: Items):
        for product in items.products:
            _short_id = product.id//100000
                                             # Use match/case to determine basket based on _short_id/
                                             # Используем match/case для определения basket на основе _short_id
            if 0 <= _short_id <= 143:
                basket = '01'
            elif 144 <= _short_id <= 287:
                basket = '02'
            elif 288 <= _short_id <= 431:
                basket = '03'
            elif 432 <= _short_id <= 719:
                basket = '04'
            elif 720 <= _short_id <= 1007:
                basket = '05'
            elif 1008 <= _short_id <= 1061:
                basket = '06'
            elif 1062 <= _short_id <= 1115:
                basket = '07'
            elif 1116 <= _short_id <= 1169:
                basket = '08'
            elif 1170 <= _short_id <= 1313:
                basket = '09'
            elif 1314 <= _short_id <= 1601:
                basket = '10'
            elif 1602 <= _short_id <= 1655:
                basket = '11'
            elif 1656 <= _short_id <= 1919:
                basket = '12'
            elif 1920 <= _short_id <= 2045:
                basket = '13'
            elif 2046 <= _short_id <= 2189:
                basket = '14'
            elif 2190 <= _short_id <= 2405:
                basket = '15'
            else:
                basket = '16'

                                           # We make a list of all links to images and translate them into a string/
                                           # Делаем список всех ссылок на изображения и переводим в строку
            link_str = ''.join([
                f'https://basket-{basket}.wbbasket.ru/vol{_short_id}/part{product.id//1000}/{product.id}/images/big/{i}.webp;'
                for i in range(1, product.pics + 1)])
            product.image_links = link_str
            link_str = ''

    @staticmethod
    def __feedback(items: Items):
        for product in items.products:
            url = f'https://feedbacks1.wb.ru/feedbacks/v1/{product.id}'
            res = requests.get(url=url)
            if res.status_code == 200:
                feedback = Feedback.model_validate(res.json())
                product.feedback_count = feedback.feedbackCountWithText
                product.valuation = feedback.valuation


if __name__ == '__main__':
    ParseWB('https://www.wildberries.ru/seller/14104').parse()