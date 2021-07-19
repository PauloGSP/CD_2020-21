#!/usr/bin/env bash

N=${1:-100}
C=${2:-5}
MIN=${3:-100}

K=$(($N / $C))

echo -e "Stress test Load Balancer "

PID_LIST=""

START=$(date +%s)
for i in $(seq $C)
do
  MAX=$(($MIN + $K))
  curl -s "http://localhost:8080/[$MIN-$MAX]" > /dev/null 2>&1 & 
  PID=$!
  PID_LIST="$PID_LIST $PID"
  echo -e "Requests [$MIN-$MAX] ($PID)"
  MIN=$MAX
done

FAIL=0
for PID in $PID_LIST; 
do
  echo -e "Wait for $PID..."    
  wait $PID || let "FAIL+=1" 
done
END=$(date +%s)

if [ "$FAIL" == "0" ]; then 
  echo "YAY!"
  TIME=$(echo "($END - $START)" | bc -l)
  RPS=$(echo "$N / $TIME" | bc)
  echo -e "Requests Per Second = $RPS ($TIME)"
else 
  echo "FAIL! ($FAIL)" 
fi