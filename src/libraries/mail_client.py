# buildin pacakges
from datetime import datetime
import base64
import sys
import json
# 3rd party packages
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apiclient import errors
import yaml
# my pacakges
from libraries.arguments import parse_arguments
import libraries.config as config

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

KEYS_ACCOUNTS = ["config","mail_client","accounts"]

def _print_mail_help():
  cmd_indent = "".join([" " * len(sys.argv[0])])
  print(
"""usage:
  %s mail init <MAIL_ADDRESS> [{-t | --type} <MAIL_TYPE>] 
  %s                          [{-u | --username} <MAIL_USER>] 
  %s                          [{-p | --password} <MAIL_PASS>]
  %s                          [{-P | --pop3-server} <ADDRESS{:PORT}>]
  %s                          [{-I | --imap-server} <ADDRESS{:PORT}>]
""" % (
    sys.argv[0],
    cmd_indent, cmd_indent, cmd_indent, cmd_indent
  ))

# Gmail のトークンを取得
def _gmail_get_token(mail_address):
  creds = None
  if "gmail" != config.get(KEYS_ACCOUNTS + [mail_address,"type"]):
    return None
  token = config.get(KEYS_ACCOUNTS + [mail_address,"token"])
  if token is not None:
      creds = Credentials.from_authorized_user_info(token, GMAIL_SCOPES)
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          credentials = config.get(["config","mail_client","gmail","credentials"])
          print(credentials)
          print(config.get(["config","mail_client"]))
          flow = InstalledAppFlow.from_client_config(credentials, GMAIL_SCOPES)
          creds = flow.run_local_server(port=0)
      config.set(KEYS_ACCOUNTS + [mail_address,"token"], json.loads(creds.to_json()))
  return creds

# Gmail からメールを取得
def _gmail_get_mail(mail_address, q=None, max_read=0, start_time=None, flat=False):
  if max_read < 1:
    max_read = 10

  creds = _gmail_get_token(mail_address)

  read_opt = {
    "maxResults": max_read
  }
  if q is not None:
    read_opt["q"] = q

  # 検索条件を指定して読み込む
  service = build("gmail", "v1", credentials=creds)
  message_ids = (
    service
    .users()
    .messages()
    .list(userId="me", **read_opt)
    .execute()
  )
  messages = []
  for message_id in message_ids["messages"]:
    detail = (
      service
      .users()
      .messages()
      .get(userId="me", id=message_id["id"])
      .execute()
    )
    message = {
      "message_id": message_id["id"]
    }
    # 本文
    if "data" in detail["payload"]["body"]:
      decoded_bytes = base64.urlsafe_b64decode(
          detail["payload"]["body"]["data"])
      message["body"] = decoded_bytes.decode("UTF-8")
    elif 0 < len(detail["payload"]["parts"]):
      for part in detail["payload"]["parts"]:
        if "mimeType" in part and \
            "text/plain" == part["mimeType"] and \
            "body" in part and \
            "data" in part["body"]:
          # とりあえずエンコードは後回し
          decoded_bytes = base64.urlsafe_b64decode(
              part["body"]["data"])
          message["body"] = decoded_bytes.decode("UTF-8")
    else:
      message["body"] = ""
    # 件名
    message["subject"] = [
      header["value"]
      for header in detail["payload"]["headers"]
      if header["name"] == "Subject"
    ][0]
    # ヘッダ
    message["headers"] = detail["payload"]["headers"]
    # 追加
    if flat:
      # ヘッダのみ特別処理
      message = {
        k: [v]
          for k, v in message.items()
      }
      message["headers"] = {}
      for header in detail["payload"]["headers"]:
        if header["name"] not in message["headers"]:
          message["headers"][header["name"]] = []
        message["headers"][header["name"]].append(header["value"])
    # 追加範囲をチェックして追加するかどうか決める
    if start_time is not None and \
        "Date" in message["headers"]:
      # Sat, 20 Aug 2022 15:16:15 +0000
      t = datetime.strptime(message["headers"]["Date"][0], "%a, %d %b %Y %H:%M:%S %z")
      if t < start_time:
        continue
    messages.append(message)

  return messages

# GMail用の認証情報を初期化
def _mail_init_gmail(mail_address):
  config.set(KEYS_ACCOUNTS + [mail_address], {
    "type": "gmail",
    "token": {}
  })
  creds = _gmail_get_token(mail_address)

def _mail_init(params):
  # 引数解析
  args = parse_arguments(params, [
    [ "mail_address",        { "help": ""            } ],
    [ "-t", "--type",        { "dest": "type"        } ],
    [ "-u", "--username",    { "dest": "username"    } ],
    [ "-p", "--password",    { "dest": "password"    } ],
    [ "-P", "--pop3-server", { "dest": "pop3_server" } ],
    [ "-I", "--imap-server", { "dest": "imap_server" } ],
  ])
  # 引数解析結果確認
  #print("args",args)
  if args is None:
    return False
  if args.mail_address is None or\
     args.type is None:
    return False
  #
  if "gmail" == args.type:
    _mail_init_gmail(args.mail_address)
  return True

def mail_command(args):
  if len(args) < 1 or "mail" != args[0]:
    return False

  if len(args) <= 2:
    _print_mail_help()
  elif "init" == args[1] \
        and _mail_init(args[2:]):
    return True
  else:
    _print_mail_help()

  return True

def read(mail_address, **options):
  account_type = config.get(KEYS_ACCOUNTS + [mail_address,"type"])
  if "gmail" == account_type:
    return _gmail_get_mail(mail_address, **options)
  return None

if __name__ == "__main__":
  mail_command(["mail"].extend(sys.argv[1:]))
