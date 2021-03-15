import inspect
import urllib
import os


import requests
from bs4 import BeautifulSoup
import csv

from tkinter import *
from tkinter import messagebox

window = Tk()
name = StringVar()

LOG_PATH = 'C:\\forum.csv'
URL = 'http://imf.forum24.ru'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0', 'accept': '*/*'}
#создаем константы c URL сайта и используемым браузером, чтобы сайт не принимал нас за скрипт
FILE = 'forum.csv'



DEFAULT_WORK = 16
DEFAULT_KAKISKAT = 1
#objform = {'parol': '', 'chto': '', 'work': '16', 'kakiskat': '1'}  # данные форм, из которых формируется запрос


class SearchAttr(object):
    def __init__(self, parol, chto, work, kakiskat):
        self.parol = parol
        self.chto = chto
        self.work = work
        self.kakiskat = kakiskat

def open_config():
    o_search_attr = SearchAttr('', '', DEFAULT_WORK, DEFAULT_KAKISKAT)
    line_count = 0
    with open('data.txt', "r", encoding="utf-8") as f:
        for line in f:
            if line_count == 1:
                o_search_attr.parol = line[0:-1]
            elif line_count == 2:
                o_search_attr.chto = line[0:-1]
            elif line_count == 3:
                o_search_attr.work = line[0:-1]
            elif line_count == 4:
                o_search_attr.kakiskat = line
            line_count += 1
    return o_search_attr

oSearchAttr = open_config()

def post_html(url, params):
    r = requests.post(url, headers = HEADERS, params = params)
    return r

def get_html(url):
    r = requests.get(url, headers = HEADERS)
    return r


def get_content(html, group_selector):
    soup = BeautifulSoup(html, 'html.parser') # чтобы парсить хтмл, создаем объект суп, передаем html и тип док-та,
    # с которым работаем, если его не передавать, то в консоли будет предупреждение, хотя все будет работать
    items = soup. \
        select(group_selector)
    return items

def link_discussion(items):
    discussions = []
    for item in items:
        discussions.append({
            'title': item.text,
            'href': item['href']
        })
    return discussions


def save_file(arg1):
    with open(LOG_PATH, 'a+', newline = '') as file:
        writer = csv.writer(file)
        if os.path.exists(LOG_PATH):
            file.seek(0)
        for i in arg1:
            writer.writerow([i])
    file.close()




def parse():
    objform = props(oSearchAttr)
    objform["chto"] = urllib.parse.quote(oSearchAttr.chto)

    html = post_html(URL, objform)

    print(html.status_code)
    if html.status_code == 200: # статус код 200 означает, что у нас есть доступ и ответ от страницы
        group_selector = \
            "#content-table-main tr > td > table tr > td.font3 > a"
            #"#content-table-main > tr > td > table > tr > td.font3 > a"
        itemContent = get_content(html.text, group_selector)
        arrContent = link_discussion(itemContent)
        link_tree_process(arrContent)

    else:
        messagebox.showerror("Ошибка", "Нет доступа к сайту!")
        #print('error')

def content_search(html, group_selector, chto_name):
    arrPages = get_content(html.text,
                           #'#posts-table tr.font1 > td > a')
                           'tr.font1 > td > a')
    if (arrPages is not None) and len(arrPages)>0:
        for page in arrPages:
            if (page.text.upper() == "All".upper()):
                url = URL + page['href']
                html = get_html(url)
                if html.status_code == 200:
                    break

    arrContent = get_content(html.text, group_selector)
    for content in arrContent:
        if (content.text is not None) and ( -1 < content.text.find(chto_name)):
            #print("Поиск контента: {0}".format(content.text))
            try:
                save_file(("", urllib.parse.unquote(content.text)))
            except:
                continue
        else:
            print("Контент не найден")

list_of_end = []
def link_tree_process(arrContent):
    open(LOG_PATH, "w").close()
    for content in arrContent:
        #save_file('title:{0} \n href:{1} \n'.format(content['title'], content['href']))       #!!!!!!!!!!
        url = URL + content['href']
        save_file((content['title'], url))
        html = get_html(url)
        if html.status_code == 200:  # статус код 200 означает, что у нас есть доступ и ответ от страницы
            group_selector = \
                "#table-thread tr > td > table tr > td:nth-child(2) > font.font3 > a" #tochka
            itemContent = get_content(html.text, group_selector)  #tochka
            arrContent = link_discussion(itemContent)
            if len(arrContent) > 0:
                link_tree_process(arrContent)
            else:
                print("URL: {0}".format(url))
                group_selector = 'div.font1'
                content_search(html, group_selector, oSearchAttr.chto)
        else:
            messagebox.showerror("Ошибка", "Нет доступа к сайту!")
            #print('error')

def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
            pr[name] = value
    return pr
def button_click_search():
    if len(text_e.get()) == 0:
        messagebox.showerror("Ошибка", "Не введена фраза для поиска!")
        pass
    else:
        #oSearchAttr.parol = ''
        #oSearchAttr.chto = text_e.get()
        #oSearchAttr.work = 16
        #oSearchAttr.kakiskat = rb_search.get()
        #oSearchAttr =  SearchAttr('', text_e.get(), 16, rb_search.get())
        oSearchAttr.chto = text_e.get()
        oSearchAttr.kakiskat = rb_search.get()
        try:
            parse()
        except Exception as e:
            messagebox.showerror("Ошибка", '"{}"\n Нет подключения!'.format(e))
            #print('Ошибка:\n', e)
        window.quit()

#add widget here

photo = PhotoImage(file='rkkaww_banner.gif')
photoimage = photo.subsample(3, 3)

lbl = Label(window, text = "Запрос", fg = "blue", font=("Arial", 17))
lbl.place(x=50, y=50)

text_e = Entry(window, textvariable = name, width = 40)
text_e.place(x=50, y=100)
name.set(oSearchAttr.chto)

# radiobuttons set ; v - variable that connecting buttons

rb_search = IntVar()
rb_search.set(oSearchAttr.kakiskat)

radio_button = Radiobutton(window, text="Фраза", variable = rb_search, value=1)
radio_button.place(x=50, y=150)

radio_button2 = Radiobutton(window, text="Слово", variable = rb_search, value=2)
radio_button2.place(x=50, y=200)

radio_button3 = Radiobutton(window, text="Все слова", variable = rb_search, value=3)
radio_button3.place(x=50, y=250)

command_button = Button(window, text="Поиск", image = photoimage, compound = LEFT, command=button_click_search)
command_button.place(x=50, y=300)

# add title
window.title("Международный военный форум")
window.iconphoto(False, photo)
# set frame and geometry (widthxheight+XPOS+YPOS)
window.geometry("400x400+100+200")
window.mainloop()