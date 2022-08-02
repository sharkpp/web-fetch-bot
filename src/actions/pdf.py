# buildin pacakges
from os import makedirs, scandir, path, stat, utime
from datetime import datetime, timezone, timedelta
import re
# 3rd party packages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
# my pacakges
from libraries.file_util import touch_file

"""
actions:
  - name: pdf from dir
    pdf.from_dir:
      in: $DIR_PATH
      out: $PDF_PATH
"""

def _pdf_from_dir(ctx, params):
  try:
    in_dir = ctx.apply_vars(params["in"])
    out_path = ctx.apply_vars(params["out"])
    timestamp = ctx.apply_vars(params["timestamp"]) if "timestamp" in params else None
    base_dir = path.dirname(out_path)
    # PDF生成開始
    if not path.exists(base_dir):
      makedirs(base_dir)
    pagesize = portrait(A4)
    page = canvas.Canvas(\
      out_path, \
      pagesize=pagesize, \
      pageCompression=1 \
    )
    # フォルダ内の画像からPDFを生成
    page_list = []
    with scandir(in_dir) as it:
      for entry in it:
        if entry.is_file() and \
            re.search(r"\.(png|jpg|jpeg|gif)$", entry.name) is not None:
          page_list.append(entry.path)
    page_list.sort()
    for page_file in page_list:
      try:
        page.drawImage(page_file, 0, 0, *pagesize)
        page.showPage()
      except Exception as e:
        print("skip {} by {}".format(entry.name, e))
    # PDFファイルとして保存
    page.save()
    # 日付を変更
    if timestamp is not None:
      # ファイルのタイムスタンプを指定のものに変更
      touch_file(out_path, timestamp)

  except Exception as e:
    print("_for", e)
    return False
  return True

def get_actions():
  """
  Returns a list of the actions it is providing
  """
  return {
    "pdf.from_dir": _pdf_from_dir,
  }
