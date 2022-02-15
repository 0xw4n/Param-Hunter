import argparse
import requests
import re

desc = 'Example: paramhunter.py -u https://example.com/index.php -w /path/to/wordlist OR paramhunter.py -U urls.txt -w /path/to/wordlist'



def url_validation(url):
    if re.search(r'https?:\/\/', url) is None:
        url = 'https://' + url
    if '?' in url:
        find = re.findall(r'.+?(?=\?)', url)
        url = find[0] + '?'
    else:
        url = url + '?'

    return url

def isReflected(response):
    if 'paramHunter' in response:
        return True
    else:
        return False

def analyze_payload(response):
    try:
        find = re.findall(r'\bparamHunter\S*', response)
        print(find)
        filter = re.findall(r'[/?()`}{!#&$<>\'\"]', find[0])
    except:
        pass
    return filter

parser = argparse.ArgumentParser(description=desc)
parser.add_argument('--url', '-u', help='single url', type=str)
parser.add_argument('--urls', '-U', help='url wordlist', type=str)
parser.add_argument('--wordlist', '-w', help='use custom parameter wordlist', type=str, required=True)
parser.add_argument('--analyze', '-a', help='analyze if there is a filter in place', action='store_true', dest='isAnalyze')
args = parser.parse_args()

chars = 'paramHunter/?()`}{!#&$<>\'\"'
wordlist = args.wordlist
with open(wordlist) as f:
    params = f.read().splitlines()

if args.url and args.urls is not None:
    print('Only one argument --url or --urls, -h for help')
    exit()

elif args.url is not None and args.urls is None:
    url = args.url
    url = url_validation(url)
    for param in params:
        try:
            target = url + param + '=' + chars
            r = requests.get(target)
            response = r.text
            if r.status_code == 404 or r.status_code == 500 or r.status_code == 403:
                print(target + ' : ' + r.status_code)
            elif isReflected(response):
                txt = target + ' : reflected'
                print(txt)
                if args.analyze is True:
                    print(' not filter: '+ analyze_payload(response))
        except:
            pass


elif args.urls is not None and args.url is None:
    urls = []
    tmp = []
    with open(args.urls) as f:
        url = f.read().splitlines()
    for u in url:
        u = url_validation(u)
        tmp.append(u)
    for t in tmp:
        for param in params:
            u = t + param + '=' + chars
            urls.append(u)
    for url in urls:
        try:
            r = requests.get(url)
            response = r.text
            if r.status_code == 404 or r.status_code == 500 or r.status_code == 403:
                print(url + ' : ' + r.status_code)
            elif isReflected(response):
                txt = url + ' : reflected'
                print(txt)
                if args.analyze is True:
                    print(' not filter: '+ analyze_payload(response))
        except:
            pass

else:
    print('Only one argument --url or --urls, -h for help')
    exit()
