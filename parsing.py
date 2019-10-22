import re
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://pubs.opengroup.org/onlinepubs/9699919799/'
HEADERS_URL = 'https://pubs.opengroup.org/onlinepubs/9699919799/idx/head.html'

def get_headers(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    soup_cpp_header_links = soup.find_all('li')
    list_cpp_header_links = []

    for header in soup_cpp_header_links:
        link = header.a.get('href')
        link = BASE_URL + link[3:]
        list_cpp_header_links.append(link)

    list_cpp_header_links.pop(0)
    return list_cpp_header_links


def is_func_header(str_func_h):
    if re.search(' (\w+)\(', str_func_h) is None:
        return False
    return True


def get_func_name(str_func_h):
    result = re.search(' (\w+)\(', str_func_h).group(1)
    if re.search('\s', result):
        result = result.split(' ').pop()
        if re.match('\*', result):
            return result[1:]
        return result.split(' ').pop()
    return result


def parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    pre_soup = soup.findAll('pre')
    func_names = []

    header_name_soup = soup.find('blockquote', {'class': 'synopsis'})
    header_name = re.search('<(.+)>', header_name_soup.text).group(1)

    if len(pre_soup) == 0:
        return {header_name: 'None'}

    for item in pre_soup:
        str_func_headers = item.text
        str_func_headers_list = str_func_headers.split(';')
        for str_func_h in str_func_headers_list:
            if is_func_header(str_func_h):
                func_names.append(get_func_name(str_func_h))

    if len(func_names) == 0:
        return {header_name: 'None'}
    return {header_name: func_names}


list_cpp_h_links = get_headers(HEADERS_URL)
json_header_list = []

for link in list_cpp_h_links:
    json_header_list.append(parse(link))

with open('personal.json', 'w') as json_file:
    for item in json_header_list:
        json.dump(item, json_file)


