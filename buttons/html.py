x="**Жирный текст** *Курсивный текст* ~~Зачеркнутый текст~~ `Моноширинный текст` [Ссылка](https://example.com) > Цитата __Подчеркнутый текст__ [hidden]Это скрытый текст[/hidden]"

def find_indices(text, substring):
    indices = []
    start = 0
    while start < len(text):
        index = text.find(substring, start)
        if index == -1:
            break
        indices.append(index)
        start = index + len(substring)
    return indices


def convert_to_html(text: str) -> str:
    dict_index = {
        '%%': [],        # жирный
        '^^': [],        # курсив my
        ';;': [],        # зачеркнутый
        '!!': [],         # моно
        '&&': [],        # цитата my
        '№№': [],        # ссылка my
        '$$': []         # скрытый my
    }
    dict_html_1 = {
        '%%': '<b>',  # жирный
        '^^': '<i>',  # курсив my
        ';;': '<s>',  # зачеркнутый
        '!!': '<code>',  # моно
        '&&': '<pre>',  # цитата my
        '№№': '<a href="',  # ссылка my
        '$$': '||'      # скрытый my
    }
    dict_html_2 = {
        '%%': '</b>',  # жирный my
        '^^': '</i>',  # курсив my
        ';;': '</s>',  # зачеркнутый my
        '!!': '</code>',  # моно my
        '&&': '</pre>',  # цитата my
        '№№': '</a>',  # ссылка my
        '$$': '||'  # скрытый my
    }
    for k in dict_index.keys():
        dict_index[k] = find_indices(text, k)


    for k,v in dict_index.items():
        if len(v) != 0 and k!='№№':
            for i in range(0, len(v), 2):
                text = text.replace(k, dict_html_1[k], 1)
                text = text.replace(k, dict_html_2[k], 1)

    if len(dict_index['№№'])!=0:
        for i in range(0, len(dict_index['№№']), 2):
            text = text.replace('№№', dict_html_1['№№'], 1)
            text = text.replace(' №№', dict_html_2['№№'], 1)
            text = text.replace('№ ', '">', 1)
    return text


