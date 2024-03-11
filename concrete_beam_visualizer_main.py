# Schraubenbemessungsprogramm: Webapp mit Streamlit - Axial- und Schertragfähigkeit von Würth Vollgewindeschrauben

# Standard Libraries
from math import pi, sqrt, cos, sin, atan, isnan
from itertools import product
from collections import defaultdict

# External Libraries
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image

# Custom Functions
from concrete_beam_visualizer_functions import *

# HTML Einstellungen
st.set_page_config(page_title="Concrete Beam Visualizer", layout="wide")
st.markdown("""<style>
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {width: 500px;}
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {width: 500px;margin-left: -500px;}
footer:after{
    content:"Python for Structural Engineers | Cal Mense (M.Eng.) ";
    display:block;
    position:relative;
    color:grey;
}
</style>""",unsafe_allow_html=True)

st.markdown('''
<style>
.katex-html {
    text-align: left;
}
</style>''',
unsafe_allow_html=True
)


st.header("Concrete Beam Visualizer")
st.write("This application visualizes rectangular cross-sections of concrete beams.")

with st.sidebar:
    st.header("Parameter")
    
    concrete = st.selectbox("Concrete", ["C12/15", "C16/20", "C20/25", "C25/30", "C30/37", "C35/45", "C40/45", "C50/60"], 3)
    steel = st.selectbox("Steel", ["B500A", "B500B"])
    text = st.text_input("Text", "XC1")
    refinement = st.radio("Rebar Refinement?", ["No", "Yes"])

    if refinement == "Yes":
        rebarBot1 = st.selectbox("Rebar Bottom 1", [12, 14, 16, 20, 25, 28])
        rebarBot2 = st.selectbox("Rebar Bottom 2", [12, 14, 16, 20, 25, 28])
        rebarBot3 = st.selectbox("Rebar Bottom 3", [12, 14, 16, 20, 25, 28])
        rebarTop1 = st.selectbox("Rebar Top 1", [12, 14, 16, 20, 25, 28])
        rebarTop2 = st.selectbox("Rebar Top 2", [12, 14, 16, 20, 25, 28])
    else:
        st.write("The rebar diameters are initially determined according to the table. For finer adjustments, click 'Yes'.")

# _______________________main_______________________________________
# __________________________________________________________________
        
st.subheader("Table")
st.write("The table below is interactive and editable. You can easily paste data from applications like Excel. Utilize the **Select** buttons to display your desired column.")
# input editable table
        
df = pd.DataFrame(
    [
        {"Select": True, "Title": "Beam1", "Width": 200, "Height": 400, "Vert. cover": 50, "Horiz. cover": 50, "Rebar": 16, "Stirrups": 8, "Sleeks": 2, "Spacing": 15, "No Top 1": 2, "No Top 2": 0,  "No Bot 1": 3, "No Bot 2": 0, "No Bot 3": 0 },
        {"Select": False, "Title": "Beam2", "Width": 400, "Height": 800, "Vert. cover": 50, "Horiz. cover": 50, "Rebar": 20, "Stirrups": 8, "Sleeks": 2,"Spacing": 15, "No Top 1": 3, "No Top 2": 0,  "No Bot 1": 5, "No Bot 2": 5, "No Bot 3": 2 },
        {"Select": False, "Title": "Beam3", "Width": 1500, "Height": 1700, "Vert. cover": 50, "Horiz. cover": 50, "Rebar": 20, "Stirrups": 8, "Sleeks": 2,"Spacing": 15, "No Top 1": 2, "No Top 2": 0,  "No Bot 1": 3, "No Bot 2": 3, "No Bot 3": 2 },
   ])

edited_df = st.data_editor(df, hide_index=True, num_rows="dynamic") 

# get index of the selected table
ListIndex = [x for x in edited_df["Select"]]
ListIndexFiltered = [n for n,bool in enumerate(ListIndex) if bool == True]
index = 0 if not ListIndexFiltered else ListIndexFiltered[0]


title = [x for x in edited_df["Title"]][index]
width = [y for y in edited_df["Width"]][index]
height = [y for y in edited_df["Height"]][index]
rebar = [y for y in edited_df["Rebar"]][index]
stirrups = [y for y in edited_df["Stirrups"]][index]
sleeks = [y for y in edited_df["Sleeks"]][index]
dsw = [y for y in edited_df["Spacing"]][index]
edgeVertical = [y for y in edited_df["Vert. cover"]][index]
edgeHorizontal = [y for y in edited_df["Horiz. cover"]][index]
noTop1 = int([y for y in edited_df["No Top 1"]][index])
noTop2 = int([y for y in edited_df["No Top 2"]][index])
noBot1 = int([y for y in edited_df["No Bot 1"]][index])
noBot2 = int([y for y in edited_df["No Bot 2"]][index])
noBot3 = int([y for y in edited_df["No Bot 3"]][index])

noList = [noTop1, noTop2, noBot1, noBot2, noBot3]
zeroIndices = [index for index, value in enumerate(noList) if value == 0]
allIndices = [i for i in range(len(noList))]
nonZeroIndices = [item for item in allIndices if item not in zeroIndices]

if refinement == "No":
    rebarBot1 = rebarBot2 = rebarBot3 = rebarTop1 = rebarTop2 = rebar

rebarList = [rebarTop1, rebarTop2, rebarBot1, rebarBot2, rebarBot3]
rebarMax = max(rebarList)

# ____________________calculation___________________________________
# __________________________________________________________________
try:        
    # rebar top
    distanceTop1 = (width - edgeHorizontal * 2) / (noTop1-1)
    xCordinatesTop1 = [(edgeHorizontal + distanceTop1 * i) for i in range(int(noTop1))]
    yCordinatesTop1 = [(height - edgeVertical) for i in range(noTop1)]

    # rebar top 2
    xCordinatesTop21 = [xCordinatesTop1[i] for i in range(int(noTop2/2))]
    xCordinatesTop22 = [xCordinatesTop1[-i] for i in range(1,int(noTop2/2)+1)]
    xCordinatesTop2 = xCordinatesTop21 + xCordinatesTop22
    yCordinatesTop2 = [(height - edgeVertical - 3 * rebarMax) for i in range(noTop2)]
    
    # rebar bottom 1
    distanceBottom1 = (width - edgeHorizontal * 2) / (noBot1-1)
    xCordinatesBot1 = [(edgeHorizontal + distanceBottom1 * i) for i in range(noBot1)]
    yCordinatesBot1 = [(edgeVertical) for i in range(noBot1)]
    
    # rebar bottom 2
    middleCoord2 = [width / 2 if noBot2 % 2 != 0 else None] # Check if the length is odd
    outer_index21 = [i for i in range(int(noBot2/2))]
    outer_index22 = [-i for i in range(1, int(noBot2/2)+1)]
    index2 = outer_index21 + outer_index22
    xCordinatesBot2 = [xCordinatesBot1[i] for i in index2] + middleCoord2
    xCordinatesBot2 = [i for i in xCordinatesBot2 if i is not None]
    yCordinatesBot2 = [(edgeVertical + rebarMax * 3) for i in range(noBot2)]
    
    # rebar bottom 3
    middleCoord3 = [width / 2 if noBot3 % 2 != 0 else None] # Check if the length is odd
    outer_index31 = [i for i in range(int(noBot3/2))]
    outer_index32 = [-i for i in range(1, int(noBot3/2)+1)]
    index3 = outer_index31 + outer_index32
    xCordinatesBot3 = [xCordinatesBot1[i] for i in index3] + middleCoord3
    xCordinatesBot3 = [i for i in xCordinatesBot3 if i is not None]
    yCordinatesBot3 = [(edgeVertical + rebarMax * 6) for i in range(noBot3)]
    
    xCoordinates = [xCordinatesTop1, xCordinatesTop2, xCordinatesBot1, xCordinatesBot2, xCordinatesBot3]
    yCoordinates = [yCordinatesTop1, yCordinatesTop2, yCordinatesBot1, yCordinatesBot2, yCordinatesBot3]
    
    # filter out zero lists
    xCoordinates = [xCoordinates[i] for i in nonZeroIndices]
    yCoordinates = [yCoordinates[i] for i in nonZeroIndices]
    rebarList = [rebarList[i] for i in nonZeroIndices]
    
    # resulting coordinates
    yCoordinatesSet = [set(yCoordinates[i]) for i in range(len(yCoordinates))]
    yCoordinatesSet = [value for inner_list in yCoordinatesSet for value in inner_list]
    
    gapx = 50
    gapy = 50
    
    # _______________________Visualization______________________________
    # __________________________________________________________________
    
    st.subheader("Cross-Section")
    
    # concrete cross-section
    scaleY = height / 400
    scaleX = 400 / height
    fig = go.Figure(go.Scatter(x=[gapx + 0,gapx + width,gapx + width,gapx + 0, gapx + 0], 
                            y=[0 + gapy,0 + gapy, height + gapy,height + gapy, 0 + gapy], 
                            line=dict(color='darkgrey'),
                            mode="lines",
                            fillcolor='lightgrey',  
                            fill="toself",
                            opacity=0.7))
    
    # bolt markers
    for i in range(len(xCoordinates)):
        add_rebar(fig, xCoordinates[i], yCoordinates[i], rebarList[i], gapx, gapy)
    
    # hatching
    pyLogo = Image.open("concrete_hatching.png")
    fig.add_layout_image(
            dict(source=pyLogo, xref="x", yref="y",
                x = gapx, y = gapy + height,
                sizex = width, sizey = height,
                sizing = "fill", opacity=1,
                layer="below"))
    
    # stirrups
    t = stirrups * 1/2 + max(rebarBot1, rebarTop1) / 2
    xList = [gapx + edgeHorizontal - t, gapx + width - edgeHorizontal + t, gapx + width - edgeHorizontal + t, gapx + edgeHorizontal - t, gapx + edgeHorizontal - t]
    yList = [gapy + edgeVertical - t, gapy + edgeVertical - t, gapy + height - edgeVertical + t, gapy + height - edgeVertical + t, gapy + edgeVertical - t]
    #go_scatter = plotly_go_scatter_stirrup(xList, yList, "grey", stirrups * scaleX)
    
    #____________________TEXT____________________
    # text sizes
    titleSize = + 20
    textSize = 18
    annotationSize = 15
    scaleY = height / 400
    scaleX = width / 200
    
    # title
    x = gapx
    y = gapy + height + 80 * scaleY
    add_text(fig, f"<b>{title}", x , y, titleSize)
    add_text(fig, concrete, x , y - 20 * 1 * scaleY, textSize)
    add_text(fig, text, x , y - 20 * 2 * scaleY, textSize)
    
    # annotation
    # width
    x = gapx / 2 + width / 2
    y = 5 
    add_text(fig, int(width), x, y, annotationSize)    
    
    # height
    x = - 20 * scaleX
    y = gapy + height / 2 - 20 
    add_text(fig, int(height), x, y, annotationSize)   
    
    # rebar information
    Asu1 = round(noBot1 * (rebarBot1/10)**2 / 4 * pi, 1)
    Asu2 = round(noBot2 * (rebarBot2/10)**2 / 4 * pi, 1)
    Asu3 = round(noBot3 * (rebarBot3/10)**2 / 4 * pi, 1)
    Aso1 = round(noTop1 * (rebarTop1/10)**2 / 4 * pi, 1)
    Aso2 = round(noTop2 * (rebarTop2/10)**2 / 4 * pi, 1)
    asw = round(100/dsw * (stirrups/10)**2 / 4 * pi * sleeks, 1)
    
    textAsu1 = f"A<sub>s.bot.1</sub>= {noBot1} x ⌀{rebarBot1} = {Asu1} cm<sup>2</sup>"
    textAsu2 = f"A<sub>s.bot.2</sub> = {noBot2} x ⌀{rebarBot2} = {Asu2} cm<sup>2</sup>"
    textAsu3 = f"A<sub>s.bot.3</sub> = {noBot3} x ⌀{rebarBot3} = {Asu3} cm<sup>2</sup>"
    textAso1 = f"A<sub>s.top.1</sub> = {noTop1} x ⌀{rebarTop1} = {Aso1} cm<sup>2</sup>"
    textAso2 = f"A<sub>s.top.2</sub> = {noTop2} x ⌀{rebarTop2} = {Aso2} cm<sup>2</sup>"
    textAsw = f"a<sub>sw</sub> = ⌀{stirrups} / {dsw} cm x {sleeks} = {asw} cm<sup>2</sup>/m"
    
    textAs = [textAso1, textAso2, textAsu1, textAsu2, textAsu3]
    AsList = [Aso1, Aso2, Asu1, Asu2, Asu3]
    
    AsuCount = []
    AsoCount = []
    
    # reinforcement text
    verticalDistanceText = 20  * scaleY
    x0 = gapx + width + 50
    y0 = gapy + height * 3/4  
    add_text(fig, "<b>Reinforcement</b>", x0, y0, textSize)
    
    for n,i in enumerate(nonZeroIndices):
        x = x0
        y = y0 - verticalDistanceText * (n + 1)
        add_text(fig, textAs[i], x, y, textSize)
        if i > 1:
            AsuCount.append(AsList[i])
        if i < 2:
            AsoCount.append(AsList[i])
    
    x = x0
    y = y0 - verticalDistanceText * (n + 3)
    add_text(fig, f"<b>Total", x, y, textSize)
    
    y = y0 - verticalDistanceText * (n + 4)
    add_text(fig, f"A<sub>s.top.tot</sub> = {round(sum(AsoCount),1)} cm<sup>2</sup>", x, y, textSize)
    
    y = y0 - verticalDistanceText * (n + 5)
    add_text(fig, f"A<sub>s.bot.tot</sub> = {round(sum(AsuCount),1)} cm<sup>2</sup>", x, y, textSize)
    
    y = y0 - verticalDistanceText * (n + 6)
    add_text(fig, textAsw, x, y, textSize)
    
    y = y0 - verticalDistanceText * (n + 8)
    add_text(fig, f"cover = {edgeVertical} mm", x, y, textSize)
    
    # dimension height
    xList = [-20 * scaleX, -20 * scaleX]
    yList = [gapy, height + gapy]
    draw_arrow(fig, xList, yList, "Y", scaleX, scaleY)
    
    # dimension width
    xList = [gapx, gapx + width]
    yList = [-10 * scaleY, -10 * scaleY]
    draw_arrow(fig, xList, yList, "X", scaleX, scaleY)
    
    # update layout
    fig.update_layout(
        autosize=False,
        width = 800,
        height = 700,
        uirevision='static',
        showlegend=False)
    
    # Set the aspect ratio to be equal
    fig.update_layout(
        xaxis=dict(scaleanchor="y", scaleratio=1, fixedrange=True, visible=False),
        yaxis=dict(scaleanchor="x", scaleratio=1, fixedrange=True, visible=False),
        uirevision='static')  # Disable zoom functionality
    
    # Hide the axis
    fig.update_xaxes(showline=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showline=False, showgrid=False, zeroline=False)
    
    
    st.write(fig)

except:
    st.warning("Some error happened - change input.")

st.write("")
st.write("")
st.write("")
st.write("")

text = '<p style="font-family:Arial; color:rgb(114, 114, 114); font-size: 10px;">Cal Mense (M.Eng.) | Concrete Beam Visualizer | v.1</p>'
st.markdown(text, unsafe_allow_html=True)
