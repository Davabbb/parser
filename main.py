import xlsxwriter
from selenium import webdriver
import traceback


class Client:
    url = 'https://www.avito.ru/{}/zapchasti_i_aksessuary?q={}&p={}'
    keys = ['opel+astra', 'volkswagen+golf', 'volkswagen+passat', 'bmw+e', 'peugeot', 'audi+a4', 'audi+a6',
            'mazda+3', 'mazda+6', 'mitsubishi+outlander', 'renault+megane', 'hyndai+i30', 'kia', 'nissan',
            'volvo+v70', 'volvo+v50']
    regions = ['samarskaya_oblast', 'saratovskaya_oblast', 'astrahan', 'volgogradskaya_oblast',
               'ulyanovskaya_oblast',
               'rostovskaya_oblast', 'voronezhskaya_oblast', 'belgorodskaya_oblast', 'kurskaya_oblast',
               'lipetskaya_oblast', 'tambovskaya_oblast', 'orlovskaya_oblast', 'dagestan', 'krasnodarskiy_kray',
               'ryazanskaya_oblast', 'respublika_krym', 'vladikavkaz', 'chechenskaya_respublika',
               'bryanskaya_oblast',
               'penzenskaya_oblast', 'tulskaya_oblast']

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        # chrome_options.binary_location = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        chrome_options.add_argument('--remote-debugging-port=9222')
        path_to_chromedriver = 'chromedriver_windows/chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=path_to_chromedriver, chrome_options=chrome_options)
        self.driver.implicitly_wait(5)
        self.driver.maximize_window()
        self.result = []

    def get_pagination(self):
        pagination = self.driver.find_elements_by_class_name('pagination-item-1WyVp')
        return 1 if len(pagination) == 0 else int(pagination[-2].text)

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

    def run(self):
        try:
            for region in self.regions:
                for key in self.keys:
                    self.driver.get(self.url.format(region, key, ''))
                    all_ad = self.driver.find_element_by_class_name('page-title-count-1oJOc').text
                    for page in range(1, self.get_pagination() + 1):
                        if page != 1:
                            self.driver.get(self.url.format(region, key, page))
                        urls = list(map(lambda x: x.get_attribute('href'), self.driver.find_elements_by_class_name(
                            'link-link-39EVK link-design-default-2sPEv title-root-395AQ iva-item-title-1Rmmj title-listRedesign-3RaU2 title-root_maxHeight-3obWc'.replace(
                                ' ', '.'))))
                        for url in urls:
                            self.driver.get(url)
                            info, address, url_user, district, vid_zapchasti = self.parse_element()
                            self.result.append(
                                [all_ad, url_user, key.replace('+', ' '), address, district, vid_zapchasti, info,
                                 url])
        except Exception as ex:
            print(f'ERROR: {ex}', traceback.format_exc())

    def save_result(self):
        workbook = xlsxwriter.Workbook('result.xlsx')
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
    client.save_result()
    client.quit()
