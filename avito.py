import requests
from bs4 import BeautifulSoup


def get_data(url):
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

    for project_url in projects_url:
        print(project_url)
        req = requests.get(project_url, headers)
        name = project_url.split("/")[-2]

        with open(f"data/{name}.html", "w", encoding='utf-8') as file:
            file.write(req.text)

        with open(f"data/{name}.html", encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        info = soup.find("div", class_="l-content clearfix")


get_data("https://www.avito.ru/perm/zapchasti_i_aksessuary?cd=1")

