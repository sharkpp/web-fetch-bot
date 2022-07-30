# buildin pacakges
import re

PatternString = r'"((?:[^\\"]+|\\.)*)"'
PatternNumber = r'(?:([0#]+)(?:.([0#]+))?)'
PatternNumberWithZero = r'(?:(0+)(?:.(0+))?)'
PatternNumberWithSpace = r'(?:(#+)(?:.(#+))?)'

def format(pattern, value):
  # 文字列
  match_string = re.findall(PatternString, pattern)
  pattern = re.sub(PatternString, "{}", pattern)
  # 数値
  match_number = re.findall(PatternNumber, pattern)
  if match_number is not None:
    #print(pattern,value,match_number)
    #return ""
    (number_integer_part, number_decimal_part) = (str(value) + ".").split(".")[0:2]
    (match_number_integer_part, match_number_decimal_part) = list(match_number[0])
    #print(">>",(number_integer_part, number_decimal_part),(match_number_integer_part, match_number_decimal_part))
    # 整数部の桁合わせ
    number_width = len(match_number_integer_part) - len(number_integer_part)
    number_integer_part_str = ""
    if number_width < 0: # 桁が多い
      number_integer_part_str = number_integer_part
    elif 0 < len(match_number_integer_part):
      c = ("0" if "0" == match_number_integer_part[0] else " ")
      number_integer_part_str = "".join([c * number_width]) + number_integer_part
    # 少数部の桁合わせ
    number_width = len(match_number_decimal_part) - len(number_decimal_part)
    number_decimal_part_str = ""
    if number_width < 0: # 桁が多い
      number_decimal_part_str = number_decimal_part
    elif 0 < len(match_number_decimal_part):
      c = ("0" if "0" == match_number_decimal_part[0] else " ")
      number_decimal_part_str = number_decimal_part + "".join([c * number_width])
    # 数値書き換え
    pattern = re.sub(PatternNumber, "\x7F", pattern)
    pattern = re.sub(
      r"\x7F", 
      number_integer_part_str + \
        (("." + number_decimal_part_str) if "" != number_decimal_part_str else ""),
      pattern, count=1
    )
    pattern = re.sub(r"\x7F", "", pattern)

  return pattern.format(*match_string)
