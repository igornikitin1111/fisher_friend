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

def istrinti_rusi_layout():
    layout = [[sg.Listbox(values=ikelti_rusis(), key='-ISTRINTI-RUSI-', size=(8, 5))],
              [sg.Button('Ištrinti'), sg.Button('Išeiti')],
    ]
    window_istrinti = sg.Window('', layout)
    while True:
        event, values = window_istrinti.read()
        if event == sg.WIN_CLOSED or event == 'Išeiti':
            break
        if event == 'Ištrinti':
            pasirinkta_rusis = values['-ISTRINTI-RUSI-']
            if pasirinkta_rusis:
                istrinti_rusi(pasirinkta_rusis[0])
    window_istrinti.close()

def istrinti_rusi(pasirinkta_rusis):
    rusis_istrinimui = session.query(Rusis).filter_by(pavadinimas=pasirinkta_rusis).first()
    if rusis_istrinimui:
        session.delete(rusis_istrinimui)
        session.commit()


def ikelti_rusis():
    rusys = session.query(Rusis).all()
    data_rusis = [(rusis.pavadinimas) for rusis in rusys]
    return data_rusis

def ikelti_tipus():
    tipai = session.query(Vietove).all()
    data_tipas = [(vietove.tipas) for vietove in tipai]
    return data_tipas
def prideti_vietove_layout():
    layout = [
        [sg.Text("Pavadinimas: "), sg.InputText(key='-VIETOVE-')],
        [sg.Text("Telkinys: "), sg.Combo(values=['ežeras', 'tvenkinys', 'upė', 'jūra'], key='-TIPAS-')],
        [sg.Button("Pridėti"), sg.Button("Išeiti")]
    ]
    window_vietove = sg.Window('', layout)
    while True:
        event, values = window_vietove.read()
        if event == sg.WIN_CLOSED or event == "Išeiti":
            break
        if event == "Pridėti":
            prideti_vietove(values)
            window_vietove.close()

def prideti_vietove(values):
    pavadinimas = values['-VIETOVE-']
    tipas = values['-TIPAS-']
    nauja_vietove = Vietove(pavadinimas=pavadinimas, tipas=tipas)
    session.add(nauja_vietove)
    session.commit()
    sg.popup(f"Vietovė '{nauja_vietove.pavadinimas}, {nauja_vietove.tipas}' sėkmingai pridėta...'")

def ikelti_vietoves():
    vietoves = session.query(Vietove).all()
    data_vietoves = [(vietove.pavadinimas, vietove.tipas) for vietove in vietoves]
    return data_vietoves

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


layout = [
    [sg.TabGroup([
        [sg.Tab('Prideti', [
            [sg.Text("Svoris:"), sg.InputText(key='-SVORIS-')],
            [sg.Text("Ilgis:"), sg.InputText(key='-ILGIS-')],
            [sg.Text("Pagavimo data:"), sg.InputText(key='-KADA_PAGAUTA-')],
            [sg.Text("Rusis:"), sg.Combo(values=ikelti_rusis(), enable_events=True, key='-RUSIS-', size=(8, 10)), sg.Button("Pridėti rūšį"), sg.Button("Ištrinti rūšį")],
            [sg.Text("Vietove:"), sg.Combo(values=ikelti_vietoves(), enable_events=True, key='-VIETOVE-'), sg.Button("Pridėti vietovę"), sg.Button("Ištrinti vietovę")],
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

window = sg.Window("Fisher Friend Programa", layout, finalize=True)
while True:
    event, values = window.read()
    ikelti_rusis()
    ikelti_vietoves()
    if event == sg.WIN_CLOSED or event == 'Atšaukti':
        break
    if event == "Pridėti rūšį":
        prideti_rusi()
        window['-RUSIS-'].update(values=ikelti_rusis())
    if event == "Ištrinti rūšį":
        istrinti_rusi_layout()
    if event == "Ištrinti vietovę":
        istrinti_vietove()
    if event == "Pridėti vietovę":
        prideti_vietove_layout()
        window['-VIETOVE-'].update(values=ikelti_vietoves())
window.close()