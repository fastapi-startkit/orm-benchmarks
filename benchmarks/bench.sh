#!/bin/sh

export ITERATIONS=100
if [ "x$1" == "xfull" ]; then
    export ITERATIONS=1000
fi
if [ "x$1" == "xextra" ]; then
    export ITERATIONS=10000
fi

cd $(dirname $0)

echo Iterations: $ITERATIONS


echo Test 1
export TEST=1
printf '' > outfile1

sqlalchemy_async/bench.sh | tee -a outfile1
fastapi_startkit/bench.sh | tee -a outfile1


echo Test 2
export TEST=2
printf '' > outfile2

sqlalchemy_async/bench.sh | tee -a outfile2
fastapi_startkit/bench.sh | tee -a outfile2


echo Test 3
export TEST=3
printf '' > outfile3

sqlalchemy_async/bench.sh | tee -a outfile3
fastapi_startkit/bench.sh | tee -a outfile3

echo `python -V`, Iterations: $ITERATIONS DBtype: $DBTYPE | tee -a results
cat outfile1 | ./present.py "Test 1" | tee -a results
cat outfile2 | ./present.py "Test 2" | tee -a results
cat outfile3 | ./present.py "Test 3" | tee -a results
echo | tee -a results
