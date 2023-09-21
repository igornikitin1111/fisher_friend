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

# PySimpleGUI
layout = [
    [sg.TabGroup([
    [sg.Tab('Prideti zuvi', [
    [sg.Text("Svoris:"), sg.InputText(key='-SVORIS-')],
    [sg.Text("Ilgis:"), sg.InputText(key='-ILGIS-')],
    [sg.Text("Pagavimo data:"), sg.InputText(key='-KADA_PAGAUTA-')],
    [sg.Text("Rusis:"), sg.InputText(key='-RUSIS-')],
    [sg.Text("Vietove:"), sg.InputText(key='-VIETOVE-')],
    [sg.Button("Prideti")]]),],
    [sg.Tab('Istrinti zuvi', [
    [sg.Text("Pasirinkite zuvi:"), sg.Listbox(values=[], size=(30, 10), key='-ZUVYS-')],
    [sg.Button("Istrinti")]])],
    [sg.Tab('Perziureti zuvis', [
    [sg.Listbox(values=[], size=(30, 10), key='-ZUVYS-')]])]])]
]

window = sg.Window("Fisher Friend Programa", layout)
window.close()