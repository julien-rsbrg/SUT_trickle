import math

import transform


def dico_reverse(dico):
    '''
    Exchanges directions in a directed graph

    Variable :
        dico : a dictionary with key a node, value the list of tuples (nodes the key is directly linked to,
               the transfer string)
    returns :
        dico_rev : dico with reverse directions   
    '''
    dico_rev = {}
    for key in dico:
        for neigh, n_trans in dico[key]:
            if not(neigh in dico_rev):
                dico_rev[neigh] = [(key, n_trans)]
            else:
                dico_rev[neigh].append((key, n_trans))
    return dico_rev


def dico_W(t, FDB_graph):
    '''
    BFS

    Variables:
        - t = vertex we want to end (str)
        - FDB_graph = (V,Vb,Vr,L,E,s0) a bipartite graph with "puit" and "ErrInf" in E.keys()

    Returns :
        dict_W = dictionnary with key a node and value a tuple (i,j) where i,j are those of Wij
    '''
    (_, Vb, _, _, E, _) = FDB_graph
    dict_W = {t: (0, 0)}
    lnext = [t]
    E = dico_reverse(E)
    while len(lnext):
        c_node = lnext.pop(0)
        (i, j) = dict_W[c_node]

        if c_node in E.keys():
            # to deal with source vertices
            for neigh, _ in E[c_node]:
                if neigh in Vb:
                    if not(neigh in dict_W) or dict_W[neigh][0] > i+1:
                        dict_W[neigh] = i+1, j
                        lnext.append(neigh)
                else:
                    if not(neigh in dict_W) or dict_W[neigh][0] > 0:
                        dict_W[neigh] = 0, j+1
                        lnext.append(neigh)
    return dict_W


def choose_transition(s, graph, dict_W):
    '''
    Return the best path from s to t

    Variables :
        - s = beginning vertex, s in Vb (str)
        - graph = (V,Vb,Vr,L, E,s0) a bipartite graph
        - dict_W = dictionary returned by dico_W(,,)

    Return :
        best_neigh, best_trans : blue player has to choose
    '''
    (_, _, _, _, E, _) = graph

    best_j, best_neigh, best_trans = math.inf, None, None
    for neigh, trans in E[s]:
        if dict_W[neigh][1] <= best_j:
            best_j, best_neigh, best_trans = dict_W[neigh][1], neigh, trans
    return best_neigh, best_trans


if __name__ == '__main__':

    def test():
        S = {f"g{i}" for i in range(4)}
        L = set(["COIN", "BAD", "GOOD", "SODA", "CANCEL", "UNAV", "CAN"])
        T = {"g0": [("g1", "?COIN")], "g1": [("g0", "!BAD"), ("g2", "!GOOD")], "g2": [
            ("g3", "?SODA"), ("g0", "?CANCEL")], "g3": [("g2", "!UNAV"), ("g0", "!CAN")]}
        s0 = "g0"
        graph_test = (S, L, T, s0)
        FDB_graph = transform.graph_to_game(graph_test)
        print(FDB_graph[-2])
        # print(dico_reverse(E))
        print("dico :", dico_W("g3", FDB_graph))

    test()

    def test_2():
        S = {f"g{i}" for i in range(4)}
        L = set(["COIN", "BAD", "GOOD", "SODA", "CANCEL", "UNAV", "CAN"])
        T = {"g0": [("g1", "?COIN")], "g1": [("g0", "!BAD"), ("g2", "!GOOD")], "g2": [
            ("g3", "?SODA"), ("g0", "?CANCEL")], "g3": [("g2", "!UNAV"), ("g0", "!CAN")]}
        s0 = "g0"
        graph_test = (S, L, T, s0)
        FDB_graph = transform.graph_to_game(graph_test)
        print(len(FDB_graph))
        # print(dico_reverse(E))
        dict_W = dico_W("g0", FDB_graph)
        print("next neigh + trans :", choose_transition("g2", FDB_graph, dict_W))

    test_2()
