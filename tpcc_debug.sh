cp -r config_tpcc_debug.h config.h
rm debug.out

wl="TPCC"
threads=16
cnt=100000
penalty=1
wh=1
spin="true"
pf="true"
alg="CLV"
alg="WOUND_WAIT"
alg="WAIT_DIE"
alg="NO_WAIT"
on=2
off=17
phs="true"
phs="false"
tmp="true"
tmp="false"
dynamic="true"
dynamic="false"
debug="false"
#debug="true"
nodist="true"
#nodist="false"
perc=0.5
perc=1
merge="true"
merge="false"
reorder="false"
reorder="true"



for i in 1 2 3
do
for alg in CLV #WOUND_WAIT WAIT_DIE NO_WAIT
do
for threads in 16 8 4 2 1
do
timeout 50 python test.py REORDER_WH=$reorder MERGE_HS=$merge PERC_PAYMENT=$perc DEBUG_BENCHMARK=$nodist DEBUG_CLV=$debug DYNAMIC_TS=$dynamic DEBUG_TMP=$tmp PRIORITIZE_HS=$phs CLV_RETIRE_ON=$on CLV_RETIRE_OFF=$off DEBUG_PROFILING=$pf SPINLOCK=$spin WORKLOAD=${wl} CC_ALG=$alg THREAD_CNT=$threads MAX_TXN_PER_PART=$cnt ABORT_PENALTY=$penalty NUM_WH=${wh}|& tee -a debug.out
done
done
done


#timeout 50 python test.py DEBUG_TMP="false" PRIORITIZE_HS=$phs CLV_RETIRE_ON=$on CLV_RETIRE_OFF=$off DEBUG_PROFILING=$pf SPINLOCK=$spin WORKLOAD=${wl} CC_ALG=$alg THREAD_CNT=$threads MAX_TXN_PER_PART=$cnt ABORT_PENALTY=$penalty NUM_WH=${wh}|& tee -a debug.out
