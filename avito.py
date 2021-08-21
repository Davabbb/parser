import requests
from bs4 import BeautifulSoup
import time


def get_data(url, model):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 OPR/77.0.4054.275 (Edition Yx GX)"
    }

    # req = requests.get(url, headers)
    # print(req.text)

    # with open("projects.html", "w", encoding='utf-8') as file:
    #     file.write(req.text)

    with open("projects.html", "r", encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    articles = soup.find_all(class_="iva-item-root-G3n7v")

    projects_url = []
    for article in articles:
        project_url = "https://www.avito.ru" + article.find("div", class_="iva-item-titleStep-2bjuh").find("a").get("href")
        projects_url.append(project_url)

    for project_url in projects_url[0:1]:
        print(project_url)
        req = requests.get(project_url, headers)
        name = project_url.split("/")[-2]

        with open(f"data/{name}.html", "w", encoding='utf-8') as file:
            file.write(req.text)

        with open(f"data/{name}.html", encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        data = soup.find("div", class_="l-content clearfix")

        d = data.find("div", class_="item-description-html").find_all("strong")
        description = ''
        for elem in d:
            elem = elem.text
            description += elem + '\n'
        print(description)

        address = data.find("span", class_="item-address__string").text.split(',')
        district = address[0]
        city = address[1]
        address = address[-2] + address[-1]
        print(district)
        print(city)
        print(address)
        code_word = model
        print(code_word)


all_places = ['samarskaya_oblast', 'saratovskaya_oblast', 'astrahan', 'volgogradskaya_oblast', 'ulyanovskaya_oblast',
              'rostovskaya_oblast', 'voronezhskaya_oblast', 'belgorodskaya_oblast', 'kurskaya_oblast',
              'lipetskaya_oblast', 'tambovskaya_oblast', 'orlovskaya_oblast', 'dagestan', 'krasnodarskiy_kray',
              'ryazanskaya_oblast', 'respublika_krym', 'vladikavkaz', 'chechenskaya_respublika', 'bryanskaya_oblast',
              'penzenskaya_oblast', 'tulskaya_oblast']
all_models = ['opel+astra', 'volkswagen+golf', 'volkswagen+passat', 'bmw+e', 'peugeot', 'audi+a4', 'audi+a6',
              'mazda+3', 'mazda+6', 'mitsubishi+outlander', 'renault+megane', 'hyndai+i30', 'kia', 'nissan',
              'volvo+v70', 'volvo+v50']
for place in all_places:
    for model in all_models:
        get_data(f"https://www.avito.ru/{place}/zapchasti_i_aksessuary?q={model}", model)
