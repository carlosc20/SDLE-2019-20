from executions import execution

import matplotlib.pyplot as plt


class Interval:
    def __init__(self, med, min, max, med_label, int_label):
        self.med = med
        self.min = min
        self.max = max
        self.med_label = med_label
        self.int_label = int_label
    

def graph_multi(x, title, x_label, y_label, *args):

    fig, ax = plt.subplots()

    for arg in args:  
        ax.plot(x, arg.med, '-', label=arg.med_label)
        ax.fill_between(x, arg.min, arg.max, alpha=0.2, label=arg.int_label)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.legend()
    plt.show()


def graph_vs(x, med1, min1, max1, med_label1, int_label1, med2, min2, max2, med_label2, int_label2, title, x_label, y_label):

    fig, ax = plt.subplots()

    ax.plot(x, med1, '-', label=med_label1)
    ax.fill_between(x, min1, max1, alpha=0.2, label=int_label1)

    ax.plot(x, med2, label=med_label2)
    ax.fill_between(x, min2, max2, alpha=0.2, label=int_label2)

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
        one["med_messages"], one["min_messages"], one["max_messages"], 'Average (AVERAGE)', 'Interval (AVERAGE)', 
        two["med_messages"], two["min_messages"], two["max_messages"], 'Average (COUNT)', 'Interval (COUNT)', 
        "Messages comparison AVERAGE vs COUNT", 
        "Nodes", "Messages")

    graph_vs(
        nodes, 
        one["med_rounds"], one["min_rounds"], one["max_rounds"], 'Average (AVERAGE)', 'Interval (AVERAGE)', 
        two["med_rounds"], two["min_rounds"], two["max_rounds"], 'Average (COUNT)', 'Interval (COUNT)', 
        "Rounds comparison AVERAGE vs COUNT", 
        "Nodes", "Rounds")


# rondas e mensagens por nodos, rmse vs flowsum termination
# dois sims rmse e flowsum, com COUNT
def rmse_vs_flowsum(r):
    nodes = r["rmse"]["step_axis"]

    one = r["rmse"]
    two = r["floswum"]

    graph_vs(
        nodes,
        one["med_messages"], one["min_messages"], one["max_messages"], 'Average (RMSE)', 'Interval (RMSE)', 
        two["med_messages"], two["min_messages"], two["max_messages"], 'Average (FLOWSUM)', 'Interval (FLOWSUM)', 
        "Messages comparison RMSE vs FLOWSUM termination", 
        "Nodes", "Messages")

    graph_vs(
        nodes, 
        one["med_rounds"], one["min_rounds"], one["max_rounds"], 'Average (RMSE)', 'Interval (RMSE)', 
        two["med_rounds"], two["min_rounds"], two["max_rounds"], 'Average (FLOWSUM)', 'Interval (FLOWSUM)', 
        "Rounds comparison RMSE vs FLOWSUM termination", 
        "Nodes", "Rounds")


# rondas por rmse, para varias loss rates, graficos para broadcast uni e euni
# TODO, mudar nomes para uni e euni, se calhar tirar 0.6 loss rate?
def rounds_rmse_loss(r, rmse):

    # normal/broadcast
    graph_multi(
        rmse, "Broadcast", "RMSE", "Rounds",
        Interval(r["0"]["med_rounds"],r["0"]["min_rounds"],r["0"]["max_rounds"],"No loss","No loss"),
        Interval(r["02"]["med_rounds"],r["02"]["min_rounds"],r["02"]["max_rounds"],"20% message loss","20% message loss"),
        Interval(r["04"]["med_rounds"],r["04"]["min_rounds"],r["04"]["max_rounds"],"40% message loss","40% message loss"),
        Interval(r["06"]["med_rounds"],r["06"]["min_rounds"],r["06"]["max_rounds"],"60% message loss","60% message loss")
        )

    # uni
    graph_multi(
        rmse, "Unicast", "RMSE", "Rounds",
        Interval(r["0"]["med_rounds"],r["0"]["min_rounds"],r["0"]["max_rounds"],"No loss","No loss"),
        Interval(r["02"]["med_rounds"],r["02"]["min_rounds"],r["02"]["max_rounds"],"20% message loss","20% message loss"),
        Interval(r["04"]["med_rounds"],r["04"]["min_rounds"],r["04"]["max_rounds"],"40% message loss","40% message loss"),
        Interval(r["06"]["med_rounds"],r["06"]["min_rounds"],r["06"]["max_rounds"],"60% message loss","60% message loss")
        )

    # evaluated uni
    graph_multi(
        rmse, "Evaluated Unicast", "RMSE", "Rounds",
        Interval(r["0"]["med_rounds"],r["0"]["min_rounds"],r["0"]["max_rounds"],"No loss","No loss"),
        Interval(r["02"]["med_rounds"],r["02"]["min_rounds"],r["02"]["max_rounds"],"20% message loss","20% message loss"),
        Interval(r["04"]["med_rounds"],r["04"]["min_rounds"],r["04"]["max_rounds"],"40% message loss","40% message loss"),
        Interval(r["06"]["med_rounds"],r["06"]["min_rounds"],r["06"]["max_rounds"],"60% message loss","60% message loss")
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
# TODO por nos resultados isto, substituir os ??, por legendas direito
def min_dif_average(r):
    
    fig, ax = plt.subplots()

    ax.plot(r["step_axis"], r["??"], '-')
    ax.fill_between(r["step_axis"], r["min_??"], r["max_??"], alpha=0.2)

    ax.set_title("Mindif por nodos com RMSE global")
    ax.set_xlabel("Nodos")
    ax.set_ylabel("Média rondas em que estimativa permanece dentro do intervalo mindif")

    plt.show()



# rondas e mensagens por nodos, com sync e async, com certo timeout
# dois sims sync e async, com COUNT
def sync_vs_async(r):

    nodes = r["sync"]["nodes"]

    one = r["sync"]
    two = r["async"]

    graph_vs(
        nodes,
        one["med_messages"], one["min_messages"], one["max_messages"], 'Average (sync)', 'Interval (sync)', 
        two["med_messages"], two["min_messages"], two["max_messages"], 'Average (async)', 'Interval (async)', 
        "Messages comparison sync vs async", 
        "Nodes", "Messages")

    graph_vs(
        nodes, 
        one["med_rounds"], one["min_rounds"], one["max_rounds"], 'Average (sync)', 'Interval (sync)', 
        two["med_rounds"], two["min_rounds"], two["max_rounds"], 'Average (async)', 'Interval (async)', 
        "Rounds comparison sync vs COUNT", 
        "Nodes", "Rounds")



if __name__ == '__main__': 
    results = execution(10,50,10,2)
    print(results)










