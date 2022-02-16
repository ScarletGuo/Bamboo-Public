#pragma once 

#include "global.h"

class workload;
class ycsb_query;
class tpcc_query;
class ycsb_request;

extern thread_local drand48_data per_thread_rand_buf;

class base_query {
public:
	virtual void init(uint64_t thd_id, workload * h_wl) = 0;
	uint64_t waiting_time;
	uint64_t part_num;
	uint64_t * part_to_access;
	bool rerun;
#if CC_ALG == SILO_PRIO
	uint32_t num_abort = 0;
	uint32_t prio = 0;
	// note prio may be overwritten by subclass to support more complicated
	// priority distribution, e.g. long-running txn
#endif
};

// All the querise for a particular thread.
class Query_thd {
public:
	void init(workload * h_wl, int thread_id);
	base_query * get_next_query(); 
	uint64_t q_idx;
#if WORKLOAD == YCSB
	ycsb_query * queries;
    ycsb_request * long_txn;
    uint64_t * long_txn_part;
#else 
	tpcc_query * queries;
#endif
	char pad[CL_SIZE - sizeof(void *) - sizeof(int)];
	drand48_data buffer;
	uint64_t request_cnt;
};

// TODO we assume a separate task queue for each thread in order to avoid 
// contention in a centralized query queue. In reality, more sofisticated 
// queue model might be implemented.
class Query_queue {
public:
	void init(workload * h_wl);
	void init_per_thread(int thread_id);
	base_query * get_next_query(uint64_t thd_id); 
	
private:
	static void * threadInitQuery(void * This);

	Query_thd ** all_queries;
	workload * _wl;
	static int _next_tid;
};
