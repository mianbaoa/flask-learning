# -*- coding:utf-8 -*-
import time
import random
import string
import hashlib
import urllib
import json
# appId = 'wx30c624fefe6ee9e3'
# appSecret = '11b509811bf88c532dbdc8fe7b9e73f5'
# url_access_token = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'.format(
#     APPID=appId, APPSECRET=appSecret)
# print url_access_token
def json_loads(url):
    content = urllib.urlopen(url).read()
    data = json.loads(content)
    return data
#
# access_token = json_loads(url_access_token)['access_token']
access_token = 'TXIWph1r9SxFip2eRy_SnRXRMYjCKqtWG9wUfcJEWNX_ciFyt3Yj9Ck-PFgODtRQ5nSX5GpRuHLHe9RxQ6k0N6t5n6Ooaz5jSQkHK4x77Bh7uVANajjJm4vik37C3vQIAZVcAIAUTP'
url_ticket = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={ACCESS_TOKEN}&type=jsapi'.format(
    ACCESS_TOKEN=access_token)
ticket = json_loads(url_ticket)['ticket']

print access_token, ticket

class Sign:
    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        print string
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        print self.ret
        return self.ret

# if __name__ == '__main__':
#     # 注意 URL 一定要动态获取，不能 hardcode
#     sign = Sign(ticket, 'http://example.com')
#     print sign.sign()