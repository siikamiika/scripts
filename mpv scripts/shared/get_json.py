import json
import sys

def main():
    args = sys.argv[1:]
    data = args[0]
    data = json.loads(data)
    keys = args[1].split(',')
    for key in keys:
        data = data[key]
    sys.stdout.write(json.dumps(data))

if __name__ == '__main__':
    main()
