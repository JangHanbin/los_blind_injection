import requests
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


def do_blind_inject(pwning_url, field):

    digit = 10
    while True:

        # data = {field : }
        res = requests.get(pwning_url)

if __name__ == '__main__':
    user_id = input('Enter your los id : ')
    # user_pw = getpass('Enter your los pw : ')
    user_pw = input('Enter your los pw : ')
    login_cookies = login(user_id, user_pw)

    pwning_url = input('Enter your pwning_url : ')
    pwning_query = input('Enter defalut query to escape security options')


