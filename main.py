import PySimpleGUI as sg
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import Base, Zuvis, Rusis, Vietove
from datetime import datetime
import csv

db_engine = create_engine('sqlite:///fisher_friend_database.db')

Session = sessionmaker(db_engine)
session = Session()

sg.theme('DarkTeal12')

##############################################################################
def atnaujinti_duomenis_layout(selected_data, window):
    zuvis = selected_data[0]
    layout = [
        [sg.Text("Svoris:", justification='left', size=12), sg.InputText(key='-SVORIS-', default_text=str(zuvis.svoris), size=10)],
        [sg.Text("Ilgis:", justification='left', size=12), sg.InputText(key='-ILGIS-', default_text=str(zuvis.ilgis), size=10)],
        [sg.Text("Pagavimo data:", justification='left', size=12), sg.InputText(key='-PAGAVIMO-DATA-', default_text=zuvis.kada_pagauta, size=10)],
        [sg.Text("Rūšis:", justification='left', size=7), sg.Combo(values=ikelti_rusis(), enable_events=True, key='-RUSIS-', size=(14, 10), readonly=True, default_value=zuvis.rusis)],
        [sg.Text("Vietovė:", justification='left', size=7), sg.Combo(values=ikelti_vietoves(), enable_events=True, key='-VIETOVE-', size=(14, 10), readonly=True, default_value=zuvis.vietove)],
        [sg.Button("Atnaujinti", key="-ATNAUJINTI-"), sg.Text('', size=8), sg.Button("Išeiti", key='-ISEITI-ATNAUJINTI-')]
    ]
    window_atnaujinti = sg.Window('', layout, finalize=True)
    window_atnaujinti.set_icon(r"icon.ico")
    while True:
        event, values = window_atnaujinti.read()
        if event == sg.WIN_CLOSED or event == "-ISEITI-ATNAUJINTI-":
            break
        if event == "-ATNAUJINTI-":
            atnaujinti_duomenis(selected_data, values, window_atnaujinti)
            window['-TABLE-ZUVIS-'].update(values=ikelti_zuvis(window))
    window_atnaujinti.close()

def atnaujinti_duomenis(selected_data, values, window_atnaujinti):
    while True:
        svoris_str = values['-SVORIS-']
        ilgis_str = values['-ILGIS-']
        kada_pagauta_str = values['-PAGAVIMO-DATA-']
        rusis_pavadinimas = values['-RUSIS-']
        vietove_pavadinimas = values['-VIETOVE-']
        svoris_valid = True
        ilgis_valid = True
        if not svoris_str or not ilgis_str or not kada_pagauta_str:
            sg.popup('Visi laukai turi būti užpildyti...', title='', icon=r"icon.ico")
            return
        try:
            svoris = float(svoris_str)
        except ValueError:
            svoris_valid = False
        try:
            ilgis = float(ilgis_str)
        except ValueError:
            ilgis_valid = False
        if not svoris_valid and not ilgis_valid:
            sg.popup('Svoris ir ilgis turi būti skaičiai...', title='', icon=r"icon.ico")
            return
        elif not svoris_valid:
            sg.popup('Svoris turi būti skaičius...', title='', icon=r"icon.ico")
            return
        elif not ilgis_valid:
            sg.popup('Ilgis turi būti skaičius...', title='', icon=r"icon.ico")
            return
        else:
            try:
                kada_pagauta = datetime.strptime(kada_pagauta_str, '%Y-%m-%d').date()
            except ValueError:
                sg.popup('Neteisingas datos formatas. Turi būti YYYY-MM-DD...', title='', icon=r"icon.ico")
                return
            else:
                zuvis = selected_data[0]
                zuvis.svoris = svoris
                zuvis.ilgis = ilgis
                zuvis.kada_pagauta = kada_pagauta
                zuvis.rusis = rusis_pavadinimas
                zuvis.vietove = vietove_pavadinimas
                session.commit()
                window_atnaujinti.close()
                break
##############################################################################


##############################################################################
def prideti_rusi():
    button_text = ('My OK', 'My Cancel')
    while True:
        rusis_pavadinimas = sg.popup_get_text("Įveskite rūšį, kurią norite pridėti: ", ' ', size=26, icon=r"icon.ico")
        if rusis_pavadinimas is None:
            break
        if rusis_pavadinimas:
            yra_rusis = session.query(Rusis).filter_by(pavadinimas=rusis_pavadinimas).first()
            if yra_rusis:
                sg.popup(f"Rūšis '{rusis_pavadinimas}' jau egzistuoja. Bandykite pridėti kitą rūšį...", title='', icon=r"icon.ico")
            else:
                nauja_rusis = Rusis(pavadinimas=rusis_pavadinimas)
                session.add(nauja_rusis)
                session.commit()
                sg.popup(f"Rūšis '{rusis_pavadinimas}' sėkmingai pridėta...", title='', icon=r"icon.ico")
                break
        else:
            sg.popup("Laukelis privalo būti užpildytas...", title='', icon=r"icon.ico")

def istrinti_rusi_layout():
    layout = [
        [sg.Listbox(values=ikelti_rusis(), key='-ISTRINTI-RUSI-', size=(15, 7), select_mode='extended')],
        [sg.Button('Ištrinti'), sg.Text('', size=2), sg.Button('Išeiti')],
    ]
    window_istrinti = sg.Window('', layout, finalize=True)
    window_istrinti.set_icon(r"icon.ico")
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
        deleted_ids = []
        for pasirinkta_rusis in pasirinktos_rusys:
            ar_naudojama = session.query(Zuvis).filter_by(rusis=pasirinkta_rusis).first()
            if ar_naudojama:
                sg.popup(f'Rūšis "{pasirinkta_rusis}" negali būti ištrinta, nes ji yra naudojama lentelėje "Žuvys"...', title='', icon=r"icon.ico")
                return
            else:           
                patvirtinimas = sg.popup_yes_no(f'Ar tikrai norite ištrinti rūšį "{pasirinkta_rusis}"?', title='', icon=r"icon.ico")
                if patvirtinimas == 'Yes':
                    session.delete(pasirinkta_rusis)
                    deleted_ids.append(pasirinkta_rusis)
                if patvirtinimas == 'No':
                    pass
        session.commit()
        if len(deleted_ids) == 1:
            sg.popup(f'Rūšis "{deleted_ids[0]}" sėkmingai ištrinta...', title='', icon=r"icon.ico")
        elif len(deleted_ids) > 1:
            sg.popup(f'Rūšys "{", ".join(map(str, deleted_ids))}" sėkmingai ištrintos...', title='', icon=r"icon.ico")
        elif len(deleted_ids) == 0:
            pass
    window_istrinti['-ISTRINTI-RUSI-'].update(values=ikelti_rusis())
    window['-RUSIS-'].update(values=ikelti_rusis())

def ikelti_rusis():
    rusys = session.query(Rusis).all()
    return rusys
##############################################################################


##############################################################################
def prideti_vietove_layout():
    layout = [
        [sg.Text("Pavadinimas:", size=10), sg.InputText(key='-VIETOVE-', size=20)],
        [sg.Text("Telkinys:", size=10), sg.Combo(values=['ežeras', 'tvenkinys', 'upė', 'jūra', 'marios'], key='-TIPAS-', size=18, readonly=True)],
        [sg.Button("Pridėti"), sg.Text('', size=17), sg.Button("Išeiti")]
    ]
    window_vietove = sg.Window('', layout, finalize=True)
    window_vietove.set_icon(r"icon.ico")
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
        sg.popup('Vietovės pavadinimas ir tipas turi būti užpildyti...', title='', icon=r"icon.ico")
    elif not tipas.strip():
        sg.popup('Vietovės tipas turi būti pasirinktas...', title='', icon=r"icon.ico")
    elif not pavadinimas.strip():
        sg.popup('Vietovės pavadinimas turi būti užpildyti...', title='', icon=r"icon.ico")
    else:
        nauja_vietove = Vietove(pavadinimas=pavadinimas, tipas=tipas)
        session.add(nauja_vietove)
        session.commit()
        sg.popup(f"Vietovė '{nauja_vietove.pavadinimas}, {nauja_vietove.tipas}' sėkmingai pridėta...", title='', icon=r"icon.ico")
        window_vietove.close()

def ikelti_vietoves():
    vietoves = session.query(Vietove).all()
    return vietoves
##############################################################################


##############################################################################
def istrinti_vietove_layout(window):
    layout = [[sg.Listbox(values=ikelti_vietoves(), size=(15, 7), key='-ISTRINTI-VIETOVE-', select_mode='extended')],
              [sg.Button('Ištrinti'), sg.Text('', size=2), sg.Button('Išeiti')],
    ]
    window_istrinti_vietove = sg.Window('', layout, finalize=True)
    window_istrinti_vietove.set_icon(r"icon.ico")
    while True:
        event, values = window_istrinti_vietove.read()
        if event == sg.WIN_CLOSED or event == 'Išeiti':
            break
        if event == 'Ištrinti':
            pasirinktos_vietoves = values['-ISTRINTI-VIETOVE-']
            istrinti_vietove(pasirinktos_vietoves, window_istrinti_vietove, window)
    window_istrinti_vietove.close()

def istrinti_vietove(pasirinktos_vietoves, window_istrinti_vietove, window):
    if pasirinktos_vietoves:
        deleted_ids = []
        for pasirinkta_vietove in pasirinktos_vietoves:
            ar_naudojama = session.query(Zuvis).filter_by(vietove=pasirinkta_vietove).first()
            if ar_naudojama:
                sg.popup(f'Vietovė "{pasirinkta_vietove}" negali būti ištrinta, nes ji yra naudojama lentelėje "Žuvys"...', title='', icon=r"icon.ico")
                return
            else:
                patvirtinimas = sg.popup_yes_no(f'Ar tikrai norite ištrinti vietovę "{pasirinkta_vietove}"?', title='', icon=r"icon.ico")
                if patvirtinimas == 'Yes':
                    session.delete(pasirinkta_vietove)
                    deleted_ids.append(pasirinkta_vietove)
                if patvirtinimas == 'No':
                    pass
        session.commit()
        if len(deleted_ids) == 1:
            sg.popup(f'Vietovė "{deleted_ids[0]}" sėkmingai ištrinta...', title='', icon=r"icon.ico")
        elif len(deleted_ids) > 1:
            sg.popup(f'Vietovės "{" | ".join(map(str, deleted_ids))}" sėkmingai ištrintos...', title='', icon=r"icon.ico")
        elif len(deleted_ids) == 0:
            pass        
    window['-VIETOVE-'].update(values=ikelti_vietoves())
    window_istrinti_vietove['-ISTRINTI-VIETOVE-'].update(values=ikelti_vietoves())
##############################################################################


##############################################################################
def sorted_svoris(window):
    zuvys = session.query(Zuvis).order_by(Zuvis.svoris).all()
    data = [(zuvis.id, zuvis.svoris, zuvis.ilgis, zuvis.rusis.pavadinimas, zuvis.vietove, zuvis.kada_pagauta) for zuvis in zuvys]
    window['-TABLE-ZUVIS-'].update(values=data)

def sorted_ilgis(window):
    zuvys = session.query(Zuvis).order_by(Zuvis.ilgis).all()
    data = [(zuvis.id, zuvis.svoris, zuvis.ilgis, zuvis.rusis.pavadinimas, zuvis.vietove, zuvis.kada_pagauta) for zuvis in zuvys]
    window['-TABLE-ZUVIS-'].update(values=data)

def sorted_rusis(window):
    zuvys = session.query(Zuvis).order_by(Zuvis.rusis.pavadinimas).all()
    data = [(zuvis.id, zuvis.svoris, zuvis.ilgis, zuvis.rusis.pavadinimas, zuvis.vietove, zuvis.kada_pagauta) for zuvis in zuvys]
    window['-TABLE-ZUVIS-'].update(values=data)

def sorted_vietove(window):
    zuvys = session.query(Zuvis).order_by(Zuvis.vietove.pavadinimas).all()
    data = [(zuvis.id, zuvis.svoris, zuvis.ilgis, zuvis.rusis.pavadinimas, zuvis.vietove, zuvis.kada_pagauta) for zuvis in zuvys]
    window['-TABLE-ZUVIS-'].update(values=data)

def sorted_kada_pagauta(window):
    zuvys = session.query(Zuvis).order_by(Zuvis.kada_pagauta).all()
    data = [(zuvis.id, zuvis.svoris, zuvis.ilgis, zuvis.rusis.pavadinimas, zuvis.vietove, zuvis.kada_pagauta) for zuvis in zuvys]
    window['-TABLE-ZUVIS-'].update(values=data)
##############################################################################


##############################################################################
def ikelti_zuvis(window):
    zuvys = session.query(Zuvis).all()
    data = [(zuvis.id, zuvis.svoris, zuvis.ilgis, zuvis.rusis.pavadinimas, zuvis.vietove, zuvis.kada_pagauta) for zuvis in zuvys]
    window['-TABLE-ZUVIS-'].update(values=data)

def prideti_zuvi(values):
    svoris_str = values['-SVORIS-']
    ilgis_str = values['-ILGIS-']
    kada_pagauta = values['-KADA_PAGAUTA-']
    rusis = values['-RUSIS-']
    vietove = values['-VIETOVE-']
    svoris_valid = True
    ilgis_valid = True
    if not svoris_str or not ilgis_str or not kada_pagauta or not rusis or not vietove:
        sg.popup('Visi laukai turi būti užpildyti...', title='', icon=r"icon.ico")
        return
    try:
        svoris = float(svoris_str)
    except ValueError:
        svoris_valid = False
    try:
        ilgis = float(ilgis_str)
    except ValueError:
        ilgis_valid = False
    if not svoris_valid and not ilgis_valid:
        sg.popup('Svoris ir ilgis turi būti skaičiai...', title='', icon=r"icon.ico")
        return
    elif not svoris_valid:
        sg.popup('Svoris turi būti skaičius...', title='', icon=r"icon.ico")
        return
    elif not ilgis_valid:
        sg.popup('Ilgis turi būti skaičius...', title='', icon=r"icon.ico")
        return
    try:
        kada_pagauta = datetime.strptime(kada_pagauta, '%Y-%m-%d').date()
        nauja_zuvis = Zuvis(svoris=svoris, ilgis=ilgis, kada_pagauta=kada_pagauta, rusis=rusis, vietove=vietove)
    except ValueError:
        sg.popup('Neteisingas datos formatas. Turi būti YYYY-MM-DD...', title='', icon=r"icon.ico")
    else:
        session.add(nauja_zuvis)
        session.commit()
        sg.popup("Žuvis sėkmingai pridėta...", title='', icon=r"icon.ico")

def istrinti_zuvi(selected_data):
    if selected_data:
        deleted_ids = []
        for zuvis in selected_data:
            zuvis_id = zuvis.id
            patvirtinimas = sg.popup_yes_no(f'Ar tikrai norite ištrinti žuvį "ID {zuvis_id}, {zuvis.rusis}"?', title='', icon=r"icon.ico")
            if patvirtinimas == 'Yes':
                session.delete(zuvis)
                deleted_ids.append(zuvis_id)
            if patvirtinimas == 'No':
                pass
        session.commit()
        ikelti_zuvis(window)
        if len(deleted_ids) == 1:
            sg.popup(f'Žuvis "ID {deleted_ids[0]}" sėkmingai ištrinta...', title='', icon=r"icon.ico")
        elif len(deleted_ids) > 1:
            sg.popup(f'Žuvys "ID {", ".join(map(str, deleted_ids))}" sėkmingai ištrintos...', title='', icon=r"icon.ico")
        elif len(deleted_ids) == 0:
            pass
##############################################################################


##############################################################################
def filtruoti(window, values):
    zuvys = session.query(Zuvis).all()
    search_query = values['-PAIESKA-'].strip().lower()
    filtered_data = [
        (
            zuvis.id,
            zuvis.svoris,
            zuvis.ilgis,
            zuvis.rusis.pavadinimas,
            f"{zuvis.vietove.pavadinimas}, {zuvis.vietove.tipas}",
            zuvis.kada_pagauta,
        )
        for zuvis in zuvys
        if (
            search_query in str(zuvis.id)
            or search_query in str(zuvis.svoris)
            or search_query in str(zuvis.ilgis)
            or search_query in zuvis.rusis.pavadinimas
            or search_query in f"{zuvis.vietove.pavadinimas.strip().lower()}, {zuvis.vietove.tipas.strip().lower()}"
            or search_query in str(zuvis.kada_pagauta) 
        )
    ]
    window['-TABLE-ZUVIS-'].update(values=filtered_data)
##############################################################################


##############################################################################
def eksportuoti_encode(data, file_path):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'SVORIS(kg)', 'ILGIS(cm)', 'RŪŠIS', 'VIETOVĖ', 'PAGAVIMO DATA'])
        for row in data:
            encoded_row = [str(cell).encode('utf-8').decode('utf-8') for cell in row]
            writer.writerow(encoded_row)

def eksportuoti():
    zuvys = session.query(Zuvis).all()
    export_file_path = sg.popup_get_file('Nurodykite saugojimo kelią...', title=' ', icon=r"icon.ico", save_as=True, file_types=(("CSV Files", "*.csv"),))
    if export_file_path:
        data_to_export = [(zuvis.id, zuvis.svoris, zuvis.ilgis, zuvis.rusis.pavadinimas, zuvis.vietove, zuvis.kada_pagauta) for zuvis in zuvys]
        eksportuoti_encode(data_to_export, export_file_path)
        sg.popup("Duomenys sėkmingai eksportuoti...", title='') 
##############################################################################


layout = [
    [sg.TabGroup([
        [sg.Tab('                        Pridėti                        ', [
            [sg.Text("Svoris: (kg)", justification='left', size=(12, 1)), sg.InputText(key='-SVORIS-', size=(17, 1))],
            [sg.Text("Ilgis: (cm)", justification='left', size=(12, 1)), sg.InputText(key='-ILGIS-', size=(17, 1))],
            [sg.Text("Pagavimo data:", justification='left', size=(12, 1)), sg.InputText(key='-KADA_PAGAUTA-', size=(17, 1))],
            [sg.Text("Rūšis:", justification='left', size=(12, 1)), sg.Combo(values=ikelti_rusis(), enable_events=True, key='-RUSIS-', size=(16, 1), readonly=True), sg.Button("Pridėti rūšį", size=(10, 1)), sg.Button("Ištrinti rūšį", size=(10, 1))],
            [sg.Text("Vietovė:", justification='left', size=(12, 1)), sg.Combo(values=ikelti_vietoves(), enable_events=True, key='-VIETOVE-', size=(16, 1), readonly=True), sg.Button("Pridėti vietovę", size=(10, 1)), sg.Button("Ištrinti vietovę", size=(10, 1))],
            [sg.Button("Pridėti")],
            [sg.Text('', size=(80, 1)), sg.Button("Išeiti")]
        ])],
        [sg.Tab('                                                 Žuvys                                                       ', [
            [sg.Table(values=[], headings=['ID', 'SVORIS (kg)', 'ILGIS (cm)', 'RŪŠIS', 'VIETOVĖ', 'PAGAVIMO DATA'], 
                    col_widths=[4, 14, 14, 14, 14, 14], justification='center', auto_size_columns=False,
                    key='-TABLE-ZUVIS-', select_mode='extended', enable_events=True, enable_click_events=True),],
            [sg.Button("Ištrinti", disabled=True), sg.Button("Atnaujinti duomenis", disabled=True), sg.Button('?'), sg.InputText(key='-PAIESKA-', size=(36, 1)), sg.Button('Filtruoti'), sg.Button('Eksportuoti'), sg.Button("Išeiti", key='-ISEITI-', size=(6, 1))]
        ])],
    ], border_width=0.5, pad=(0, 0))]
]


klaustukas = "Įveskite į laukelį informaciją, pagal kurią bus išfiltruota duomenų lentelė ir paspauskite 'Filtruoti' mygtuką...\
            ************************************************************\
            Jei norite sugrąžinti duomenis, tai dar kartą paspauskite 'Filtruoti' mygtuką...\
            ************************************************************\
                                                   Eksportuojamų duomenų bylos tipas yra 'CSV'..."



def main(session=session):
    global window
    filtruoti_paspaudimai = 0
    paspaudimai_svoris = 0
    paspaudimai_ilgis = 0
    paspaudimai_rusis = 0
    paspaudimai_vietove = 0
    paspaudimai_kada_pagauta = 0
    window = sg.Window("Fisher Friend", layout, finalize=True)
    window.set_icon(r"icon.ico")
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
            istrinti_vietove_layout(window)
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
        elif event == "?":
            sg.popup(klaustukas, icon=r"icon.ico", title='')
        elif event == "Eksportuoti":
           eksportuoti()
        elif event == ('-TABLE-ZUVIS-','+CLICKED+',(-1, 0)):
            pass
        elif event == ('-TABLE-ZUVIS-','+CLICKED+',(-1, 1)):
            paspaudimai_svoris += 1
            if paspaudimai_svoris >= 2:
                ikelti_zuvis(window)
                paspaudimai_svoris = 0
            else:
                sorted_svoris(window)
        elif event == ('-TABLE-ZUVIS-','+CLICKED+',(-1, 2)):
            paspaudimai_ilgis += 1
            if paspaudimai_ilgis >= 2:
                ikelti_zuvis(window)
                paspaudimai_ilgis = 0
            else:
                sorted_ilgis(window)
        elif event == ('-TABLE-ZUVIS-','+CLICKED+',(-1, 3)):
            paspaudimai_rusis += 1
            if paspaudimai_rusis >= 2:
                ikelti_zuvis(window)
                paspaudimai_rusis = 0
            else:
                sorted_rusis(window)
        elif event == ('-TABLE-ZUVIS-','+CLICKED+',(-1, 4)):
            paspaudimai_vietove += 1
            if paspaudimai_vietove >= 2:
                ikelti_zuvis(window)
                paspaudimai_vietove = 0
            else:
                sorted_vietove(window)
        elif event == ('-TABLE-ZUVIS-','+CLICKED+',(-1, 5)):
            paspaudimai_kada_pagauta += 1
            if paspaudimai_kada_pagauta >= 2:
                ikelti_zuvis(window)
                paspaudimai_kada_pagauta = 0
            else:
                sorted_kada_pagauta(window)
        elif event == "Filtruoti":
            if values['-PAIESKA-']:
                filtruoti_paspaudimai += 1
                if filtruoti_paspaudimai >= 2:
                    ikelti_zuvis(window)
                    filtruoti_paspaudimai = 0
                    window['-PAIESKA-'].update('')
                else:
                    filtruoti(window, values)
            else:
                ikelti_zuvis(window)
        if selected_data:
            window['Ištrinti'].update(disabled=False)
            window['Atnaujinti duomenis'].update(disabled=False)
        else:
            window['Ištrinti'].update(disabled=True)
            window['Atnaujinti duomenis'].update(disabled=True)
    window.close()