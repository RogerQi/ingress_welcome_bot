#-*-coding: UTF-8-*-
import requests
import json
import re
import time
import random
import logging
import config
from bs4 import BeautifulSoup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename='/var/log/rec.log', filemode='w')
logging.getLogger("requests").setLevel(logging.WARNING)
sent_list = [] #Initialize params
#flag = [1]
url_login = "https://accounts.google.com/ServiceLogin"
url_auth = "https://accounts.google.com/ServiceLoginAuth"
url_intel = 'https://www.ingress.com/intel'
intel_login = "https://www.google.com/accounts/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttps://www.ingress.com/intel&ltmpl=gm&shdf=ChMLEgZhaG5hbWUaB0luZ3Jlc3MMEgJhaCIUDxXHTvPWkR39qgc9Ntp6RlMnsagoATIUG3HUffbxSU31LjICBdNoinuaikg"
headers = {
    'Host': 'www.ingress.com',
    'User-Agent': config.user_agent,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/json; charset=utf-8',
    'X-CSRFToken': 'XXX',
    'Referer': 'https://www.ingress.com/intel',
    'Content-Length': '190',
    'Cookie': "XXX",
    'Connection': 'keep-alive'
    }
v = 'XXX'
pattern = re.compile(r'\w*:\s\bhas\scompleted\straining\b')
vstamp_pattern = re.compile(r'gen_dashboard_\w*.js')

def updatecookie():
    global v
    ses = requests.session()
    login_html = ses.get(url_login)
    soup_login = BeautifulSoup(login_html.content, 'html.parser').find('form').find_all('input')
    dico = {}
    for u in soup_login:
        if u.has_attr('value'):
            dico[u['name']] = u['value']
    dico['Email'] = config.login
    dico['Passwd'] = config.pwd
    ses.post(url_auth, data = dico)
    ses.get(intel_login).request.headers['Cookie']
    cookie = ses.get(intel_login).request.headers['Cookie']
    headers['Cookie'] = cookie
    token = cookie.split(';')[0][cookie.split(';')[0].find('=')+1:]
    headers['X-CSRFToken'] = token
    intel_html = ses.get(url_intel).content
    v = vstamp_pattern.findall(intel_html)[0].split('_')[2].split('.')[0]
def request(url, params = {}, method = "POST"):
    payload=json.dumps(params)
    request=requests.post(url, data = payload, headers = headers, verify = True)
    return request.text

def getfaction(minlat, minlng, maxlat, maxlng): #Comm Faction msg, restrict to map
    url = 'https://www.ingress.com/r/getPlexts'
    payload = {
    "minLatE6": minlat,
    "minLngE6": minlng,
    "maxLatE6": maxlat,
    "maxLngE6": maxlng,
    "minTimestampMs":-1,
    "maxTimestampMs":-1,
    "tab":"faction",
    "v": v
    }
    result_rec =  request(url, params = payload, method = "POST")
    if 'The world around you is not what it seems.' in result_rec:
        logging.warning("Cookies seems invalid. Unable to fetch data. Trying to update")
        updatecookie()
        logging.warning("Cookie and CSRF token updated.")
        getfaction(minlat, minlng, maxlat, maxlng)
    elif 'out of date' in result_rec:
        logging.warning("v_stmap seems invalied.")
        updatecookie()
        logging.warning("v_stamp updated.")
        getfaction(minlat, minlng, maxlat, maxlng)
    else:
        return result_rec

getnamelist = lambda u_msg: [i.split(':')[0] for i in pattern.findall(str(u_msg))]

def send_faction_msg(msg_str, lat = config.bot_latitude, lng = config.bot_longitude):
    url = 'https://www.ingress.com/r/sendPlext'
    payload = {
    "message": msg_str,
    "latE6": lat,
    "lngE6": lng,
    "tab":"faction",
    "v": v
    }
    result = request(url, params = payload, method = "POST")
    result = str(result)
    if 'success' in result:
        return 1
    else:
        return 0

def sent_list_maintainer():
    if len(sent_list) > 200:
        sent_list.reverse()
        for i in range(100):
            sent_list.pop()
        sent_list.reverse()
        logging.warning("Sent list checked and fixed.")

def main():
    buddies_list = []
    faction_msg = getfaction(config.minlat1, config.minlng1, config.maxlat1, config.maxlng1)
    buddies_list += getnamelist(faction_msg)
    time.sleep(3 + random.randint(2,5))
    faction_msg = getfaction(config.minlat2, config.minlng2, config.maxlat2, config.maxlng2)
    buddies_list += getnamelist(faction_msg)
    time.sleep(3 + random.randint(2,5))
    buddies_list = [i for i in list(set(buddies_list)) if i not in sent_list]
    for i in buddies_list:
        time.sleep(4 + random.randint(1,5))
        if send_faction_msg(config.anli % i):
            logging.info('Greeting successfully sent to @%s' % i)
            sent_list.append(i)
        else:
            logging.error("Msg sent failed.")

if __name__ == '__main__':
    while True:
        try:
            main()
            sent_list_maintainer()
            time.sleep(600)
        except Exception, e:
            logging.error(str(e))
            time.sleep(10)
