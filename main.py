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
def prideti_rusi():
    rusis_pavadinimas = sg.popup_get_text("Įveskite rūšį, kurią norite pridėti: ")
    if rusis_pavadinimas:
        yra_rusis = session.query(Rusis).filter_by(pavadinimas=rusis_pavadinimas).first()
        if yra_rusis:
            sg.popup(f"Rūšis '{rusis_pavadinimas} jau egzistuoja. Bandykite pridėti kitą rūšį...'")
        else:
            nauja_rusis = Rusis(pavadinimas=rusis_pavadinimas)
            session.add(nauja_rusis)
            session.commit()
            sg.popup(f"Rūšis '{rusis_pavadinimas} sėkmingai pridėta...")
            ikelti_rusis()

def istrinti_rusi():
    layout = [[sg.Listbox(values=ikelti_rusis(), key='-ISTRINTI-RUSI-')],
              [sg.Button('Ištrinti'), sg.Button('Išeiti')],
    ]
    window_istrinti = sg.Window('', layout)
    while True:
        event, values = window_istrinti.read()
        if event == sg.WIN_CLOSED or event == 'Išeiti':
            break
        if event == 'Ištrinti':
            pass
    window_istrinti.close()

def ikelti_rusis():
    rusys = session.query(Rusis).all()
    data_rusis = [(rusis.pavadinimas) for rusis in rusys]
    return data_rusis

def istrinti_vietove():
    layout = [[sg.Listbox(values=[], key='-ISTRINTI-VIETOVE-')],
              [sg.Button('Ištrinti'), sg.Button('Išeiti')],
    ]
    window_istrinti = sg.Window('', layout)
    while True:
        event, values = window_istrinti.read()
        if event == sg.WIN_CLOSED or event == 'Išeiti':
            break
        if event == 'Ištrinti':
            pass
    window_istrinti.close()


#
#

layout = [
    [sg.TabGroup([
        [sg.Tab('Prideti', [
            [sg.Text("Svoris:"), sg.InputText(key='-SVORIS-')],
            [sg.Text("Ilgis:"), sg.InputText(key='-ILGIS-')],
            [sg.Text("Pagavimo data:"), sg.InputText(key='-KADA_PAGAUTA-')],
            [sg.Text("Rusis:"), sg.Combo(values=[], enable_events=True, key='-RUSIS-'), sg.Button("Pridėti rūšį"), sg.Button("Ištrinti rūšį")],
            [sg.Text("Vietove:"), sg.Combo(values=[], enable_events=True, key='-VIETOVE-'), sg.Button("Prideti vietove"), sg.Button("Ištrinti vietovę")],
            [sg.Button("Prideti"), sg.Button('Update')]
        ])],
        [sg.Tab('Perziurėti zuvis', [
            [sg.Table(values=[], headings=['ID', 'SVORIS', 'ILGIS', 'RUSIS', 'VIETOVE', 'PAGAVIMO DATA'], 
                      col_widths=[4, 14, 14, 14, 14, 14], justification='center', auto_size_columns=False,
                        key='-TABLE-', select_mode='extended', enable_events=True)],
            [sg.Button("Istrinti")]
        ])]
    ])]
]

window = sg.Window("Fisher Friend Programa", layout, finalize=True)
while True:
    event, values = window.read()
    ikelti_rusis()
    if event == sg.WIN_CLOSED or event == 'Atšaukti':
        break
    if event == "Pridėti rūšį":
        prideti_rusi()
    if event == "Ištrinti rūšį":
        istrinti_rusi()
    if event == "Ištrinti vietovę":
        istrinti_vietove()
    if event == 'UPDATE':
        ikelti_rusis()
window.close()