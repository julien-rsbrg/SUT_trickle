import random


def existChemin(c, graph, IOSM_is_graph_type=True):
    """
    Are the test objective c and graph consistent together

    Variables :
        - c (list): test objective, a list like [(s0,trans name from s0), (s1, trans name from s1)]
        - graph (tuple): an IOSM or FDB grap
        - IOSM_is_graph_type (bool) : indicate the type of the graph, if false, graph is an FDB graph
    Returns :
        boolean indicating if the objective c and the graph graph are consistent together
    """
    if IOSM_is_graph_type:
        S, _, T, _ = graph
    else:
        # graph type is FDB (V,Vb,Vr,L,E,s0)
        S, _, _, _, T, _ = graph
    for i, (node, trans) in enumerate(c):
        if not(node in S):
            return False
        else:
            found_trans = False
            for neigh, neigh_trans in T[node]:
                if neigh_trans == trans:
                    if found_trans:
                        return False
                    if i <= len(c)-2 and neigh != c[i+1][0]:
                        return False
                    found_trans = True
    return True


def randomObjectifTest(IOSM_graph, N):
    """
    Prend en entrée un graphe IOSM et un entier N qui représente la taille du chemin voulu
    Return un objectif de test aléatoire de taille N
    """
    S, _, E, _ = IOSM_graph
    objTest = []
    c_node = random.choice(list(S))
    for _ in range(N):
        next_node, c_trans = random.choice(E[c_node])
        objTest.append((c_node, c_trans))
        c_node = next_node
    return objTest


if __name__ == '__main__':

    S2 = {f"g{i}" for i in range(4)}
    L2 = set(["Coin", "Bad", "Good", "Soda", "Cancel", "Unav", "Can"])
    T2 = {"g0": [("g1", "?Coin")], "g1": [("g0", "!Bad"), ("g2", "!Good")], "g2": [
        ("g3", "?Soda"), ("g0", "?Cancel")], "g3": [("g2", "!Unav"), ("g0", "!Can")]}
    s02 = "g0"
    graph_test = (S2, L2, T2, s02)

    print(randomObjectifTest(graph_test, 4))

    # print(existChemin(
    #     [("g0", "?Coin"), ("g1", "!Good"), ("g2", "?Cancel")], graph_test))
