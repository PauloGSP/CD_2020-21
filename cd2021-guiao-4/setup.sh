#!/usr/bin/env bash

N_SERVERS=${1:-4} 
POLICY=${2:-N2One}

# delete old pid file
rm -f http_server.pid

echo -e Start $N_SERVERS Http Servers

SERVERS=""

for ((i = 0 ; i < $N_SERVERS ; i++ ));
do 
  PORT=$((5000 + $i))
  SERVERS="$SERVERS$PORT "
  python3 http_server.py -p $PORT > /dev/null 2>&1 & 
  PID=$! 
  echo $PID >> http_server.pid
  echo -e "\tStart HTTP Server localhost:$PORT ($PID)"
done

echo -e Start Load Balancer: $SERVERS

python3 load_balancer.py -p 8080 -s $SERVERS -a $POLICY

echo -e Stop $N_SERVERS Http Servers

for PID in $(cat http_server.pid);
do
    echo -e "\tKill -9 $PID"
    kill -9 $PID
    wait $PID 2>/dev/null
done

rm -f http_server.pid