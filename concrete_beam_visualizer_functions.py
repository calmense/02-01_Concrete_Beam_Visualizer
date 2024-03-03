# Schraubenbemessungsprogramm: Webapp mit Streamlit - Axial- und Schertragfähigkeit von Würth Vollgewindeschrauben
# Bibliotheken
from math import pi, sqrt, cos, sin, atan
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from itertools import product
from collections import defaultdict

def add_text(fig, text, xPosition, yPosition, textSize):
    fig.add_annotation(dict(font=dict(size=textSize, color = "black"),
                                            x = xPosition,
                                            y = yPosition,
                                            showarrow=False,
                                            text=text,
                                            textangle=0,
                                            xanchor='left',
                                            xref="x",
                                            yref="y"))


def draw_arrow(fig, xList, yList, direction, scaleX, scaleY):
    fig.add_trace(go.Scatter(x = xList, y = yList,
                marker= dict(size=10,symbol= "arrow", angleref="previous", color='black')))
       
    fig.add_trace(go.Scatter(x = list(reversed(xList)), y = list(reversed(yList)),
                marker= dict(size=10,symbol= "arrow", angleref="previous", color='black')))
    
    if direction == "X":
        xLine1 = [xList[0], xList[0]]
        yLine1 = [yList[0] - 5*scaleY, yList[0] + 5*scaleY]

        xLine2 = [xList[-1], xList[-1]]
        yLine2 = [yList[-1] - 5*scaleY, yList[-1] + 5*scaleY]

    elif direction == "Y":
        xLine1 = [xList[0] - 5*scaleY, xList[0] + 5*scaleY]
        yLine1 = [yList[0], yList[0]]

        xLine2 = [xList[-1] - 5*scaleY, xList[-1] + 5*scaleY]
        yLine2 = [yList[-1], yList[-1]]

    fig.add_trace(go.Scatter(x=xLine1, y = yLine1, mode="lines", marker=dict(color='black')))
    fig.add_trace(go.Scatter(x=xLine2, y = yLine2, mode="lines", marker=dict(color='black', angle = 45)))

def draw_line(fig, xList, yList, size, color, opacity):
    fig.add_trace(go.Scatter(x = list(reversed(xList)), y = list(reversed(yList)), 
                             mode="lines", line=dict(color=color, width=size / 5), opacity=opacity))

def add_rebar(fig, xCoordinates, yCoordinates, diameter, gapx, gapy):
    for i in range(len(xCoordinates)):
        x = xCoordinates[i] + gapx - diameter / 2
        y = yCoordinates[i] + gapy - diameter / 2
        x1 = x + diameter
        y1 = y + diameter
        fig.add_shape(dict(type="circle", x0 = x, y0 = y, x1 = x1, y1 = y1), line_color='black', fillcolor = "black")

def plotly_go_scatter_stirrup(xList, yList, lineColor, width):

    go_scatter = go.Scatter(
        x = xList, 
        y = yList, 
        line = dict(color = lineColor, shape = "spline", smoothing = 0, width = width),
        mode = "lines")
    
    return go_scatter