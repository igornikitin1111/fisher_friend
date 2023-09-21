import PySimpleGUI as sg
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import Base, Zuvis, Rusis, Vietove



# Duomenu baze
db_engine = create_engine('sqlite:///fisher_friend_database.db')

# Sesijos kurimas
Session = sessionmaker(db_engine)
session = Session()

# Funkcija zuvies pridejimui
def prideti_zuvi(values):
    svoris = float(values['-SVORIS-'])
    ilgis = float(values['-ILGIS-'])
    kada_pagauta = values['-KADA_PAGAUTA-']
    rusis_pavadinimas = values['-RUSIS-']
    vietoves_pavadinimas = values['-VIETOVE-']

#Kitos funkcijos
#
#
#

layout = [
    [sg.TabGroup([
        [sg.Tab('Prideti', [
            [sg.Text("Svoris:"), sg.InputText(key='-SVORIS-')],
            [sg.Text("Ilgis:"), sg.InputText(key='-ILGIS-')],
            [sg.Text("Pagavimo data:"), sg.InputText(key='-KADA_PAGAUTA-')],
            [sg.Text("Rusis:"), sg.Combo(values=[], enable_events=True, key='-RUSIS-'), sg.Button("Prideti rusi")],
            [sg.Text("Vietove:"), sg.Combo(values=[], enable_events=True, key='-VIETOVE-'), sg.Button("Prideti vietove")],
            [sg.Button("Prideti")]
        ])],
        [sg.Tab('Perziurėti zuvis', [
            [sg.Table(values=[], headings=['ID', 'SVORIS', 'ILGIS', 'RUSIS', 'VIETOVE', 'PAGAVIMO DATA'], 
                      col_widths=[4, 14, 14, 14, 14, 14], justification='center', auto_size_columns=False,
                        key='-TABLE-', select_mode='extended', enable_events=True)],
            [sg.Button("Istrinti")]
        ])]
    ])]
]

window = sg.Window("Fisher Friend Programa", layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Atšaukti':
        break
window.close()