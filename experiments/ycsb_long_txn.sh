cd ..
#rm outputs/stats.json

zipf=0.9
for l in 0.15 #0
do
for thd in 16 # 120 96 64 32 16 8 4 2 1
do
for i in 0 #1 2 3 4
do
for alg in WAIT_DIE #BAMBOO SILO WOUND_WAIT NO_WAIT #WAIT_DIE
do
		python test.py experiments/long_txn.json BB_LAST_RETIRE=$l THREAD_CNT=${thd} ZIPF_THETA=${zipf} CC_ALG=${alg} OUTPUT_TO_FILE=true CPU_FREQ=2.8 
done
done
done
done

fname="ycsb-long-txn_wd"
cd outputs/
python collect_stats.py
mv stats.csv ycsb_long_txn/${fname}.csv
mv stats.json ycsb_long_txn/${fname}.json
cd ..

cd experiments
# python3 send_email.py ${fname}
