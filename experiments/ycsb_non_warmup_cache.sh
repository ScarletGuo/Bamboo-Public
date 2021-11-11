cd ..
#rm outputs/stats.json

for alg in NO_WAIT SILO 
do
for read_perc in 0.5
do
for thd in 32 16 8 4 2 1 # 120 96 64 32 16 8 4 2 1
do
for zipf in 0.9 # 0.3 0.5 0.7 0.9 0.999
do
		python test.py experiments/non_warmup_cache.json THREAD_CNT=${thd} ZIPF_THETA=${zipf} CC_ALG=${alg} READ_PERC=${read_perc} OUTPUT_TO_FILE=true 
done
done
done
done

fname="ycsb_non_warmup_cache"
cd outputs/
python collect_stats.py
mv stats.csv ${fname}/${fname}_readperc0.5.csv
mv stats.json ${fname}/${fname}_readperc0.5.json
cd ..

# cd experiments
# python3 send_email.py ${fname}
