from executions import *
import graphGen
import builders

import matplotlib.pyplot as plt


class Interval:
    def __init__(self, med, min, max, med_label):
        self.med = med
        self.min = min
        self.max = max
        self.med_label = med_label
    

def graph_multi(x, title, x_label, y_label, *args):

    fig, ax = plt.subplots()

    for arg in args:  
        ax.plot(x, arg.med, '-', label=arg.med_label)
        ax.fill_between(x, arg.min, arg.max, alpha=0.2)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.legend()
    plt.show()


def graph_vs(x, med1, min1, max1, med_label1, med2, min2, max2, med_label2, title, x_label, y_label):

    fig, ax = plt.subplots()

    ax.plot(x, med1, label=med_label1)
    ax.fill_between(x, min1, max1, alpha=0.2)

    ax.plot(x, med2, label=med_label2)
    ax.fill_between(x, min2, max2, alpha=0.2)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.legend()
    plt.show()


# rondas e mensagens por nodos, operaçao average e count
# dois sims average e count
def average_vs_count(r):
    nodes = r["average"]["step_axis"]

    one = r["average"]
    two = r["count"]

    graph_vs(
        nodes,
        one["med_messages"], one["min_messages"], one["max_messages"], 'AVERAGE', 
        two["med_messages"], two["min_messages"], two["max_messages"], 'COUNT', 
        "Messages comparison AVERAGE vs COUNT", 
        "Nodes", "Messages")

    graph_vs(
        nodes, 
        one["med_rounds"], one["min_rounds"], one["max_rounds"], 'AVERAGE', 
        two["med_rounds"], two["min_rounds"], two["max_rounds"], 'COUNT', 
        "Rounds comparison AVERAGE vs COUNT", 
        "Nodes", "Rounds")





def multicasts(r):
    graph_multi(
        r["normal"]["step_axis"], "Broadcast vs Unicast comparison", "Nodes", "Rounds",
        Interval(r["normal"]["med_rounds"],r["normal"]["min_rounds"],r["normal"]["max_rounds"],"Broadcast"),
        Interval(r["uni"]["med_rounds"],r["uni"]["min_rounds"],r["uni"]["max_rounds"],"Unicast"),
        Interval(r["euni"]["med_rounds"],r["euni"]["min_rounds"],r["euni"]["max_rounds"],"Evaluated Unicast")
        )


# rondas por rmse, para varias loss rates, graficos para broadcast uni e euni
def rounds_rmse_loss(r, rmse):

    # normal/broadcast
    graph_multi(
        rmse, "Broadcast with different loss rates", "RMSE", "Rounds",
        Interval(r["0"]["med_rounds"],r["0"]["min_rounds"],r["0"]["max_rounds"],"No loss"),
        Interval(r["02"]["med_rounds"],r["02"]["min_rounds"],r["02"]["max_rounds"],"20% message loss"),
        Interval(r["04"]["med_rounds"],r["04"]["min_rounds"],r["04"]["max_rounds"],"40% message loss"),
        Interval(r["06"]["med_rounds"],r["06"]["min_rounds"],r["06"]["max_rounds"],"60% message loss")
        )



# rondas por rmse com entradas e saídas de nodos (nº variado)
def rounds_rmse_dynamic(r, rmse):

    fig, ax = plt.subplots()

    ax.plot(rmse, r["med_rounds"], '-')
    ax.fill_between(rmse, r["min_rounds"], r["max_rounds"], alpha=0.2)

    ax.set_title("Dynamic network")
    ax.set_xlabel("RMSE")
    ax.set_ylabel("Rounds")

    plt.show()


# rondas por rmse com input variável
# TODO arranjar um melhor?
def rounds_rmse_varying_inputs(r, rmse):

    fig, ax = plt.subplots()

    ax.plot(rmse, r["med_rounds"], '-')
    ax.fill_between(rmse, r["min_rounds"], r["max_rounds"], alpha=0.2)

    ax.set_title("Regular input change")
    ax.set_xlabel("RMSE")
    ax.set_ylabel("Rounds")

    plt.show()



# media de rondas que estimativa fica no intervalo mindif, por nr de nodos
# TODO por legendas direito
def min_dif_average(r):
    
    fig, ax = plt.subplots()

    ax.plot(r["step_axis"], r['nodes_consecutive_rounds'])

    ax.set_title("Finding optimal consecutive rounds for self-termination")
    ax.set_xlabel("Nodes")
    ax.set_ylabel("Rounds")

    plt.show()



# rondas e mensagens por nodos, com sync e async, com certo timeout
# dois sims sync e async, com COUNT
def sync_vs_async(r, r2):

    nodes = r["step_axis"]

    one = r
    two = r2

    graph_vs(
        nodes,
        one["med_messages"], one["min_messages"], one["max_messages"], 'Sync',
        two["med_messages"], two["min_messages"], two["max_messages"], 'Async',
        "Messages comparison sync vs async", 
        "Nodes", "Messages")

    graph_vs(
        nodes, 
        one["med_rounds"], one["min_rounds"], one["max_rounds"], 'Sync',
        two["med_rounds"], two["min_rounds"], two["max_rounds"], 'Async',
        "Rounds comparison sync vs async", 
        "Nodes", "Rounds")


def async_vs_asynct(r, r2):

    nodes = r["step_axis"]

    one = r
    two = r2

    graph_vs(
        nodes,
        one["med_messages"], one["min_messages"], one["max_messages"], 'Without timeout',
        two["med_messages"], two["min_messages"], two["max_messages"], 'With timeout',
        "Messages comparison async vs async with timeout", 
        "Nodes", "Messages")

    graph_vs(
        nodes, 
        one["med_rounds"], one["min_rounds"], one["max_rounds"], 'Without timeout',
        two["med_rounds"], two["min_rounds"], two["max_rounds"], 'With timeout',
        "Rounds comparison async vs async with timeout", 
        "Nodes", "Rounds")


# execs---------------------------------------------------------------------------------------------------

def average_vs_count_exec():

    average = builders.SimulatorBuilder().with_agregation_type('average')
    count = builders.SimulatorBuilder().with_agregation_type('count')
    
    bs = {'average' : average, 'count' : count}
    
    thread_args = (3, 10, bs, 10) # (max degree, iters, ...)

    print("start execution")
    
    final_results = node_step_execution(5, 50, 5, 2, bs, thread_args) #(n_min, n_max, step, n_threads, ...)

    print(final_results)
    average_vs_count(final_results)



# TODO meter melhot
def rounds_rmse_loss_exec():


    b1 = builders.SimulatorBuilder().with_agregation_type('average').with_loss_rate(0)
    b2 = builders.SimulatorBuilder().with_agregation_type('average').with_loss_rate(0.2)
    b3 = builders.SimulatorBuilder().with_agregation_type('average').with_loss_rate(0.4)
    b4 = builders.SimulatorBuilder().with_agregation_type('average').with_loss_rate(0.6)
    
    bs = {'0' : b1, '02' : b2, '04' : b3, '06' : b4}
    
    Graphs = []
    for i in range(10):
        Graphs.append(graphGen.randomG(250,5,10))

    rmses = [0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.15, 0.20, 0.25, 0.5]
    thread_args = (Graphs, bs)
    print("start execution")
    final_results = rmse_step_execution(rmses, 2, bs, thread_args)
    #print(final_results)
    rounds_rmse_loss(final_results, rmses)


# TODO
def casts_comparison_exec():

    iters = 3
    max_degree = 3

    b1 = builders.SimulatorBuilder().with_agregation_type('average')
    b2 = builders.SimulatorBuilder().with_agregation_type('average').with_multicast_protocol(1)
    b3 = builders.SimulatorBuilder().with_agregation_type('average').with_evaluated_multicast_protocol(1)

    bs = {'normal' : b1, 'uni' : b2, 'euni' : b3}

    thread_args = (max_degree, iters, bs, 10)

    print("start execution")
    final_results = node_step_execution(5, 25, 5, 2, bs, thread_args)
    all_estimates = final_results['uni']['nodes_estimates'][0]
    final_e = all_estimates[len(all_estimates) -1]
    print("isto -> ", final_e)

    multicasts(final_results)









def min_dif_average_exec():

    b = builders.SimulatorBuilder().with_agregation_type('average').with_min_dif_testing(0.01)
    b.with_confidence_value(0.0009)
    bs = {'builder' : b}

    thread_args = (3, 20, bs, 1)

    print("start execution")
    #(n_min, n_max, step, n_threads, ..., ...)
    final_results = node_step_execution(50, 1000, 50, 2, bs, thread_args)
    #print(final_results)
    min_dif_average(final_results['builder'])



def sync_vs_async_exec():


    b1 = builders.SimulatorBuilder().with_agregation_type('average')
    
    bs = {'sync' : b1}
    
    thread_args = (3, 1, bs)

    print("start execution")
    #(n_min, n_max, step, n_threads, ..., ...)
    final_results_sync = node_step_execution(5, 25, 5, 2, bs, thread_args)

    b2 = builders.SimulatorBuilder().with_agregation_type('average').with_timeout_protocol(10)
    
    bs = {'async' : b2}
    
    thread_args = (3, 1, bs, 5)

    print("start execution")
    #(n_min, n_max, step, n_threads, ..., ...)
    final_results_async = node_step_execution(5, 25, 15, 2, bs, thread_args)


    #print(final_results)
    sync_vs_async(final_results_sync['sync'], final_results_async['async'])


def async_vs_async_no_timeout_exec():

    b1 = builders.SimulatorBuilder().with_agregation_type('average')
    bs = {'async' : b1}
    thread_args = (3, 3, bs)
    final_results1 = node_step_execution(5, 25, 5, 2, bs, thread_args)

    b2 = builders.SimulatorBuilder().with_agregation_type('average').with_timeout_protocol(10)
    bs = {'asynct' : b2}
    thread_args = (3, 3, bs)
    final_results2 = node_step_execution(5, 25, 5, 2, bs, thread_args)

    async_vs_asynct(final_results1['async'], final_results2['asynct'])



def converge():

    iters = 1
    max_degree = 3

    inputs = {}
    for i in range(10):
        inputs[i] = 1.5


    b = builders.SimulatorBuilder().with_agregation_type('count').with_departure_arrival_members_event(10, 2000, False)
    
    builder = {'builder' : b}
    
    thread_args = (max_degree, iters, builder)

    print("start execution")
    final_results = node_step_execution(10, 15, 5, 2, builder, thread_args)
    estimates = final_results['builder']['nodes_estimates'][0]
    estimates = list(map(list, zip(*estimates)))

    fig, ax = plt.subplots()
    for e in estimates:
        ax.scatter(range(len(e)), e, color="red", s=1)

    ax.set_title("Estimates over time")
    ax.set_xlabel("Rounds")
    ax.set_ylabel("Estimates")

    plt.show()


def custom_add_rem():

    iters = 1
    max_degree = 3

    b = builders.SimulatorBuilder().with_agregation_type('count')
    # TODO preencher
    b.with_scheduled_remove_members_event(5, 4000, False)
    b.with_scheduled_add_members_event(5, 1, 0, 2500, False, 10)
    b.with_scheduled_add_members_event(5, 1, 0, 5000, False, 10)
    b.with_scheduled_remove_members_event(10, 5500, False)


    builder = {'builder' : b}
    
    thread_args = (max_degree, iters, builder)

    print("start execution")
    final_results = node_step_execution(10, 15, 5, 2, builder, thread_args)

    estimates = final_results['builder']['nodes_estimates'][0]
    estimates = list(map(list, zip(*estimates)))

    fig, ax = plt.subplots()
    for e in estimates:
        ax.scatter(range(len(e)), e, color="red", s=1)

    ax.set_title("Estimates over time")
    ax.set_xlabel("Rounds")
    ax.set_ylabel("Estimates")

    plt.show()







def rounds_rmse_node_entry_exec():

    b = builders.SimulatorBuilder().with_agregation_type('count')
    # TODO preencher
    b.with_scheduled_add_members_event(5, 3, 0, 30, False,  w=10)
    bs = {'builder' : b}

    G = graphGen.randomG(100,3,10)
    rmses = [0.1, 0.01, 0.001]
    thread_args = ([G], bs)

    print("start execution")
    final_results = rmse_step_execution(rmses, 3, bs, thread_args)

    print(final_results['builder']['nodes_estimates'])

    rounds_rmse_dynamic(final_results['builder'], rmses)


def rounds_rmse_node_removal_exec():

    b = builders.SimulatorBuilder().with_agregation_type('count')
    # TODO preencher
    b.with_scheduled_remove_members_event(10, 20, False)
    bs = {'builder' : b}

    G = graphGen.randomG(100,3,10)
    rmses = [0.1, 0.01, 0.001]
    thread_args = ([G], bs)

    print("start execution")
    final_results = rmse_step_execution(rmses, 3, bs, thread_args)

    print(final_results['builder']['nodes_estimates'])

    rounds_rmse_dynamic(final_results['builder'], rmses)



def rounds_rmse_dynamic_exec():

    b = builders.SimulatorBuilder().with_agregation_type('average')
    # TODO preencher
    b.with_departure_arrival_members_event(10, 30, True)
    bs = {'builder' : b}

    G = graphGen.randomG(100,3,10)
    rmses = [0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.15, 0.20, 0.25, 0.5]
    thread_args = ([G], bs)

    print("start execution")
    final_results = rmse_step_execution(rmses, 2, bs, thread_args)

    rounds_rmse_dynamic(final_results['builder'], rmses)



#TODO
def rounds_rmse_varying_inputs_exec():

    n = 10
    inputs = {}
    for i in range(n):
        inputs[i] = 1.5

    b = builders.SimulatorBuilder().with_agregation_type('average').with_scheduled_change_inputs_event(inputs, 10)
    bs = {'builder' : b}

    G = graphGen.randomG(n,3,10)
    rmses = [0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.15, 0.20, 0.25, 0.5]
    thread_args = ([G], bs)

    print("start execution")
    final_results = rmse_step_execution(rmses, 2, bs, thread_args)

    rounds_rmse_varying_inputs(final_results['builder'], rmses)


if __name__ == '__main__': 
    #average_vs_count_exec()
    #rounds_rmse_loss_exec()
    #casts_comparison_exec()
    #async_vs_async_no_timeout_exec()
    async_vs_async_no_timeout_exec()
    #converge()
    












