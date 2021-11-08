cd ..
#rm outputs/stats.json

for alg in NO_WAIT SILO 
do
for read_perc in 0.9
do
for thd in 32 16 8 4 2 1 # 120 96 64 32 16 8 4 2 1
do
for zipf in 0.9 0.999 1.3 1.5 2.0
do
		python test.py experiments/non_warmup_cache.json THREAD_CNT=${thd} ZIPF_THETA=${zipf} CC_ALG=${alg} READ_PERC=${read_perc} OUTPUT_TO_FILE=true 
done
done
done
done

fname="ycsb_non_warmup_cache"
cd outputs/
python collect_stats.py
mv stats.csv ${fname}/${fname}.csv
mv stats.json ${fname}/${fname}.json
cd ..

cd experiments
# python3 send_email.py ${fname}
