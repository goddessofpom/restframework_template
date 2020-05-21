port=18888
pid=`lsof -t -i:$port`
if [ $pid ];then 
    kill -9 $pid
fi
python3 manage.py runserver 0.0.0.0:$port

