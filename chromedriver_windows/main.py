import time
import random

from selenium import webdriver
import xlsxwriter
import traceback

from transliterate import translit


class Client:
    url = 'https://www.avito.ru/{}/zapchasti_i_aksessuary?q={}&p={}'
    keys = ['opel+astra', 'volkswagen+golf', 'volkswagen+passat', 'bmw+e', 'peugeot', 'audi+a4', 'audi+a6', 'mazda+3',
            'mazda+6', 'mitsubishi+outlander', 'renault+megane', 'hyndai+i30', 'kia', 'nissan', 'volvo+v70',
            'volvo+v50']
    regions = ['samarskaya_oblast', 'saratovskaya_oblast', 'astrahan', 'volgogradskaya_oblast', 'ulyanovskaya_oblast',
               'rostovskaya_oblast', 'voronezhskaya_oblast', 'belgorodskaya_oblast', 'kurskaya_oblast',
               'lipetskaya_oblast', 'tambovskaya_oblast', 'orlovskaya_oblast', 'dagestan', 'krasnodarskiy_kray',
               'ryazanskaya_oblast', 'respublika_krym', 'vladikavkaz', 'chechenskaya_respublika',
               'bryanskaya_oblast', 'penzenskaya_oblast', 'tulskaya_oblast']

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.153 (Edition Yx GX)")
        options.add_argument("--disable-blink-features=AutomationControlled")
        path_to_chromedriver = "C:\\Users\\david\\PycharmProjects\\parser\\chromedriver_windows\\chromedriver.exe"
        self.driver = webdriver.Chrome(
            executable_path=path_to_chromedriver,
            options=options
        )
        self.driver.implicitly_wait(5)
        self.driver.maximize_window()
        self.result = []

    def run(self):
        try:
            for region in self.regions:
                for key in self.keys:
                    self.driver.get(self.url.format(region, key, ''))
                    all_ad = self.driver.find_element_by_class_name('page-title-count-1oJOc').text
                    page = 1
                    should_be_filtered = True
                    count = 1

                    while should_be_filtered:
                        if page != 1:
                            self.driver.get(self.url.format(region, key, page))
                        urls = list(map(lambda x: x.get_attribute('href'), self.driver.find_elements_by_class_name(
                            'link-link-39EVK link-design-default-2sPEv title-root-395AQ iva-item-title-1Rmmj title-listRedesign-3RaU2 title-root_maxHeight-3obWc'.replace(
                                ' ', '.'))))
                        for url in urls:
                            time.sleep(random.randint(3, 5))
                            self.driver.get(url)
                            info, address, url_user, district, vid_zapchasti = self.parse_element()
                            k = key.split('+')
                            for elem in k:
                                if elem not in info.lower() or translit(elem, 'ru') not in info.lower():
                                    should_be_filtered = False
                            self.result.append(
                                [all_ad, url_user, key.replace('+', ' '), address, district, vid_zapchasti, info,
                                 url])
                            count += 1
                        if count == 50:
                            page += 1
                            count = 1
                    time.sleep(random.randint(1, 5))
                    client.save_result(region, key)

        except Exception as ex:
            print(f'ERROR: {ex}', traceback.format_exc())

    def parse_element(self):
        vid_zapchasti = list(filter(lambda x: True if 'Вид запчасти' in x.text else False,
                                    self.driver.find_elements_by_class_name('item-params-list-item')))
        vid_zapchasti = vid_zapchasti[0].text.replace('Вид запчасти: ', '') if vid_zapchasti else ''
        url_user = self.driver.find_elements_by_class_name('seller-info-name.js-seller-info-name a')[0].get_attribute(
            'href')
        info = self.driver.find_elements_by_class_name('item-description')
        info = info[0].text if info else ''
        address = self.driver.find_elements_by_class_name('item-address__string')
        address = address[0].text if address else ''
        district = self.driver.find_elements_by_class_name('item-address-georeferences')
        district = district[0].text if address else ''
        return info, address, url_user, district, vid_zapchasti

    def save_result(self, region, key):
        workbook = xlsxwriter.Workbook(f'result_{region}_{key}.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, ['Кол-во объявление', 'Ссылка на продавца', 'Ключевое слово', 'Адрес',
                                   'Район', 'Категория', 'Описание', 'Ссылка на объявление'])
        for row, elem in enumerate(self.result):
            worksheet.write_row(row + 1, 0, elem)
        workbook.close()

    def quit(self):
        self.driver.quit()


if __name__ == '__main__':
    client = Client()
    client.run()
    client.quit()
