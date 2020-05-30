import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import simulator
from multiprocessing.pool import ThreadPool
import math
import numpy as np
import sys
import builders
import copy

def builder_simple():
    sim_builder = builders.SimulatorBuilder()
    sim_builder.with_agregation_type('count')
    # nodos ficam com resultados diferentes
    #sim_builder.with_self_termination_by_rounds(50)
    #sim_builder.with_self_termination_by_min_dif(50, 0.01)
    #sim_builder.with_timeout_protocol(100)
    #inputs_by_node = dict.fromkeys(range(len(G)), 2)
    #sim_builder.with_scheduled_change_inputs_event(inputs_by_node, 5)
    #sim_builder.with_scheduled_add_members_event(1,1,1,2,False,10)
    return sim_builder

def builde_super_dict(sim_builders):
    global_results = {}
    for key in sim_builders:
        global_results[key] = build_dict()
    
    return global_results


def build_dict():
    results = {}
    results['step_axis'] = [] 
    results['med_messages'] = []
    results['med_rounds'] = []
    results['max_messages'] = []
    results['min_messages'] = []
    results['max_rounds'] = []
    results['min_rounds'] = []

    return results


def simulate_single_nodes_step(n, graph, inputs, sim_name, sim_builder, global_results, iter_size):
    global_results[sim_name]['step_axis'].append(n)
    min_r = min_m = sys.maxsize
    max_r = max_m = -1
    med_r = med_m = 0

    for i in range(iter_size):

        builder = copy.deepcopy(sim_builder)
        
        t, m, r = builder.build(graph, inputs).start()

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

    global_results[sim_name]['med_messages'].append(med_m / iter_size)
    global_results[sim_name]['med_rounds'].append(med_r / iter_size)
    global_results[sim_name]['max_messages'].append(max_m)
    global_results[sim_name]['min_messages'].append(min_m)
    global_results[sim_name]['max_rounds'].append(max_r)
    global_results[sim_name]['min_rounds'].append(min_r)

    return global_results

# Retorna [sim_dict] 
# sim_dict = {}

def thread_execution_rmse_step(rmse_list, graph, sim_builders, iter_size):
    global_results = builde_super_dict(sim_builders)

    inputs = [1] * len(G)

    for r in rmse_list:
        for sim_name, sim_builder in sim_builders.items():
            aux_builder = copy.deepcopy(sim_builder)
            sim = sim_builder.with_confidence_value(rmse_list)
            simulate_single_rmse_step(r, sim, )




def thread_execution_nodes_step(n_list, degree, iter_size, sim_builders, sync_value = None):
    global_results = builde_super_dict(sim_builders)

    for n in n_list:
        if sync_value is None:
            G = graphGen.randomG(n, degree)
        else:
            G = graphGen.randomG(n, degree, sync_value)

        # mudar aqui para fazer Contagem
        
        for sim_name, sim_builder in sim_builders.items():
            aux_builder = copy.deepcopy(sim_builder)
            if aux_builder.simulator.aggregation_type == 'average':
                inputs = [1] * len(G)
            else:
                inputs = [0] * (len(G) - 1) + [1]

            simulate_single_nodes_step(n, G, inputs, sim_name, aux_builder, global_results, iter_size)

    return global_results


#(l, 3, 3, builders, 10)
def execution(n_min, n_max, step, n_threads, sim_builders, thread_args):
    n_list = list(range(n_min, n_max, step))
    print(len(n_list), n_threads)
    slice_size = math.ceil(len(n_list) / n_threads)
    results = []
    pool = ThreadPool(n_threads)

    for i in range(0, len(n_list), slice_size):
        l = n_list[i : i  + slice_size]
        print(l)
        results.append( pool.apply_async(thread_execution_nodes_step, args=  ((l,) + thread_args)))

    pool.close()
    pool.join()

    final_results = {}
    for key in sim_builders:
        final_results[key] = build_dict()
    
    for r in results:
        r_dict = r.get()
        for sim in r_dict:
            final_results[sim]['step_axis'] += r_dict[sim]['step_axis']  
            final_results[sim]['med_messages'] += r_dict[sim]['med_messages']
            final_results[sim]['med_rounds'] += r_dict[sim]['med_rounds']
            final_results[sim]['max_messages'] += r_dict[sim]['max_messages']
            final_results[sim]['min_messages'] += r_dict[sim]['min_messages']
            final_results[sim]['max_rounds'] += r_dict[sim]['max_rounds']
            final_results[sim]['min_rounds'] += r_dict[sim]['min_rounds'] 

    #plt.plot(final_results['normal']['nodes'], final_results['normal']['med_messages'])
    #plt.show()

    return final_results


if __name__ == '__main__': 
    b1 = builder_simple()
    b2 = builder_simple()
    b3 = builder_simple()
    
    builders = {'simples1' : b1, 'simples2' : b2, 'simples3' : b3}
    
    #(degree, iter_size, ..., sync_value (None if async))
    thread_args = (3, 1, builders, 10)
    
    #(n_min, n_max, step, n_threads, ..., ...)
    final_results = execution(5, 10, 2, 1, builders, thread_args)
    
    print(final_results)
