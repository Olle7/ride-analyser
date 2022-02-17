from scipy.ndimage import gaussian_filter
from datetime import datetime,timedelta
from time import time
import numpy as np
import matplotlib.dates as mdates
import csv
from os import scandir
from os.path import isdir

class Sõit:
    def __init__(self,t_algus, t_lõpp, hind, alguse_aadress="", arvenumber=None, makseviis=None, tellija=None, saaja_aadress=None, juriidilise_keha_registrikood=None, adressaadi_VAT_Number=None, adressaadi_VAT_number=None, juhi_juriidilise_isiku_nimi=None, juhi_juriidilise_isiku_aadress=None, juriidilise_isiku_registrikood=None, ettevõtte_VAT_number=None, hind_ilma_käibemaksuta=None, käibemaks_hinnas=None):
        self.t_algus=t_algus
        self.t_lõpp=t_lõpp
        self.alguse_aadress=alguse_aadress
        self.arvenumber=arvenumber
        self.makseviis=makseviis
        self.tellija=tellija
        self.saaja_aadress=saaja_aadress
        self.juriidilise_keha_registrikood=juriidilise_keha_registrikood
        self.adressaadi_VAT_number=adressaadi_VAT_number
        self.juhi_juriidilise_isiku_nimi=juhi_juriidilise_isiku_nimi
        self.juhi_juriidilise_isiku_aadress=juhi_juriidilise_isiku_aadress
        self.juriidilise_isiku_registrikood=juriidilise_isiku_registrikood
        self.ettevõtte_VAT_number=ettevõtte_VAT_number
        self.hind_ilma_käibemaksuta=hind_ilma_käibemaksuta
        self.käibemaks_hinnas=käibemaks_hinnas
        self.hind=hind
failide_loend_sõitude_sisse_lugemise_ajal=""
def loe_failidest(pathid):
    global sõidud,failide_loend_sõitude_sisse_lugemise_ajal
    failide_loend_sõitude_sisse_lugemise_ajal=pathid
    sõidud=[]
    for path in pathid:
        if isdir(path):
            for file in scandir(path):
                loe_failist(file)
        else:
            loe_failist(path)
    sõidud.sort(key=lambda x:x.t_algus)
def loe_failist(file):
    file=open(file)
    csvreader=csv.reader(file)
    assert next(csvreader)==['Arve number', 'Kuupäev', 'Tellimuse aadress', 'Makseviis', 'Sõidu kuupäev', 'Saaja', 'Saaja aadress', 'Juriidilise keha registrikood', 'Adressaadi VAT Number', 'Juriidilise isiku nimi (juht)', 'Juriidilise isiku aadress (Tänav, maja, postiindeks, riik)', 'Juriidilise isiku registrikood', 'Ettevõtte VAT number', 'Hind (ilma KM)', 'KM', 'Lõpphind']
    for row in csvreader:
        sõit=Sõit(t_algus=datetime.strptime(row[4],"%d.%m.%Y %H:%M"),t_lõpp=datetime.strptime(row[1],"%d.%m.%Y %H:%M")-timedelta(minutes=15),hind=float(row[15]))
        #arve_number=int(row[0])
        #row[13]=float(row[13])#hind käibemaksuta
        #row[14]=float(row[14])#käibemaks
        #row[15]=#hind käibemaksuga
        sõidud.append(sõit)
    #return sõidud
#loe_failidest(["/home/olger/Documents/bolt/kviitungid"])
def esimene_ja_viimane_sõit(sõidud):
    esimene=float("inf")
    viimane=-float("inf")
    for sõit in sõidud:
        if sõit.t_algus.timestamp()<esimene:
            esimene=sõit.t_algus.timestamp()
        if sõit.t_algus.timestamp()>viimane:
            viimane=sõit.t_algus.timestamp()
    return esimene,viimane
def teenitud(t_arr):
    assert type(t_arr)==np.ndarray
    r_per_t_arr=t_arr.copy()
    for i in range(len(t_arr)):
        r=0
        sõite_sel_ajal=0
        for sõit in sõidud:
            if sõit.t_algus.timestamp()<t_arr[i] and t_arr[i]<sõit.t_lõpp.timestamp():
                r+=sõit.hind/(sõit.t_lõpp.timestamp()-sõit.t_algus.timestamp())
                if r!=0:
                    sõite_sel_ajal+=1
                    #print("kahe sõidu ajad kattuvad. t:",t_arr[i],"r:",r)
        r_per_t_arr[i]=r
        #print("t:",t_arr[i],"r:",r,"sõite sel ajal:",sõite_sel_ajal)
    return r_per_t_arr
def kuva_graafikud(originaal, keskmistatud, x0, x1, punkte):
    from matplotlib import pyplot as plt
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    x = np.linspace(x0,x1,punkte)
    dates=[datetime.fromtimestamp(ts) for ts in x]
    algus = time()#ajutine
    plt.plot(dates,originaal(x),color='black',alpha=0.5)
    plt.plot(dates,keskmistatud,color='blue')
    print("aega_võttis:",time()-algus)#ajutine
    #punkte,aega:
    #10000,19.416457653045654
    #10000,19.743277549743652

    plt.gcf().autofmt_xdate()
    myFmt = mdates.DateFormatter("%d.%m.%Y %H:%M")
    plt.gca().xaxis.set_major_formatter(myFmt)
    plt.ylim(bottom=min(keskmistatud),top=max(keskmistatud))
    plt.show()
def arvuta_keskmistatu(punkte,keskmistamise_periood_sekundites,t_esimene,t_viimane):
    xp = np.linspace(t_esimene,t_viimane,punkte)
    argument_sigma=keskmistamise_periood_sekundites*punkte/(t_viimane-t_esimene)
    keskmistatud=gaussian_filter(teenitud(xp),sigma=argument_sigma)
    return keskmistatud
def visualiseeri(keskmistamise_standardhälve):
    t_esimene,t_viimane=esimene_ja_viimane_sõit(sõidud)
    #print("t_esimene:",t_esimene)
    #print("t_viimane:",t_viimane)
    print("keskmistamise_standardhälve:",keskmistamise_standardhälve)
    #keskmistamise_standardhälve=60*60*24
    kuva_graafikud(teenitud,arvuta_keskmistatu(10000,keskmistamise_standardhälve,t_esimene,t_viimane),t_esimene,t_viimane,10000)


import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

root = tk.Tk()
root.title("Tab Widget")
tabControl = ttk.Notebook(root)
def tab_vahetus(x):
    failid=sisendfailide_sisend.get(1.0,tk.END)[:-1]
    if failid=="":
        failid=[]
    else:
        failid=failid.split("\n")
    if failide_loend_sõitude_sisse_lugemise_ajal!=failid:
        #print("vana:",failide_loend_sõitude_sisse_lugemise_ajal)
        #print("uus :",failid)
        loe_failidest(failid)
        sõite_kokku_entry.delete(0, tk.END)
        sõite_kokku_entry.insert(0,str(len(sõidud)))
        for row in tabel.get_children():
            tabel.delete(row)
        for i in range(len(sõidud)):
            tabel.insert(parent='', index='end', iid=i, text='',values=(sõidud[i].t_algus,sõidud[i].t_lõpp,sõidud[i].hind))

        #tabel.config(command=tabel.yview)
        #tabel.config(command=tabel.xview)
tabControl.bind("<<NotebookTabChanged>>", tab_vahetus)


programmi_kirjelduse_tab=ttk.Frame(tabControl)
tabControl.add(programmi_kirjelduse_tab,text='programmist')
ttk.Label(programmi_kirjelduse_tab,text='See programm võimaldab analüüsida Boldi kaudu tehtud sõidujagamise sõite.').grid(row=0)

sisendfailide_tab=ttk.Frame(tabControl)
tabControl.add(sisendfailide_tab,text='vali sisendfailid')
ttk.Label(sisendfailide_tab,text='Selles lahtris olevatest failidest võetakse sisendandmed analüüsimiseks.\nKui Lahtris on kaust, siis kasutatakse sisendiks kõiki selles kasutas olevaid faile.\nKõikide sisendiks antavate failide pathid peavad olema eraldi ridadel.\nSisendik sobivad kviitungifailid, mille saab lehelt https://partners.bolt.eu/rider-invoices').grid(row=1,columnspan=2)
sisendfailide_sisend=tk.Text(sisendfailide_tab)
sisendfailide_sisend.insert(tk.INSERT,"/home/olger/Documents/bolt/kviitungid")
sisendfailide_sisend.grid(row=2,columnspan=2)
def lisa_allikas(küsija):
    #print("alguses:["+sisendfailide_sisend.get(1.0,tk.END)+"]")
    if sisendfailide_sisend.get(1.0,tk.END)=="\n":
        lisada=""
    else:
        lisada="\n"
    k=küsija()
    if type(k)==tuple:
        lisada+="\n".join(k)
    else:
        lisada+=k
    sisendfailide_sisend.insert(tk.INSERT,lisada)
ttk.Button(sisendfailide_tab, text="vali kviitungite faile", command=lambda:lisa_allikas(filedialog.askopenfilenames)).grid(column=0, row=0)
ttk.Button(sisendfailide_tab, text="vali kaust, kust kviitugifaile otsida", command=lambda:lisa_allikas(filedialog.askdirectory)).grid(column=1, row=0)

graafiku_tab = ttk.Frame(tabControl)
tabControl.add(graafiku_tab,text='käibe graafik')

nimekirja_tab = ttk.Frame(tabControl)
tabControl.add(nimekirja_tab, text='sõitude nimekiri')
ttk.Label(nimekirja_tab, text="sõite kokku:").grid(column=0, row=0)
sõite_kokku_entry=ttk.Entry(nimekirja_tab)
sõite_kokku_entry.grid(row=0,column=1)
tabel=ttk.Treeview(nimekirja_tab)
tabel['columns']=("t_algus", "t_lõpp", "hind","sõite sõitjaga", "alguse_aadress", "arvenumber","makseviis","tellija","saaja_aadress","juriidilise_keha_registrikood","adressaadi_VAT_Number","adressaadi_VAT_number","juhi_juriidilise_isiku_nimi","juhi_juriidilise_isiku_aadress","juriidilise_isiku_registrikood","ettevõtte_VAT_number","hind_ilma_käibemaksuta","käibemaks_hinnas")

tabel.column("#0", width=0,  stretch=tk.NO)
#tabel.column("t_algus",anchor=tk.CENTER, width=80)
tabel.column("t_lõpp",anchor=tk.CENTER,width=80)
tabel.column("hind",anchor=tk.CENTER,width=80)

tabel.heading("#0",text="",anchor=tk.CENTER)
tabel.heading("t_algus",text="t_algus",anchor=tk.CENTER)
tabel.heading("t_lõpp",text="t_lõpp",anchor=tk.CENTER)
tabel.heading("hind",text="hind",anchor=tk.CENTER)
tabel.heading("sõite sõitjaga",text="sõite sõitjaga",anchor=tk.CENTER)

tabel.grid(row=2)

tabControl.pack(expand=1, fill="both")

ttk.Label(graafiku_tab, text="üle kui pika ajavahemiku keskmistada:").grid(column=0, row=0)
keskmistamise_stdev=ttk.Entry(graafiku_tab)
keskmistamise_stdev.insert(tk.END,"1")
keskmistamise_stdev.grid(column=1,row=0)
value_inside=tk.StringVar(root)
value_inside.set("ööpäeva")
ttk.OptionMenu(graafiku_tab, value_inside,"ööpäeva", "sekundit", "minutit", "tundi", "ööpäeva").grid(column=2, row=0)
def kuva_graafik():
    stdev=float(keskmistamise_stdev.get())
    print("stdev:",stdev)
    print("value_inside:",value_inside.get())
    if value_inside.get()=="minutit":
        stdev*=60
    elif value_inside.get()=="tundi":
        stdev*=60*60
    elif value_inside.get()=="ööpäeva":
        stdev*=60*60*24
    else:
        assert value_inside.get()=="sekundit"
    visualiseeri(stdev)
ttk.Button(graafiku_tab, text="kuva graafik", command=kuva_graafik).grid(column=0, row=1)

root.mainloop()