from spyre import server


class StockExample(server.App):
    title = "NOAA data vizualization"

    inputs = [{"type": 'dropdown',
               "label": 'NOAA data dropdown',
               "options": [{"label": "VCI", "value": "VCI"},
                           {"label": "TCI", "value": "TCI"},
                           {"label": "VHI", "value": "VHI"}],
               "key": 'ticker',
               "action_id": "update data"}]


inputs = [dict(type='text',
               key='range',
               label='date-ranges',
               value='9-10',
               action_id='simple_html_output')]


def getHTML(self, params):
    range = params["range"]
    return range


outputs = [{"type": "plot",
            "id": "plot",
            "control_id": "update_data",
            "tab": "Plot"},
           {"type": "table",
            "id": "table_id",
            "control_id": "update_data",
            "tab": "Table",
            "on_page_load": True}]

app = StockExample()

app.launch()
