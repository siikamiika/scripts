import json
import sys
from urllib.request import urlopen, Request

def url2object(url):
    r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urlopen(r).read().decode())

def parse_key(key):
    try:
        return int(key)
    except:
        return key[1:-1]

def main():
    args = sys.argv[1:]
    if args[0] == 'url':
        args = args[1:]
        data = url2object(args[0])
    else:
        data = json.loads(args[0])
    data_list = [[k for k in kl.split(',') if k] for kl in args[1].split(';') if kl]
    for i, kl in enumerate(data_list):
        data_list[i] = data
        for key in kl:
            try:
                data_list[i] = data_list[i][parse_key(key)]
            except Exception as e:
                data_list[i] = str(e)
    sys.stdout.write(json.dumps(data_list))

if __name__ == '__main__':
    main()
