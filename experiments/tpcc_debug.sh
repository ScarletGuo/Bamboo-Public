cp -r config_tpcc_debug.h config.h
rm temp.out
rm debug.out

merge="false"
bench="false"
reorder="true"
reorder="false"
wl="TPCC"
threads=16 
cnt=100000
penalty=100000 
penalty=0
wh=1
spin="true"
pf="true"
#pf="false"
dynamic="false"
dynamic="true"
debug="false"
retire="true"
perc=0.5
alg="CLV"
#alg="WOUND_WAIT"
tmp="true"
tmp="false"
on=1
delay=10
delay=0
dt=4
#batch_return="true"

timeout 30 python test.py DELAY_THRESHOLD=$dt DELAY_ACQUIRE=$delay MERGE_HS=$merge CLV_RETIRE_ON=$on DEBUG_TMP=$tmp RETIRE_ON=$retire REORDER_WH=$reorder PERC_PAYMENT=$perc DEBUG_BENCHMARK=$bench DEBUG_CLV=$debug DYNAMIC_TS=$dynamic DEBUG_PROFILING=$pf SPINLOCK=$spin WORKLOAD=${wl} CC_ALG=$alg THREAD_CNT=$threads MAX_TXN_PER_PART=$cnt ABORT_PENALTY=$penalty NUM_WH=${wh}|& tee -a debug.out


#for i in 0 1 2
#do
#for threads in 1 2 4 8 16
#do
#for wh in 1 2 4 8 16
#do
#for perc in 0 0.5 1
#do
#for alg in CLV WOUND_WAIT WAIT_DIE NO_WAIT
#do
#timeout 50 python test.py RETIRE_ON=$retire REORDER_WH=$reorder PERC_PAYMENT=$perc DEBUG_BENCHMARK=$bench DEBUG_CLV=$debug DYNAMIC_TS=$dynamic DEBUG_PROFILING=$pf SPINLOCK=$spin WORKLOAD=${wl} CC_ALG=$alg THREAD_CNT=$threads MAX_TXN_PER_PART=$cnt ABORT_PENALTY=$penalty NUM_WH=${wh}|& tee -a debug.out
#done
#done
#done
#done
#done