#!/bin/bash

function print_help() {
  echo "usage: $0 [OPTIONS] LIST_FILE"
  echo "OPTIONS:"
  echo "  -h, --help  show this message"
  echo "  -l LOG_DIR, --log-dir"
  echo "              LOG_DIR  set log output directory"
  echo ""
  echo "LIST_FILE format:"
  echo "|# day  mon week URL"
  echo "|*      *   *     https://example.net/book/list.html"
  echo "|1      *   *     https://example.net/series/index.html"
  exit 1
}

# set base dir
TOOL_DIR=$(dirname $0)
ROOT_DIR=$(realpath $TOOL_DIR/..)

# enable venv
if [ -f  "$TOOL_DIR/.venv/bin/activate"  ]; then
  source "$TOOL_DIR/.venv/bin/activate"
elif [ -f "$ROOT_DIR/.venv/bin/activate"  ]; then
  source  "$ROOT_DIR/.venv/bin/activate"
fi

# parse arguments
OPT_LOG_DIR=./logs
while getopts hl:-: opt option
do
  optarg="$OPTARG"
  if [[ "$opt" = - ]]; then
      opt="-${OPTARG%%=*}"
      optarg="${OPTARG/${OPTARG%%=*}/}"
      optarg="${optarg#=}"
      if [[ -z "$optarg" ]] && [[ ! "${!OPTIND}" = -* ]]; then
          optarg="${!OPTIND}"
          shift
      fi
  fi
  case $option in
    -h|--help)
      print_help ;;
    -l|--log-dir)
      OPT_LOG_DIR=${OPTARG} ;;
    \?)
      echo "This is unexpected option." 1>&2
      print_help
  esac
done
shift `expr "${OPTIND}" - 1`
if [ $# -lt 1 ]; then
  echo "No remaining options."
  print_help
fi

# set list file name
LIST_FILE=$1
if [ ! -f "$LIST_FILE" ]; then
  LIST_FILE=./list.txt
fi
if [ ! -f "$LIST_FILE" ]; then
  echo not found list file
  exit 1
fi

# set log filename
LOG_PATH=$OPT_LOG_DIR/web-fetch-bot-`date +%Y%m%d_%H%M%S`.log

mkdir -p "$OPT_LOG_DIR"

# dump options
(
echo "------------------------------"
echo "LOG DIR  : $OPT_LOG_DIR"
echo "LOG FILE : $LOG_PATH"
echo "LIST FILE: $LIST_FILE"
echo "------------------------------"
) | tee -a $LOG_PATH 1>&2

# failback
_date=date
if type gdate >/dev/null 2>&1; then
  _date=gdate
fi

IFS_HIST=()
function push_ifs() {
  IFS_HIST+=("$IFS")
  IFS="$1"
#echo @IFS=$IFS
#echo @IFS_HIST="${IFS_HIST[@]}"
}
function pop_ifs() {
  local LAST_INDEX=$((${#IFS_HIST[*]} - 1))
  IFS="${IFS_HIST[$LAST_INDEX]}"
  unset IFS_HIST[$LAST_INDEX]
}

# echo ; echo IFS=$(echo "$IFS" | od -tx1) IFS_HIST="${#IFS_HIST[@]}"
# printf '[%s]\n' $(printf "a\tb c,d")
# push_ifs ,
# echo ; echo IFS=$(echo "$IFS" | od -tx1) IFS_HIST="${#IFS_HIST[@]}"
# printf '[%s]\n' $(printf "a\tb c,d")
# push_ifs " "
# echo ; echo IFS=$(echo "$IFS" | od -tx1) IFS_HIST="${#IFS_HIST[@]}"
# printf '[%s]\n' $(printf "a\tb c,d")
# pop_ifs
# echo ; echo IFS=$(echo "$IFS" | od -tx1) IFS_HIST="${#IFS_HIST[@]}"
# printf '[%s]\n' $(printf "a\tb c,d")
# pop_ifs
# echo ; echo IFS=$(echo "$IFS" | od -tx1) IFS_HIST="${#IFS_HIST[@]}"
# printf '[%s]\n' $(printf "a\tb c,d")

function cron() {
  local RANGE
  local ITEM
  local LIST
  local STEP
  
  local URL=$1
  local DAYS=$2
  local MONTHS=$3
  local DoWS=$3
  if [ "7" == "$DoWS" ]; then DoWS=0 ; fi
  # 0=Sunday, 1=Monday, ...

  # get today part
  local TODAY_DAY=$($_date +"%d")
  local TODAY_MONTH=$($_date +"%m")
  local TODAY_MONTH=${TODAY_MONTH#0}
  local TODAY_DoW=$(LANG=C $_date +"%u")
  if [ "7" == "$TODAY_DoW" ]; then TODAY_DoW=0 ; fi
  #echo $TODAY_DAY $TODAY_MONTH $TODAY_DoW
  local MATCH=0 # full match is 7
  for TYPE in DAYS MONTHS DoW
  do
    set -f # disable * expand
    ITEM=
    LIST=
    case $TYPE in
      "DAYS")   ITEM=$DAYS
                LIST=$(eval "echo {1..$(echo $($_date +"%d" -d"`$_date +"%Y%m01"` 1 days ago + 1 month"))}")
                ;;
      "MONTHS") ITEM=$MONTHS
                LIST="1 2 3 4 5 6 7 8 9 10 11 12"
                ;;
      "DoW")    ITEM=$DoWS
                LIST="0 1 2 3 4 5 6"
                ;;
    esac
    if [ "" == "$ITEM" ]; then
      continue
    fi
    #echo "$TYPE / $ITEM / $LIST"
    #
    push_ifs "/"
    ITEM=($ITEM)
    STEP=${ITEM[1]}
    if [ "*" == "$ITEM" ]; then
      ITEM=$LIST
    fi
    if [ "" == "$STEP" ]; then STEP=1 ; fi
    pop_ifs
    #echo "@= $ITEM ${ITEM[@]}"
    # N-M format expand
    RANGE=$(eval "echo {${ITEM//-/..}}")
    RANGE=${RANGE#\{}
    RANGE=${RANGE%\}}
    push_ifs " "
    RANGE=($RANGE)
    pop_ifs
    for I in $(seq 0 $STEP $(( ${#RANGE[@]} - 1 ))) ; do
      #echo "@@ $TYPE ${RANGE[$I]} $TODAY_DAY $TODAY_MONTH $TODAY_DoW "
      case $TYPE in
        "DAYS")   if [ ${RANGE[$I]} -eq $TODAY_DAY   ]; then MATCH=$(( $MATCH | 1 )) ; fi ;;
        "MONTHS") if [ ${RANGE[$I]} -eq $TODAY_MONTH ]; then MATCH=$(( $MATCH | 2 )) ; fi ;;
        "DoW")    if [ ${RANGE[$I]} -eq $TODAY_DoW   ]; then MATCH=$(( $MATCH | 4 )) ; fi ;;
      esac
    done
    set +f
  done
  #  
  #echo $MATCH
  if [ $MATCH -ne 7 ]; then
    # 対象外
    echo "TARGET  : $URL"
    echo "STATUS  : SKIP"
    echo "SKIP-----------: $URL" 1>&2
  else
    # check today and target
    echo "TARGET  : $URL"
    t0=$($_date +'%s.%3N')
    python3 $ROOT_DIR/src/main.py -vv $1 2>&1
    #sleep 1
    t1=$($_date +'%s.%3N')
    td=$(echo $(($(echo $t1 - $t0 | sed -e "s/\.//g"))) | sed -e "s/\(...\)$/.\1/g" -e "s/^\./0./g")
    echo "START   : $($_date -d "@${t0}" +'%Y-%m-%d %H:%M:%S.%3N (%:z)')"
    echo "END     : $($_date -d "@${t1}" +'%Y-%m-%d %H:%M:%S.%3N (%:z)')"
    eval "echo ELAPSED : -------- $($_date -ud "@$td" +'$((%s/3600/24)) %H:%M:%S.%3N')"
    echo "STATUS  : COMPLETE"
    echo "$(eval "echo $($_date -ud "@$td" +'$((%s/3600/24))d %H:%M:%S.%3N')"): $URL" 1>&2
  fi
  echo "------------------------------"
}

cat $LIST_FILE | grep -vE "^\s*#" | \
while read DAY MONTH DoW URL ; do
  #echo DAY=$DAY MONTH=$MONTH DoW=$DoW URL=$URL
  if [ "" != "$URL" ]; then
    # stdout ... to log file
    # stderr ... to termal
    cron "$URL" "$DAY" "$MONTH" "$DoW"
  fi
done >> $LOG_PATH
