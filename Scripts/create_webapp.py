import os
import re
from spyre import server

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

from dateutil.relativedelta import relativedelta
import datetime


# Функція для встановлення першого дня кожного року (н/д 1 січня 2004)
def df_datetime_date(year):
    return datetime.date(year, 1, 1)


# Функція, яка дасть змогу додавати до поточного дня року певну кількість тижнів, які будуть переведені у дні та місяці
def df_relativedelta(week):
    return relativedelta(weeks=+week)


# Функція для зміни формату дат, щоб можна було попудувати графік, на якому значення показників залежать від часу
def change_data_format(df):
    df["Week"] = df["Week"].astype("int")
    df["Year"] = df["Year"].astype("int")
    df["date"] = df["Year"].apply(df_datetime_date) + df["Week"].apply(df_relativedelta)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    pass


# Функція, яка видаляє HTML-теги з початкового файлу (н/д такі, як <br>)
def remove_tags(string):
    return re.sub("<.*?>", "", string)


# Функція для створення та підготовки єдиного файлу даних (конкатенація усіх файлів .csv)
def prepare_dataframe(path):
    concatenate_files = []
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath):
            headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty', 'Area']
            df = pd.read_csv(filepath, header=1, names=headers)

            df["Year"] = df["Year"].apply(lambda cw: remove_tags(cw))  # Застосовуємо ф-ію видалення HTML-тегів
            df = df.loc[df["VHI"] != -1]  # Обрати лише ті дані, де показник "VHI" не дорівнює -1
            df = df[df["Week"].notna()]  # Використовувати лише існуючі дані
            df = df.dropna(axis=1)  # Видалати стовпчик порожніх значень (empty)

            df["Area"] = regions[int(filename.split("_")[2]) - 1]
            concatenate_files.append(df)
    return pd.concat(concatenate_files, axis=0, ignore_index=True)


regions = ["АР Крим", "Вінницька", "Волинська", "Дніпропетровська", "Донецька", "Житомирська", "Закарпатська",
           "Запорізька", "Івано-Франківська", "Київ", "Київська", "Кропивницька", "Луганська", "Львівська",
           "Миколаївська", "Одеська", "Полтавська", "Рівненська", "Севастополь", "Сумська", "Тернопільська",
           "Харківська", "Херсонська", "Хмельницька", "Черкаська", "Чернівецька", "Чернігівська"]


# translit_regions = ["Crimea", "Vinnytska", "Volhkjynska", "Dnipropetrovska", "Donetska", "Zhytomyrska", "Zakarpatska",
#                     "Zaporizka", "Ivano-Frankivska", "Kyiv_city", "Kyiv_region", "Kropyvnytsk", "Luhansk", "Lviv",
#                     "Mykolaiv", "Odesa", "Poltava", "Rivne", "Sevastopol", "Sumy", "Ternopil", "Kharkiv", "Kherson",
#                     "Khmelnytsk", "Cherkasy", "Chernivtsi", "Chernihiv"]


class WebAPI(server.App):
    title = "NOAA data vizualization"  # Заголовок веб-додатку

    inputs = [{"type": "dropdown",  # Випадаючий список для показників: VCI, TCI та VHI
               "label": "NOAA data dropdown",
               "options": [{"label": "VCI", "value": "VCI"},
                           {"label": "TCI", "value": "TCI"},
                           {"label": "VHI", "value": "VHI"}],
               "key": "type",
               "action_id": "update_data"},

              {"type": "dropdown",  # Випадаючий список для вибору області
               "label": "Region dropdown",
               "options": [{"label": f"{name}", "value": f"{name}"} for name in regions],
               "key": "region",
               "action_id": "update_data"},

              {"type": "text",  # Текстове поле для введення інтервалу років
               "label": "Year interval",
               "key": "year",
               "value": '1982-2022',
               "action_id": "simple_html_output"},

              {"type": "text",  # Текстове поле для введення інтервалу тижнів
               "label": "Week interval",
               "key": "week",
               "value": '1-52',
               "action_id": "simple_html_output"}]

    controls = [{"type": "button",  # Кнопка, яка оновлює сторінку з новими значеннями
                 "label": "Завантажити дані",
                 "id": "update_data"}]

    tabs = ["Plot", "Table"]  # Дві вкладки для відображення графіку та таблиці

    outputs = [{"type": "plot",  # Дані демонстуруються на графіку
                "id": "plot_id",
                "control_id": "update_data",
                "tab": "Plot"},

               {"type": "table",  # Дані демонстуруються у таблиці
                "id": "table_id",
                "control_id": "update_data",
                "tab": "Table",
                "on_page_load": True}]

    def getData(self, params):  # Ф-ія для занесення даних із єдиного файлу у таблицю веб-додатку
        server.include_df_index = True  # Опція для відображення індексів у DataFrame (скорочено df)

        df = prepare_dataframe("./../NOAA_data")
        change_data_format(df)
        return df[(df["Area"] == params["region"]) &
                  (df["Week"] >= int(params["week"].split("-")[0])) &
                  (df["Week"] <= int(params["week"].split("-")[1])) &
                  (df["Year"] >= int(params["year"].split("-")[0])) &
                  (df["Year"] <= int(params["year"].split("-")[1]))]

    def getPlot(self, params):  # Ф-ія для занесення даних із єдиного файлу на графік веб-додатку
        df = prepare_dataframe("./../NOAA_data")
        change_data_format(df)
        df = df[(df["Area"] == params["region"]) &
                (df["Week"] >= int(params["week"].split("-")[0])) &
                (df["Week"] <= int(params["week"].split("-")[1])) &
                (df["Year"] >= int(params["year"].split("-")[0])) &
                (df["Year"] <= int(params["year"].split("-")[1]))]

        # Встановлення стилю (заднього фону та розміру) графіка
        sns.set_style("darkgrid")
        plt.figure(figsize=(24, 12))
        return sns.scatterplot(x=df["date"], y=df[params["type"]])


app = WebAPI()
app.launch()
