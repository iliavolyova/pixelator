
class Config():
    def __init__(self):
        respath = '../../res/creds.txt'
        credsFile = open(respath, 'r')
        self.creds = {}
        for line in credsFile:
            k, v = line.strip().split('=')
            self.creds[k.strip()] = v.strip()
