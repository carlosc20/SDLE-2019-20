import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import simulator
from multiprocessing.pool import ThreadPool
import math
import numpy as np
import sys
import builders

def simulator_simple(G, inputs):
    sim_builder = builders.SimulatorBuilder()
    sim_builder.with_loss_rate(0).with_agregation_type('average')
    sim_builder.with_flowsums_termination()
    # nodos ficam com resultados diferentes
    #sim_builder.with_self_termination_by_rounds(50)
    #sim_builder.with_self_termination_by_min_dif(50, 0.01)
    #sim_builder.with_timeout_protocol(100)
    #inputs_by_node = dict.fromkeys(range(len(G)), 2)
    #sim_builder.with_scheduled_change_inputs_event(inputs_by_node, 5)
    #sim_builder.with_scheduled_add_members_event(1,1,1,2,False,10)
    sim = sim_builder.build(G, inputs)
    return sim.start()

def build_dict():
    results = {}
    results['nodes'] = [] 
    results['med_messages'] = []
    results['med_rounds'] = []
    results['max_messages'] = []
    results['min_messages'] = []
    results['max_rounds'] = []
    results['min_rounds'] = []

    return results


def thread_execution(n_list):
    results = build_dict()

    iter_size = 3

    for n in n_list:
        results['nodes'].append(n)
        min_r = min_m = sys.maxsize
        max_r = max_m = -1
        med_r = med_m = 0
        for i in range(iter_size):
            G = graphGen.randomG(n,3,10)
            inputs = [1] * len(G)
            #nx.draw(G, with_labels=True)
            #plt.show()
            
            t, m, r = simulator_simple(G, inputs)

            if m < min_m:
                min_m = m

            if m > max_m:
                max_m = m

            if r < min_r:
                min_r = r

            if r > max_r:
                max_r = r

            med_r += r
            med_m += m
        
        results['med_messages'].append(med_m / iter_size)
        results['med_rounds'].append(med_r / iter_size)
        results['max_messages'].append(max_m)
        results['min_messages'].append(min_m)
        results['max_rounds'].append(max_r)
        results['min_rounds'].append(min_r)

    return results


def execution(n_min, n_max, step, n_threads):
    n_list = list(range(n_min, n_max, step))
    print(len(n_list), n_threads)
    slice_size = math.ceil(len(n_list) / n_threads)
    results = []
    pool = ThreadPool(n_threads)

    for i in range(0, len(n_list), slice_size):
        print (i)
        l = n_list[i : i  + slice_size]
        print(l)
        results.append( pool.apply_async(thread_execution, args= (l,)))

    pool.close()
    pool.join()

    final_results = build_dict()
    
    for r in results:
        r_dict = r.get()
        final_results['nodes'] += r_dict['nodes']  
        final_results['med_messages'] += r_dict['med_messages']
        final_results['med_rounds'] += r_dict['med_rounds']
        final_results['max_messages'] += r_dict['max_messages']
        final_results['min_messages'] += r_dict['min_messages']
        final_results['max_rounds'] += r_dict['max_rounds']
        final_results['min_rounds'] += r_dict['min_rounds'] 


    return final_results




if __name__ == '__main__': 
    results = execution(10,20,5,2)
    plt.plot(results['nodes'], results['med_messages'])
    print(results)
    plt.show()