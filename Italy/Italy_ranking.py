#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


df = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv')
focus = df.copy().drop(['stato','codice_regione','codice_provincia','sigla_provincia','lat','long','note'], axis=1).set_index(['data'])
#totale_casi denominazione_provincia denominazione_regione

confirm_r = focus.groupby('denominazione_regione').sum().T
confirm_p = focus.groupby('denominazione_provincia').sum().T

cols=['Province','COVID-Free Days','New Cases in Last 14 Days', 'Last7', 'Previous7']
import datetime as dt
collect = []
for country in confirm_p.columns:
    if country != 'In fase di definizione/aggiornamento':
        bula = focus[focus['denominazione_provincia']==country]
        bula2 = bula.copy().drop(['denominazione_provincia','denominazione_regione'], axis=1).diff()
        ave = bula2['totale_casi']
        las = len(ave)-14
        last_forteen = ave[las:].sum()
        if last_forteen < 0:
            last_forteen = 0
        last7 = ave[len(ave)-7:].sum() #last week
        prev7 = ave[len(ave)-14:len(ave)-7].sum() #prev week
        if last7 < 0:
            last7 = 0
        if last7 > last_forteen:
            last_forteen = last7
        if prev7 < 0:
            prev7 = 0
        if (last7 == 0) & (last_forteen == 0):
            prev7 = 0
        i = len(ave)-1
        c = 0
        while i > 0:
            if ave[i] <= 0:
                c = c + 1
            else:
                i = 0
            i = i - 1
        last_forteen = int(last_forteen)
        last7 = int(last7)
        prev7 = int(prev7)
        collect.append((country,
                       c,
                       last_forteen,
                       last7,
                       prev7))

thr = pd.DataFrame(collect, columns=cols)
fin = thr.sort_values(['COVID-Free Days'], ascending=[False])
fin['week'] = fin['COVID-Free Days'].gt(13) 
tab = fin.sort_values(['week'], ascending=[False])
tab_t = tab[tab['week']==True]
tab_f = tab[tab['week']==False]
tab_f = tab_f.sort_values(['New Cases in Last 14 Days','COVID-Free Days'], ascending = [True,False])
tab_t = tab_t.sort_values(['COVID-Free Days','New Cases in Last 14 Days'], ascending = [False,True])
tab = tab_t.append(tab_f)
tab = tab.drop(['week'], axis=1)

#Percent Change

tab['PercentChange'] = 100*(tab['Last7'] - tab['Previous7'])/(tab['Last7']+tab['Previous7'])
tab['PercentChange'] = tab['PercentChange'].fillna(0.0)

tab = tab.drop(['Previous7'], axis = 1)
tab.columns = ['Province', 'COVID-Free Days', 'New Cases in Last 14 Days', 'Last 7 Days', 'Pct Change']

def highlighter(s):
    val_1 = s['COVID-Free Days']
    val_2 = s['New Cases in Last 14 Days']
    
    r=''
    try:
        if val_1>=14: #More than 14 Covid free days
            r = 'background-color: #018001; color: #ffffff;'
        elif 20>=val_2 : # less than 20 in last 2 weeks
            r = 'background-color: #02be02; color: #ffffff;'
        elif 200>=val_2 >=21: #Light green
            r = 'background-color: #ffff01;'
        elif 1000>=val_2 >= 201: #Yellow
            r = 'background-color: #ffa501;'
        elif 20000>=val_2 >= 1001: #Orange
            r = 'background-color: #ff3434;'
        elif val_2 > 20001: # Red
            r = 'background-color: #990033;'
    except Exception as e:
        r = 'background-color: white'
    return [r]*(len(s)-2) + ['']*2

def hover(hover_color="#ffff99"):
    return dict(selector="tbody tr:hover td, tbody tr:hover th",
                props=[("background-color", "rgba(66, 165, 245, 0.2) !important")])

top = """
<!DOCTYPE html>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
<html>
<head>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
<script>
function colorize() {
var NW = String.fromCharCode(8599);
var SW = String.fromCharCode(8600);
$('td').each(function() {
    $(this).html($(this).html().
    replace(SW, '<span style="color: green">'+ SW +'</span>').
    replace(NW, '<span style="color: red">'+ NW +'</span>'))
    ;
});
};
</script>
<style>

    h2 {
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
    }
    table { 
        margin-left: auto;
        margin-right: auto;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    th, td {
        padding: 5px;
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 90%;
    }
    table tbody tr:hover {
        background-color: #dddddd;
    }
    /*
    table tbody tr:hover td, table tbody tr:hover th {
  background-color: #dddddd !important;
    }
    /*
    .wide {
        width: 90%; 
    }

</style>
</head>
<body onload=colorize()>
"""
bottom = """
</body>
</html>
"""

arrow = lambda x : ' &#x2197;' if x>0 else (' &#x2192' if x ==0  else ' &#x2198')
styles=[hover(),]
tab['Rank'] = tab.reset_index().index
tab['Rank'] = tab['Rank'].add(1)
tab['Trend'] = tab['Pct Change'].map(arrow)
tab['Percent Change'] = tab['Pct Change'].map('{:,.2f}%'.format) + tab['Trend']
tab = tab.drop(['Trend','Pct Change'], axis = 1)

tab = tab[['Rank', 'Province', 'COVID-Free Days', 'New Cases in Last 14 Days','Last 7 Days','Percent Change']]       
s = tab.style.apply(highlighter, axis = 1).set_table_styles(styles).hide_index()

try:        
    with open(f'Italy.html', 'w', encoding="utf-8") as out:
        content = top + s.render() + bottom
        out.write(content)
except Exception as e:
    print(f'Error:\n{e}')