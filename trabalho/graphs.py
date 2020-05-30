from executions import execution

import matplotlib.pyplot as plt



    
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



def average_vs_count(results):
    nodes = results['nodes']

    med_msg = results['med_messages']
    max_msg = results['max_messages']
    min_msg = results['min_messages']

    med_rnd = results['med_rounds']
    max_rnd = results['max_rounds']
    min_rnd = results['min_rounds']

    graph_vs(
        nodes, 
        med_msg, min_msg, max_msg, 'Média AVERAGE', 'Itervalo possível AVERAGE', 
        med_rnd, min_rnd, max_rnd, 'Média COUNT', 'Intervalo possível COUNT', 
        "Comparação mensagens AVERAGE e COUNT", 
        "Nodos", "Mensagens")

    graph_vs(
        nodes, 
        med_msg, min_msg, max_msg, 'Média AVERAGE', 'Itervalo possível AVERAGE', 
        med_rnd, min_rnd, max_rnd, 'Média COUNT', 'Intervalo possível COUNT', 
        "Comparação rondas AVERAGE e COUNT", 
        "Nodos", "Rondas")


def rmse_vs_flowsum(results):
    # vs push sum?
    nodes = results['nodes']

    med_msg = results['med_messages']
    max_msg = results['max_messages']
    min_msg = results['min_messages']

    med_rnd = results['med_rounds']
    max_rnd = results['max_rounds']
    min_rnd = results['min_rounds']

    graph_vs(
        nodes, 
        med_msg, min_msg, max_msg, 'Média RMSE', 'Itervalo possível RMSE', 
        med_rnd, min_rnd, max_rnd, 'Média FLOWSUM', 'Intervalo possível FLOWSUM', 
        "Comparação mensagens RMSE e FLOWSUM", 
        "Nodos", "Mensagens")

    graph_vs(
        nodes, 
        med_msg, min_msg, max_msg, 'Média RMSE', 'Itervalo possível RMSE', 
        med_rnd, min_rnd, max_rnd, 'Média FLOWSUM', 'Intervalo possível FLOWSUM', 
        "Comparação rondas RMSE e FLOWSUM", 
        "Nodos", "Rondas")


def casts_by_rmse(results):
    rmse

    # broadcast vs unicast vs eunicast

    graph_vs(
        rmse, 
        med_msg, min_msg, max_msg, 'Média RMSE', 'Itervalo possível RMSE', 
        med_rnd, min_rnd, max_rnd, 'Média FLOWSUM', 'Intervalo possível FLOWSUM', 
        "Comparação mensagens RMSE e FLOWSUM", 
        "Nodos", "Mensagens")

    graph_vs(
        rmse, 
        med_msg, min_msg, max_msg, 'Média RMSE', 'Itervalo possível RMSE', 
        med_rnd, min_rnd, max_rnd, 'Média FLOWSUM', 'Intervalo possível FLOWSUM', 
        "Comparação rondas RMSE e FLOWSUM", 
        "Nodos", "Rondas")



def rounds_rmse_loss(results):
    # media rondas por rmse 
    # broad uni e euni, um graph para cada com as losses todas
    # 0, 0.2, 0.4 0.6 loss rate 
    pass


def rounds_rmse_dynamic(results):
    # - med -> nº de rondas / RMSE (entradas e saídas de nodos (nº variado))
    pass


def rounds_rmse_varying_inputs(results):
    # - med -> nº de rondas / RMSE (mudança de input)
    pass



def min_dif_average(results):
    
    fig, ax = plt.subplots()

    ax.plot(x, med1, '-', label=med_label1)
    ax.fill_between(x, min1, max1, alpha=0.2, label=int_label1)

    ax.set_title("Mindif por nodos com RMSE global")
    ax.set_xlabel("Nodos")
    ax.set_ylabel("Média rondas em que estimativa permanece dentro do intervalo mindif")

    ax.legend()
    plt.show()




def sync_vs_async(self, parameter_list):

    nodes = results['nodes']

    med_msg = results['med_messages']
    max_msg = results['max_messages']
    min_msg = results['min_messages']

    med_rnd = results['med_rounds']
    max_rnd = results['max_rounds']
    min_rnd = results['min_rounds']

    graph_vs(
        nodes, 
        med_msg, min_msg, max_msg, 'Média sinc.', 'Itervalo possível sinc.', 
        med_rnd, min_rnd, max_rnd, 'Média assinc.', 'Intervalo possível assinc.', 
        "Comparação mensagens sinc. e assinc.", 
        "Nodos", "Mensagens")

    graph_vs(
        nodes, 
        med_msg, min_msg, max_msg, 'Média sinc.', 'Itervalo possível sinc.', 
        med_rnd, min_rnd, max_rnd, 'Média assinc.', 'Intervalo possível assinc.', 
        "Comparação rondas sinc. e assinc.", 
        "Nodos", "Rondas")



if __name__ == '__main__': 
    results = execution(10,50,10,2)
    print(results)











