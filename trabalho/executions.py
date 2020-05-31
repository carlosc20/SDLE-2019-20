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

class SingleSimulation:
    def __init__(self, input_len):
        self.min_r = self.min_m = sys.maxsize
        self.max_r = self.max_m = -1
        self.med_r = self.med_m = 0
        self.med_n_e = []
        self.med_c_r = 0
        self.input_len = input_len
        self.iter = 0

    def simulate_single(self, graph, inputs, sim_builder):
        builder = copy.deepcopy(sim_builder)

        sim = builder.build(graph, inputs)
        t, m, r, n_e, c_r = sim.start()

        if m < self.min_m:
            self.min_m = m

        if m > self.max_m:
            self.max_m = m

        if r < self.min_r:
            self.min_r = r

        if r > self.max_r:
            self.max_r = r

        if not self.med_n_e:
            self.med_n_e = n_e

        self.med_c_r += max(c_r)

        print(self.iter, c_r)
        print(self.iter, self.med_c_r)
        self.iter += 1
        
        self.med_r += r
        self.med_m += m


    def get_results(self, step, iter_size, sim_name, global_results, n_nodes):
        global_results[sim_name]['step_axis'].append(step)
        global_results[sim_name]['med_messages'].append(self.med_m / iter_size)
        global_results[sim_name]['med_rounds'].append(self.med_r / iter_size)
        global_results[sim_name]['max_messages'].append(self.max_m)
        global_results[sim_name]['min_messages'].append(self.min_m)
        global_results[sim_name]['max_rounds'].append(self.max_r)
        global_results[sim_name]['min_rounds'].append(self.min_r)
        global_results[sim_name]['nodes_estimates'].append(self.med_n_e)
        global_results[sim_name]['nodes_consecutive_rounds'].append(self.med_c_r / iter_size)



def builder_simple():
    sim_builder = builders.SimulatorBuilder()
    sim_builder.with_agregation_type('count').with_evaluated_multicast_protocol(1)
    #sim_builder.with_departure_arrivel_members_event(2,10,False)
    # nodos ficam com resultados diferentes
    #sim_builder.with_self_termination_by_rounds(50)
    #sim_builder.with_self_termination_by_min_dif(50, 0.01)
    #sim_builder.with_timeout_protocol(100)
    #inputs_by_node = dict.fromkeys(range(len(G)), 2)
    #sim_builder.with_scheduled_change_inputs_event(inputs_by_node, 5)
    #sim_builder.with_scheduled_add_members_event(1,1,1,2,False,10)
    return sim_builder


def builder_for_consecutive_rounds():
    sim_builder = builders.SimulatorBuilder()
    sim_builder.with_agregation_type('count').with_min_dif_testing(0.01)

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
    results['nodes_estimates'] = []
    results['nodes_consecutive_rounds'] = []

    return results


def simulate_single_for_rmse(step, graph_list, inputs, sim_name, sim_builder, global_results):
    global_results[sim_name]['step_axis'].append(step)
    min_r = min_m = sys.maxsize
    max_r = max_m = -1
    med_r = med_m = 0
    med_n_e = []
    med_c_r = [0] * len(inputs)

    for g in graph_list:

        builder = copy.deepcopy(sim_builder)
        
        t, m, r, n_e, c_r = builder.build(g, inputs).start()

        if m < min_m:
            min_m = m

        if m > max_m:
            max_m = m

        if r < min_r:
            min_r = r

        if r > max_r:
            max_r = r

        if not med_n_e:
            med_n_e = n_e

        for j in range(len(g)):
            med_c_r[j] += c_r[j]
        
        med_r += r
        med_m += m

    global_results[sim_name]['med_messages'].append(med_m / len(graph_list))
    global_results[sim_name]['med_rounds'].append(med_r / len(graph_list))
    global_results[sim_name]['max_messages'].append(max_m)
    global_results[sim_name]['min_messages'].append(min_m)
    global_results[sim_name]['max_rounds'].append(max_r)
    global_results[sim_name]['min_rounds'].append(min_r)
    global_results[sim_name]['nodes_estimates'].append(med_n_e)
    global_results[sim_name]['nodes_consecutive_rounds'].append((sum(med_c_r) / len(graph_list)) /len(graph_list[0]))

    return global_results

# Retorna [sim_dict] 
# sim_dict = {}

def thread_execution_rmse_step(rmse_list, graph_list, sim_builders):
    global_results = builde_super_dict(sim_builders)

    for r in rmse_list:
        for sim_name, sim_builder in sim_builders.items():
            if sim_builder.simulator.aggregation_type == 'average':
                inputs = [1] * len(graph_list[0])
            else:
                inputs = [0] * (len(graph_list[0]) - 1) + [1]
            aux_builder = copy.deepcopy(sim_builder)
            aux_builder = sim_builder.with_confidence_value(r)
            simulate_single_for_rmse(r, graph_list, inputs, sim_name, aux_builder, global_results)

    return global_results



def thread_execution_nodes_step(n_list, degree, iter_size, sim_builders, sync_value = None):
    global_results = builde_super_dict(sim_builders)

    single_simulation = {}
    for n in n_list:
        for sim_name in sim_builders:
            single_simulation[sim_name] = SingleSimulation(n)
        for i in range(iter_size):
            if sync_value is None:
                G = graphGen.randomG(n, degree)
            else:
                G = graphGen.randomG(n, degree, sync_value)

            # mudar aqui para fazer Contagem
            
            for sim_name, sim_builder in sim_builders.items():
                if sim_builder.simulator.aggregation_type == 'average':
                    inputs = [1] * len(G)
                else:
                    inputs = [0] * (len(G) - 1) + [1]

                single_simulation[sim_name].simulate_single(G, inputs, sim_builder)
        for sim_name in sim_builders:
            single_simulation[sim_name].get_results(n, iter_size, sim_name, global_results, n)

    return global_results


#(l, 3, 3, builders, 10)
#
def execution(n_list, thread_function, n_threads, sim_builders, thread_args):
    slice_size = math.ceil(len(n_list) / n_threads)
    results = []
    pool = ThreadPool(n_threads)

    for i in range(0, len(n_list), slice_size):
        l = n_list[i : i  + slice_size]
        print(l)
        results.append( pool.apply_async(thread_function, args=  ((l,) + thread_args)))

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
            final_results[sim]['nodes_estimates'] += r_dict[sim]['nodes_estimates'] 
            final_results[sim]['nodes_consecutive_rounds'] += r_dict[sim]['nodes_consecutive_rounds'] 

    #plt.plot(final_results['normal']['nodes'], final_results['normal']['med_messages'])
    #plt.show()

    return final_results

def node_step_execution(n_min, n_max, step, n_threads, sim_builders, thread_args):
    n_list = list(range(n_min, n_max, step))
    return execution(n_list, thread_execution_nodes_step, n_threads, sim_builders, thread_args)

def rmse_step_execution(rmse_list, n_threads, sim_builders, thread_args):
    return execution(rmse_list, thread_execution_rmse_step, n_threads, sim_builders, thread_args)

if __name__ == '__main__': 
    
    #(degree, iter_size ..., sync_value (None if async))
    #thread_args = (3, 1, builders, 10)
    
    #(n_min, n_max, step, n_threads, ..., ...)
    #final_results = executions.node_step_execution(5, 10, 5, 2, builders, thread_args)
    
    #([rmse], ....) 
    #G = graphGen.randomG(9,3,10)
    #rmses = [10, 1, 0.1, 0.01]
    #thread_args = (G, 1, builders)
    #print("start execution")
    #final_results = rmse_step_execution(rmses, 2, builders, thread_args)
    
   if __name__ == '__main__': 
    
    b1 = builder_simple()
    b2 = builder_simple()
    b3 = builder_simple()
    
    builders = {'simples1' : b1, 'simples2': b2}
    
    #(degree, iter_size ..., sync_value (None if async))
    #thread_args = (3, 1, builders, 10)
    
    #(n_min, n_max, step, n_threads, ..., ...)
    #final_results = executions.node_step_execution(5, 10, 5, 2, builders, thread_args)
    
    #([rmse], ....) 
    G = graphGen.randomG(9,3,10)
    rmses = [10, 1, 0.1, 0.01]
    thread_args = (G, builders)
    print("start execution")
    final_results = rmse_step_execution(rmses, 2, builders, thread_args)
    
    print(final_results)
    
