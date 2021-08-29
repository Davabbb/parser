import time
import random

from selenium import webdriver
import xlsxwriter
import traceback
from PIL import Image
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class Client:
    url = 'https://www.avito.ru/{}/zapchasti_i_aksessuary?q={}&p={}'
    keys = [#'opel+astra', 'volkswagen+golf', 'volkswagen+passat',
            'bmw+e', 'peugeot', 'audi+a4', 'audi+a6', 'mazda+3',
            'mazda+6', 'mitsubishi+outlander', 'renault+megane', 'hyndai+i30', 'kia', 'nissan', 'volvo+v70',
            'volvo+v50']
    data = {'opel+astra': ["опель", "астра"],
            'volkswagen+golf': ["гольф"],
            'volkswagen+passat': ["пассат"],
            'bmw+e': ["бмв"],
            'peugeot': ["пежо"],
            'audi+a4': ["ауди"],
            'audi+a6': ["ауди"],
            'mazda+3': ["мазда"],
            'mazda+6': ["мазда"],
            'mitsubishi+outlander': ["митсубиси", "аутлендер"],
            'renault+megane': ["рено", "меган"],
            'hyndai+i30': ['хендай'],
            'kia': ["киа"],
            'nissan': ['ниссан'],
            'volvo+v70': ["вольво"],
            'volvo+v50': ["вольво"]}
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
                    while should_be_filtered:
                        if page != 1:
                            self.driver.get(self.url.format(region, key, page))
                        urls = list(map(lambda x: x.get_attribute('href'), self.driver.find_elements_by_class_name(
                            'link-link-39EVK link-design-default-2sPEv title-root-395AQ iva-item-title-1Rmmj title-listRedesign-3RaU2 title-root_maxHeight-3obWc'.replace(
                                ' ', '.'))))
                        count_url = 0
                        while should_be_filtered and count_url != 49:
                            self.driver.get(urls[count_url])
                            print(page, count_url + 1, key, region, urls[count_url])
                            info, address, url_user, district, vid_zapchasti, name, phone, contact = self.parse_element()
                            k = key.split('+')
                            for elem in k:
                                if elem not in info.lower() and elem not in name.lower():
                                    should_be_filtered = False
                            for elem in self.data[key]:
                                if elem in info.lower() or elem in name.lower():
                                    should_be_filtered = True
                            self.result.append(
                                [contact, phone, url_user, key.replace('+', ' '), address, district, vid_zapchasti, info,
                                 urls[count_url]])
                            count_url += 1
                        page += 1
                    client.save_result(region, key)
                    self.result = []

        except Exception as ex:
            print(f'ERROR: {ex}', traceback.format_exc())

    def parse_element(self):
        button = self.driver.find_elements_by_xpath('//button[@class="popup-close-2W0cr"]')
        if button:
            button[0].click()
        vid_zapchasti = list(filter(lambda x: True if 'Вид запчасти' in x.text else False,
                                    self.driver.find_elements_by_class_name('item-params-list-item')))
        vid_zapchasti = vid_zapchasti[0].text.replace('Вид запчасти: ', '') if vid_zapchasti else ''
        url_user = self.driver.find_elements_by_class_name('seller-info-name.js-seller-info-name a')
        url_user = url_user[0].get_attribute('href') if url_user else ''
        info = self.driver.find_elements_by_class_name('item-description')
        info = info[0].text if info else ''
        address = self.driver.find_elements_by_class_name('item-address__string')
        address = address[0].text if address else ''
        district = self.driver.find_elements_by_class_name('item-address-georeferences')
        district = district[0].text if address else ''
        name = self.driver.find_elements_by_class_name('title-info-title-text')
        name = name[0].text if name else ''

        time.sleep(random.randint(1, 3))

        button = self.driver.find_elements_by_xpath('//button[@class="styles-item-phone-button_height-3SOiy button-button-2Fo5k button-size-l-3LVJf button-success-1Tf-u width-width-12-2VZLz"]')
        if button:
            button[0].click()
            time.sleep(1)
            self.take_screenshot()
            image = self.driver.find_element_by_xpath('//img[@class="contacts-phone-3KtSI"]')
            location = image.location
            size = image.size
            phone = self.crop_(location, size)
        else:
            phone = ''

        #contact = self.driver.find_elements_by_class_name('seller-info-col')
        #contact = contact[1].text if contact else ''
        contact = ''

        return info, address, url_user, district, vid_zapchasti, name, phone, contact

    def crop_(self, location, size):
        image = Image.open("avito_screenshot.png")
        x = location['x']
        y = location['y']
        width = size['width']
        height = size['height']
        image.crop((x, y, x + width, y + height)).save('tel.png')
        return self.tel_recon()

    def tel_recon(self):
        image = Image.open('tel.png')
        return pytesseract.image_to_string(image)

    def save_result(self, region, key):
        workbook = xlsxwriter.Workbook(f'result_{region}_{key}.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, ['Кол-во объявление', 'Телефон', 'Ссылка на продавца', 'Ключевое слово', 'Адрес',
                                   'Район', 'Категория', 'Описание', 'Ссылка на объявление'])
        for row, elem in enumerate(self.result):
            worksheet.write_row(row + 1, 0, elem)
        workbook.close()

    def take_screenshot(self):
        self.driver.save_screenshot('avito_screenshot.png')

    def quit(self):
        self.driver.quit()


if __name__ == '__main__':
    client = Client()
    client.run()
    client.quit()
