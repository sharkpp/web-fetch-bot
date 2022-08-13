# buildin pacakges
import sys
# 3rd party packages
# my pacakges

def mail_command(args):
  if len(args) < 1 or "mail" != args[0]:
    return False
  if len(args) <= 1:
    return True

  print(args)


  return True

if __name__ == '__main__':
  mail_command(["mail"].extend(sys.argv[1:]))
