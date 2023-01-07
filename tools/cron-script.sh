#!/bin/bash

function print_help() {
  echo "usage: $0 [OPTIONS] LIST_FILE"
  echo "OPTIONS:"
  echo "  -h, --help  show this message"
  echo "  -f, --force"
  echo "  -l LOG_DIR, --log-dir LOG_DIR"
  echo "              LOG_DIR  set log output directory"
  echo "  -d DATE, --date DATE"
  echo "              DATE  set date, default is current date"
  echo "  -n, --dry-run"
  echo "              not effective"
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
OPT_DATE=
OPT_DRY_RUN=0
OPT_FORCE=0
while getopts hnfl:d:-: OPTION
do
  OPTARG_="$OPTARG"
  # support long option by '-' option
  if [[ "$OPTION" = - ]]; then
      OPTION="-${OPTARG%%=*}"
      OPTARG_="${OPTARG_/${OPTARG%%=*}/}"
      OPTARG_="${OPTARG_#=}"
      if [[ -z "$OPTARG_" ]] && [[ ! "${!OPTIND}" = -* ]]; then
          OPTARG_="${!OPTIND}"
          shift
      fi
  fi
  case "-$OPTION" in
    -h|--help)
      print_help ;;
    -l|--log-dir)
      OPT_LOG_DIR=${OPTARG_} ;;
    -d|--date)
      OPT_DATE="-d ${OPTARG_}" ;;
    -n|--dry-run)
      OPT_DRY_RUN=1 ;;
    -f|--force)
      OPT_FORCE=1 ;;
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
if [ 0 -ne $OPT_DRY_RUN ]; then
  echo "DRY RUN  : true"
fi
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
  local OPT
  
  local URL=$1
  local DAYS=$2
  local MONTHS=$3
  local DoWS=$4
  local SUBDIR=$5
  if [ "" != "$SUBDIR" ]; then
    OPT="$OPT --sub-dir $SUBDIR"
  fi
  if [ "7" == "$DoWS" ]; then DoWS=0 ; fi
  # 0=Sunday, 1=Monday, ...

  # get today part
  local TODAY_DAY=$($_date $OPT_DATE +"%d")
  local TODAY_MONTH=$($_date $OPT_DATE +"%m")
  local TODAY_MONTH=${TODAY_MONTH#0}
  local TODAY_DoW=$(LANG=C $_date $OPT_DATE +"%u")
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
                LIST=$(eval "echo {1..$(echo $($_date $OPT_DATE +"%d" -d"`$_date $OPT_DATE +"%Y%m01"` 1 days ago + 1 month"))}")
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
    #echo "SKIP-----------: $URL" 1>&2
  else
    # check today and target
    echo "TARGET  : $URL"
    echo "$URL" 1>&2
    t0=$($_date +'%s.%3N')
    if [ 0 -eq $OPT_DRY_RUN ]; then
#     python3 $ROOT_DIR/src/main.py -vv $1 2>&1
      (
        python3 $ROOT_DIR/src/main.py $OPT -vv $1 2>&1 | \
          tee /dev/stderr ) 2> >( grep "完了 " | sed -e "s/^/  /g" 1>&2 )
    fi
    #sleep 1
    t1=$($_date +'%s.%3N')
    td=$(echo $(($(echo $t1 - $t0 | sed -e "s/\.//g"))) | sed -e "s/\(...\)$/.\1/g" -e "s/^\./0./g")
    echo "START   : $($_date -d "@${t0}" +'%Y-%m-%d %H:%M:%S.%3N (%:z)')"
    echo "END     : $($_date -d "@${t1}" +'%Y-%m-%d %H:%M:%S.%3N (%:z)')"
    eval "echo ELAPSED : -------- $($_date -ud "@$td" +'$((%s/3600/24)) %H:%M:%S.%3N')"
    echo "STATUS  : COMPLETE"
    #echo "$(eval "echo $($_date -ud "@$td" +'$((%s/3600/24))d %H:%M:%S.%3N')"): $URL" 1>&2
    echo "  >> $(eval "echo $($_date -ud "@$td" +'$((%s/3600/24))d %H:%M:%S.%3N')")" 1>&2
  fi
  echo "------------------------------"
}

# stdout -> $LOG_PATH
# stderr -> console
cat $LIST_FILE | grep -vE "^\s*#" | \
while read DAY MONTH DoW URL SUBDIR ; do
  #echo DAY=$DAY MONTH=$MONTH DoW=$DoW URL=$URL
  if [ "" != "$URL" ]; then
    # stdout ... to log file
    # stderr ... to termal
    if [ 0 -ne $OPT_FORCE ]; then
      cron "$URL" "*" "*" "*" ""
    else
      cron "$URL" "$DAY" "$MONTH" "$DoW" "$SUBDIR"
    fi
  fi
done >> $LOG_PATH
