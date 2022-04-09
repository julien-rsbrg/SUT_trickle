import tkinter as tk
from turtle import width
import random
import math

from matplotlib.pyplot import arrow, fill
from numpy import angle


def draw_FDB_graph(FDB_graph, l = 1000, h = 800):
    """draw_FDB_graph provides a graphical representation of the finite directed bipartite graph using the package Tkinter.

    Args:
        FDB_graph (tuple): a finite directed bipartite graph to be displayed
        l (int, optional): length of tkinter window. Defaults to 1000.
        h (int, optional): height of tkinter window. Defaults to 800.
    """

    w = tk.Tk()
    c = tk.Canvas(w, width=l, height=h)
 
    (S, Vb, Vr, L, E, s0) = FDB_graph
    N = len(S)

    x_b, x_r, y_b, y_r = l//(2*(N-1)), l//(2*(N-1)), 150, 650 

    c.create_text(500, 35, font=("Purisa", 20, 'underline'), text="Finite directed bipartite graph representation :")

    Vb_indexed, Vr_indexed = {}, {}
    for vertex in S:
        if vertex == "puit":
            if "puit" in Vb:
                Vb_indexed["puit"] = l -  l//(2*(N-1))
            else:
                Vr_indexed["puit"] = l -  l//(2*(N-1))
            draw_vertex(c, l -  l//(2*(N-1)), 200, vertex, "blue")
        elif vertex == "ErrInf":
            if "ErrInf" in Vb:
                Vb_indexed["ErrInf"] = l -  l//(2*(N-1))
            else:
                Vr_indexed["ErrInf"] = l -  l//(2*(N-1))
            draw_vertex(c, l -  l//(2*(N-1)), 600, vertex, 'red')
        elif vertex in Vb:
            Vb_indexed[vertex] = x_b
            draw_vertex(c, x_b, y_b, vertex, 'blue')
            x_b += l//(N//2)
        elif vertex in Vr:
            Vr_indexed[vertex] = x_r
            draw_vertex(c, x_r, y_r, vertex, 'red')
            x_r += l//(N//2)
    
    for edge in E:
        for neighbour in E[edge]:
            input_vertex, label, output_vertex = edge, neighbour[1], neighbour[0]
            if output_vertex not in ["puit", "ErrInf"] and input_vertex not in ["puit", "ErrInf"]:
                if input_vertex in Vb:
                    x_0, x_1 = Vb_indexed[input_vertex], Vr_indexed[output_vertex]
                    draw_edge(c, l, N, x_0, x_1, y_b, y_r, label, 'blue')
                elif input_vertex in Vr:
                    x_0, x_1 = Vr_indexed[input_vertex], Vb_indexed[output_vertex]
                    draw_edge(c, l, N, x_0, x_1, y_r, y_b, label, 'red')
            else:
                if output_vertex == "puit":
                    if input_vertex == "ErrInf":
                        x_0 = l -  l//(2*(N-1))
                        draw_edge(c, l, N, l -  l//(2*(N-1)), l -  l//(2*(N-1)), 600, 200, 'tau', 'green')
                    elif input_vertex in Vb:
                        x_0 = Vb_indexed[input_vertex]
                        draw_tau(c, l, N, x_0, y_b + 5)
                    elif input_vertex in Vr:
                        x_0 = Vr_indexed[input_vertex]
                        draw_tau(c, l, N, x_0, y_r - 5)
                else:
                    draw_edge(c, l, N, l -  l//(2*(N-1)), l -  l//(2*(N-1)), 200, 600, 'tau', 'blue')
                

        
    c.pack()
    w.mainloop()


def draw_vertex(c, x, y, name, color):
    c.create_rectangle(x-5, y-5, x+5, y+5, fill=color)
    if color == 'blue':
        c.create_text(x+12, y-12, text=name)
    else:
        c.create_text(x+12, y+12, text=name)

def draw_edge(c, l, N, x_0, x_1, y_0, y_1, label, color):
    if x_0 == x_1:
        if color == 'blue':
            c.create_line(x_0, y_0 + 5, (x_0 + x_1)//2 - l//(2*(N - 1)), 400 ,x_1, y_1 - 5, arrow=tk.LAST, fill= color, smooth=1, width=2)
            c.create_text((x_0 + x_1)//2 - l//(2*(N+2)), 400, text = label, fill= color, angle=90)
        else:
            c.create_line(x_0, y_0 - 5, (x_0 + x_1)//2 + l//(2*(N - 1)), 400 ,x_1, y_1 + 5, arrow=tk.LAST, fill= color, smooth=1, width=2)
            c.create_text((x_0 + x_1)//2 + l//(2*(N+2)), 400, text = label, fill= color, angle=90)
    else:
        if color == 'blue':
            c.create_line(x_0, y_0 + 5, (x_0 + x_1)//2 - l//(2*(N-2)), 400,x_1, y_1 - 5, arrow=tk.LAST, fill= color, smooth=1, width=3)
            if x_0 < x_1:
                x_test, y_test, orientation = (x_0 + x_1)//2 - 25 , 420, -45
            else:
                x_test, y_test, orientation = (x_0 + x_1)//2 - 25, 380, 45

            c.create_text(x_test , y_test, text = label, fill= color, angle = orientation)
        else:
            c.create_line(x_0, y_0 - 5, (x_0 + x_1)//2 + l//(2*(N-2)), 400,x_1, y_1 + 5, arrow=tk.LAST, fill= color, smooth=1, width=3)
            if x_0 < x_1:
                x_test, y_test, orientation = (x_0 + x_1)//2 + 25, 420, 45
            else:
                x_test, y_test, orientation = (x_0 + x_1)//2 + 25, 380, -45
            c.create_text(x_test, y_test, text = label, fill= color, angle = orientation)

def draw_tau(c, l, N, x_0, y_0):
    c.create_line(x_0, y_0,  l -  l//(2*(N-1)) - 5, 200, arrow=tk.LAST, fill="green", smooth=1, width = 2)
    c.create_text((x_0 + l -  l//(2*(N-1))) // 2 + 12, (y_0 + 200) // 2, text="tau", fill = "green")
        
    


if __name__ == "__main__":
    draw_FDB_graph(((0,1,2,3,4,5,6,7, 8, 9, "puit", "ErrInf"), (0, 2, 4,6, 8, "puit"), (1, 3, 5,7, 9, "ErrInf"), (), {0: [(1, "!Return"), (3, "?Coin")], 3:[(0, "!Bad")], 4:[('puit', '?Escape')], 5: [(2, '!Error'), (8, '?New')],6: [(1, '!Wrong'), (5, '?Coin'), (7, '!Can')], 7:[("puit", "?Escape")], "puit":[("ErrInf", 'tau')], "ErrInf":[("puit", 'tau')]}, 1))