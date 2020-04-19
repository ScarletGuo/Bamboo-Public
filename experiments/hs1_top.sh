cd ../
cp -r config_ycsb_synthetic.h config.h

# algorithm
alg=WOUND_WAIT
spin="true"
# [WW]
ww_starv_free="false"
# [BAMBOO]
dynamic="true"
on=0
retire_read="false"

# workload
wl="YCSB"
req=16
synthetic=true
zipf=0
num_hs=1
pos=TOP
specified=0
fixed=1
fhs="WR"
shs="WR"
read_ratio=1
ordered="false"
flip=0
table_size="1024*1024*20"

# other
threads=16
profile="true"
cnt=100000 
penalty=50000

retire_off_opt="true"
# figure 4: normalized throughput with optimal case, varying requests
for retire_off_opt in true false
do
for i in 0 1 2 3 4
do
for alg in BAMBOO #WOUND_WAIT WAIT_DIE NO_WAIT SILO
do
for threads in 1 2 4 8 16 32
do
for req in 4 16 64
do
timeout 500 python test.py CLV_RETIRE_OFF=${retire_off_opt} RETIRE_READ=${retire_read} FIXED_HS=${fixed} FLIP_RATIO=${flip} SPECIFIED_RATIO=${specified} WW_STARV_FREE=${ww_starv_free} KEY_ORDER=$ordered READ_PERC=${read_ratio} NUM_HS=${num_hs} FIRST_HS=$fhs POS_HS=$pos DEBUG_TMP="false" DYNAMIC_TS=$dynamic CLV_RETIRE_ON=$on SPINLOCK=$spin REQ_PER_QUERY=$req DEBUG_PROFILING=$profile SYNTH_TABLE_SIZE=${table_size} WORKLOAD=${wl} CC_ALG=$alg THREAD_CNT=$threads MAX_TXN_PER_PART=$cnt ABORT_PENALTY=$penalty ZIPF_THETA=$zipf SYNTHETIC_YCSB=$synthetic 
done
done
done
done
done

cd outputs/
python3 collect_stats.py
mv stats.csv hs1_top/hs1_top.csv
mv stats.json hs1_top_clv.json
cd ..

python experiments/send_email.py node0_hs1
