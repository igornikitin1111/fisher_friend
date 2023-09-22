import PySimpleGUI as sg
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import Base, Zuvis, Rusis, Vietove
from datetime import datetime


db_engine = create_engine('sqlite:///fisher_friend_database.db')

Session = sessionmaker(db_engine)
session = Session()

def atnaujinti_duomenis_layout(selected_data, window):
    zuvis = selected_data[0]
    layout = [
        [sg.Text("Svoris: "), sg.InputText(key='-SVORIS-', default_text=str(zuvis.svoris))],
        [sg.Text("Ilgis: "), sg.InputText(key='-ILGIS-', default_text=str(zuvis.ilgis))],
        [sg.Text("Pagavimo data: "), sg.InputText(key='-PAGAVIMO-DATA-', default_text=zuvis.kada_pagauta)],
        [sg.Text("Rūšis: "), sg.Combo(values=ikelti_rusis(), enable_events=True, key='-RUSIS-', size=(8, 10), readonly=True, default_value=zuvis.rusis)],
        [sg.Text("Vietovė: "), sg.Combo(values=ikelti_vietoves(), enable_events=True, key='-VIETOVE-', size=(15, 10), readonly=True, default_value=zuvis.vietove)],
        [sg.Button("Atnaujinti", key="-ATNAUJINTI-"), sg.Button("Išeiti", key='-ISEITI-ATNAUJINTI-')]
    ]
    window_atnaujinti = sg.Window('', layout, finalize=True)
    while True:
        event, values = window_atnaujinti.read()
        if event == sg.WIN_CLOSED or event == "-ISEITI-ATNAUJINTI-":
            break
        if event == "-ATNAUJINTI-":
            atnaujinti_duomenis(selected_data, values)
            window['-TABLE-ZUVIS-'].update(values=ikelti_zuvis(window))
            window_atnaujinti.close()
    window_atnaujinti.close()

def atnaujinti_duomenis(selected_data, values):
    svoris = values['-SVORIS-']
    ilgis = values['-ILGIS-']
    kada_pagauta_str = values['-PAGAVIMO-DATA-']
    rusis_pavadinimas = values['-RUSIS-']
    vietove_pavadinimas = values['-VIETOVE-']
    try:
        kada_pagauta = datetime.strptime(kada_pagauta_str, '%Y-%m-%d').date()
    except ValueError:
        sg.popup('Neteisingas datos formatas. Turi būti YYYY-MM-DD...', title='')
        return
    zuvis = selected_data[0]
    zuvis.svoris = svoris
    zuvis.ilgis = ilgis
    zuvis.kada_pagauta = kada_pagauta
    zuvis.rusis = rusis_pavadinimas
    zuvis.vietove = vietove_pavadinimas
    session.commit()




def prideti_rusi():
    while True:
        rusis_pavadinimas = sg.popup_get_text("Įveskite rūšį, kurią norite pridėti: ",)
        if rusis_pavadinimas is None:
            break
        if rusis_pavadinimas:
            yra_rusis = session.query(Rusis).filter_by(pavadinimas=rusis_pavadinimas).first()
            if yra_rusis:
                sg.popup(f"Rūšis '{rusis_pavadinimas}' jau egzistuoja. Bandykite pridėti kitą rūšį...")
            else:
                nauja_rusis = Rusis(pavadinimas=rusis_pavadinimas)
                session.add(nauja_rusis)
                session.commit()
                sg.popup(f"Rūšis '{rusis_pavadinimas}' sėkmingai pridėta...")
                break
        else:
            sg.popup("Laukelis privalo būti užpildytas...")

def istrinti_rusi_layout():
    layout = [
        [sg.Listbox(values=ikelti_rusis(), key='-ISTRINTI-RUSI-', size=(8, 5), select_mode='extended')],
        [sg.Button('Ištrinti'), sg.Button('Išeiti')],
    ]
    window_istrinti = sg.Window('', layout)
    while True:
        event, values = window_istrinti.read()
        if event == sg.WIN_CLOSED or event == "Išeiti":
            break
        if event == 'Ištrinti':
            pasirinktos_rusys = values['-ISTRINTI-RUSI-']
            istrinti_rusi(pasirinktos_rusys, window_istrinti)
    window_istrinti.close()

def istrinti_rusi(pasirinktos_rusys, window_istrinti):
    if pasirinktos_rusys:
        for pasirinkta_rusis in pasirinktos_rusys:
            session.delete(pasirinkta_rusis)
            session.commit()
            sg.popup(f"Žuvies rūšis '{pasirinkta_rusis}' sėkmingai ištrinta...")
    window_istrinti['-ISTRINTI-RUSI-'].update(values=ikelti_rusis())
    window['-RUSIS-'].update(values=ikelti_rusis())


def ikelti_rusis():
    rusys = session.query(Rusis).all()
    return rusys

def ikelti_zuvis(window):
    zuvys = session.query(Zuvis).all()
    data = [(zuvis.id, zuvis.svoris, zuvis.ilgis, zuvis.rusis.pavadinimas, zuvis.vietove, zuvis.kada_pagauta) for zuvis in zuvys]
    window['-TABLE-ZUVIS-'].update(values=data)


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
            prideti_vietove(values, window_vietove)
    window_vietove.close()

def prideti_vietove(values, window_vietove):
    pavadinimas = values['-VIETOVE-']
    tipas = values['-TIPAS-']
    if not pavadinimas.strip() and not tipas.strip():
        sg.popup('Vietovės pavadinimas ir tipas turi būti užpildyti...', title='')
    elif not tipas.strip():
        sg.popup('Vietovės tipas turi būti pasirinktas...', title='')
    elif not pavadinimas.strip():
        sg.popup('Vietovės pavadinimas turi būti užpildyti...', title='')
    else:
        nauja_vietove = Vietove(pavadinimas=pavadinimas, tipas=tipas)
        session.add(nauja_vietove)
        session.commit()
        sg.popup(f"Vietovė '{nauja_vietove.pavadinimas}, {nauja_vietove.tipas}' sėkmingai pridėta...")
        window_vietove.close()


def ikelti_vietoves():
    vietoves = session.query(Vietove).all()
    return vietoves

def istrinti_vietove_layout():
    layout = [[sg.Listbox(values=ikelti_vietoves(), size=(15, 10), key='-ISTRINTI-VIETOVE-', select_mode='extended')],
              [sg.Button('Ištrinti'), sg.Button('Išeiti')],
    ]
    window_istrinti_vietove = sg.Window('', layout)
    while True:
        event, values = window_istrinti_vietove.read()
        if event == sg.WIN_CLOSED or event == 'Išeiti':
            break
        if event == 'Ištrinti':
            pasirinktos_vietoves = values['-ISTRINTI-VIETOVE-']
            istrinti_vietove(pasirinktos_vietoves, window_istrinti_vietove)
    window_istrinti_vietove.close()

def istrinti_vietove(pasirinktos_vietoves, window_istrinti_vietove):
    if pasirinktos_vietoves:
        for pasirinkta_vietove in pasirinktos_vietoves:
            session.delete(pasirinkta_vietove)
            sg.popup(f"Vietovė '{pasirinkta_vietove}' sėkmingai ištrinta...")
        session.commit()
    window['-VIETOVE-'].update(values=ikelti_vietoves())
    window_istrinti_vietove['-ISTRINTI-VIETOVE-'].update(values=ikelti_vietoves())



layout = [
    [sg.TabGroup([
        [sg.Tab('Pridėti', [
            [sg.Text("Svoris:"), sg.InputText(key='-SVORIS-')],
            [sg.Text("Ilgis:"), sg.InputText(key='-ILGIS-')],
            [sg.Text("Pagavimo data:"), sg.InputText(key='-KADA_PAGAUTA-')],
            [sg.Text("Rūšis:"), sg.Combo(values=ikelti_rusis(), enable_events=True, key='-RUSIS-', size=(8, 10), readonly=True), sg.Button("Pridėti rūšį"), sg.Button("Ištrinti rūšį")],
            [sg.Text("Vietovė:"), sg.Combo(values=ikelti_vietoves(), enable_events=True, key='-VIETOVE-', size=(15, 10), readonly=True), sg.Button("Pridėti vietovę"), sg.Button("Ištrinti vietovę")],
            [sg.Button("Pridėti"), sg.Button("Išeiti")]
        ])],
        [sg.Tab('Peržiūrėti žuvis', [
            [sg.Table(values=[], headings=['ID', 'SVORIS', 'ILGIS', 'RŪŠIS', 'VIETOVĖ', 'PAGAVIMO DATA'], 
                      col_widths=[4, 14, 14, 14, 14, 14], justification='center', auto_size_columns=False,
                        key='-TABLE-ZUVIS-', select_mode='extended', enable_events=True)],
            [sg.Button("Ištrinti", disabled=True), sg.Button("Atnaujinti duomenis", disabled=True), sg.Button("Išeiti", key='-ISEITI-')]
        ])]
    ])]
]

def prideti_zuvi(values):
    svoris = values['-SVORIS-']
    ilgis = values['-ILGIS-']
    kada_pagauta = values['-KADA_PAGAUTA-']
    rusis = values['-RUSIS-']
    vietove = values['-VIETOVE-']
    if not svoris.isdigit():
        sg.popup('Svoris turi būti skaičius...', title='')
        return
    if not ilgis.isdigit():
        sg.popup('Ilgis turi būti skaičius...', title='')
        return
    if not svoris or not ilgis or not kada_pagauta or not rusis or not vietove:
        sg.popup('Visi laukai turi būti užpildyti...', title='')
    else:
        try:
            kada_pagauta = datetime.strptime(kada_pagauta, '%Y-%m-%d').date()
            nauja_zuvis = Zuvis(svoris=svoris, ilgis=ilgis, kada_pagauta=kada_pagauta, rusis=rusis, vietove=vietove)
        except ValueError:
            sg.popup('Neteisingas datos formatas. Turi būti YYYY-MM-DD...', title='')
        else:
            session.add(nauja_zuvis)
            session.commit()
            sg.popup("Žuvis sėkmingai pridėta...")


def istrinti_zuvi(selected_data):
    if selected_data:
        deleted_ids = []
        for zuvis in selected_data:
            zuvis_id = zuvis.id
            patvirtinimas = sg.popup_yes_no(f'Ar tikrai norite ištrinti žuvį "ID {zuvis_id}"?', title='')
            if patvirtinimas == 'Yes':
                session.delete(zuvis)
                deleted_ids.append(zuvis_id)
            if patvirtinimas == 'No':
                pass
        session.commit()
        ikelti_zuvis(window)
        if len(deleted_ids) == 1:
            sg.popup(f'Žuvis "ID {deleted_ids[0]}" sėkmingai ištrinta...', title='')
        elif len(deleted_ids) > 1:
            sg.popup(f'Žuvys "ID {", ".join(map(str, deleted_ids))}" sėkmingai ištrintos...', title='')
        elif len(deleted_ids) == 0:
            pass


window = sg.Window("Fisher Friend Programa", layout, finalize=True)
ikelti_zuvis(window)
while True:
    event, values = window.read()
    if values is not None:
        selected_row_indexes = values['-TABLE-ZUVIS-']
        if selected_row_indexes:
            zuvys = session.query(Zuvis).all()
            selected_data = [zuvys[i] for i in selected_row_indexes]
        else:
            selected_data = None
    ikelti_rusis()
    ikelti_vietoves()
    if event == sg.WIN_CLOSED or event == 'Išeiti' or event == '-ISEITI-':
        break
    if event == "Pridėti rūšį":
        prideti_rusi()
        window['-RUSIS-'].update(values=ikelti_rusis())
    elif event == "Ištrinti rūšį":
        istrinti_rusi_layout()
        window['-RUSIS-'].update(values=ikelti_rusis())
    elif event == "Ištrinti vietovę":
        istrinti_vietove_layout()
    elif event == "Pridėti vietovę":
        prideti_vietove_layout()
        window['-VIETOVE-'].update(values=ikelti_vietoves())
    elif event == "Pridėti":
        prideti_zuvi(values)
        ikelti_zuvis(window)
    elif event == "Atnaujinti duomenis":
        atnaujinti_duomenis_layout(selected_data, window)
    elif event == "Ištrinti":
        istrinti_zuvi(selected_data)
    if selected_data:
        window['Ištrinti'].update(disabled=False)
        window['Atnaujinti duomenis'].update(disabled=False)
    else:
        window['Ištrinti'].update(disabled=True)
        window['Atnaujinti duomenis'].update(disabled=True)
window.close()