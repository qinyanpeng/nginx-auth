from flask import Flask, abort, request, session, make_response, redirect
from flask import render_template
import sys
import uuid
import requests
import json

SIGNATURE = uuid.uuid4().hex
COOKIE = 'domin.cn'   #随机字符串
ID = ["zhangsan","lisi"] #账号
sessions = {}

app = Flask(__name__)

#  sso验证账号，可替换为其他认证（ldap，自定义认证）。返回true则认证成功。
def check_login(username, password):
  if username and password:
    import time
    import json
    import hashlib
    import requests
    authTimestamp = str(int(time.time()))
    uuid = "www.domain.cn"
    authNonce = getRandomSet(10)
    appId = "sd3fafw23240e4872e3270af4k70ea"
    authSignature = authTimestamp + authNonce + appId + uuid + "Vq6Z9ZKc3g05FU2d"
    hl = hashlib.md5()
    hl.update(authSignature.encode("utf8"))
    authSignature_md5 = hl.hexdigest()
    key = "authSignature=" + authSignature_md5 + "&uuid=" + uuid + "&authNonce=" + \
        authNonce + "&authTimestamp=" + authTimestamp + "&appId=" + appId
    url = "http://sso.domain.cn/user/login?" + key
    playload = {'userid': username, 'password': password}
    h = {"Content-type": "application/json"}
    r = requests.post(url, data=json.dumps(playload), headers=h)
    if r.status_code == 200:
      data = json.loads(r.text)
      if data['code'] == 0:
        return True
  return False


def getRandomSet(bits):
  import random
  num_set = [chr(i) for i in range(48, 58)]
  char_set = [chr(i) for i in range(97, 123)]
  total_set = num_set + char_set
  value_set = "".join(random.sample(total_set, bits))

  return value_set

# 检查 Session 是否已存在
def is_active_session():
  sid = request.cookies.get(COOKIE)
  if not sid:
    return None
  if sid in sessions:
    return sid
  else:
    return None


def show_headers():
  import pprint
  hdrs = dict(request.headers)
  pprint.pprint(hdrs)


@app.route("/")
def hello_world():
  return "ok"


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    sms_code = request.form['sms']
    url = request.form['url']
    sid = is_active_session()
    return do_login(username,password,sms_code,sid,url)
  else:
    return login_page()


#短信验证码
@app.route("/getsms", methods=['POST'])
def getsms():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    if username not in ID:
      return "您没有权限登录。请联系【管理员】。"
    if check_login(username, password):
      r = requests.post('http://manage.domain.cn/manage/inner/sendSms', data={
                        'userName': username}, headers={'Content-Type': 'application/x-www-form-urlencoded'})
      if r.status_code == 200 :
          data=json.loads(r.text)
          return 'ok'
          if  data['code'] == 0:
            return "ok"
          else:
            return data
    else:
      return "用户名密码错误。"

  else:
    return login_page()


def check_sms(username,sms_code):
    r = requests.post('http://manage.domain.cn/checkSms', data={
                        'userName': username,'code':sms_code}, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    if r.status_code == 200 :
        data=json.loads(r.text)
        if int(data['code'])==0:
          return True
    return False

def do_login(username,password,sms_code,sid,url):
  if sid:
    redirect(url)
  if username not in KEY:
    return "您没有权限登录。请联系【管理员】。"
  # if check_login(username, password) && check_sms(username, sms_code):
  
  if check_sms(username, sms_code):
    sid = uuid.uuid4().hex
    sessions[sid] = username
    #resp = make_response(redirect(url))
    resp = make_response("ok")
    resp.set_cookie(COOKIE, sid, path="/", httponly=True)
    return resp
    #return "ok" 
  else:
    return "登录失败。"


def login_page(name=None):
  sid = is_active_session()
  url = request.args.get('url')
  if sid:
    # return '已登入：%s' % sid
    redirect(url)
  return render_template('login_page.html', name=name)


# 认证
@app.route('/auth')
def auth():
  # 检查 Session 是否存在
  sid = is_active_session()
  if sid:
    # HTTP 200 表示认证成功
    return 'OK ' + str(sid)
  else:
    #  HTTP 401 表示认证失败
    abort(401, "Unathenticated")


if __name__ == '__main__':
  app.run(
      debug=True,
      host="127.0.0.1",
      port=int("18000")
  )
