svr_port=5003
cur_dir=$(pwd)

run_status=$(/usr/sbin/lsof -nP -i TCP:$svr_port |grep python)

if [[ ${#run_status} > 0 ]];
then
    echo 'dingdian still running, '${#run_status}
    exit 0
else
    nohup /usr/local/python3.6/bin/python3.6 dingd.py --manage run --port $svr_port > /dev/null 2>&1 &
    echo 'dingdian stop('${#run_status}'), start work!'$(date +"%H:%M:%S")
fi

