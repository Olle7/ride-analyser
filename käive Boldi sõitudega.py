from scipy.ndimage import gaussian_filter
from datetime import datetime,timedelta
from time import time
from scipy import stats
import numpy as np
import matplotlib.dates as mdates
import csv
from os import scandir
from os.path import isdir
from math import pi,e,exp
from matplotlib import pyplot as plt

failide_loend_sõitude_sisse_lugemise_ajal=""
def loe_failidest(pathid):
    global sõidud,sõidud2,failide_loend_sõitude_sisse_lugemise_ajal
    failide_loend_sõitude_sisse_lugemise_ajal=pathid
    sõidud=[]
    sõidud2=[]
    for path in pathid:
        if isdir(path):
            for file in scandir(path):
                loe_failist(file)
                loe_failist2(file)
        else:
            loe_failist(path)
            loe_failist2(file)
    sõidud.sort(key=lambda x:x["t_algus"])
def loe_failist(file):
    file=open(file)
    csvreader=csv.reader(file)
    assert next(csvreader)==['Arve number', 'Kuupäev', 'Tellimuse aadress', 'Makseviis', 'Sõidu kuupäev', 'Saaja', 'Saaja aadress', 'Juriidilise keha registrikood', 'Adressaadi VAT Number', 'Juriidilise isiku nimi (juht)', 'Juriidilise isiku aadress (Tänav, maja, postiindeks, riik)', 'Juriidilise isiku registrikood', 'Ettevõtte VAT number', 'Hind (ilma KM)', 'KM', 'Lõpphind']
    for row in csvreader:
        sõit={"t_algus":datetime.strptime(row[4],"%d.%m.%Y %H:%M"),"t_lõpp":(datetime.strptime(row[1],"%d.%m.%Y %H:%M")-timedelta(minutes=15)),"hind":float(row[15]),"alguse_aadress":row[2],"arvenumber":row[0],"makseviis":row[3],"tellija":row[5],"saaja_aadress":row[6],"juriidilise_keha_registrikood":row[7],"adressaadi_VAT_number":row[8],"juhi_juriidilise_isiku_nimi":row[9],"juhi_juriidilise_isiku_aadress":row[10],"juriidilise_isiku_registrikood":row[11],"ettevõtte_VAT_number":row[12],"hind_ilma_käibemaksuta":row[13],"käibemaks_hinnas":row[14]}
        #arve_number=int(row[0])
        #row[13]=float(row[13])#hind käibemaksuta
        #row[14]=float(row[14])#käibemaks
        #row[15]=#hind käibemaksuga
        sõidud.append(sõit)
    #return sõidud
    #loe_failidest(["/home/olger/Documents/bolt/kviitungid"])
class Sõit:
    def __init__(self,data):
        if "Sõidu kuupäev" in data.keys():
            #"Arve number","Kuupäev","Tellimuse aadress","Makseviis","Sõidu kuupäev","Saaja","Saaja aadress","Juriidilise keha registrikood","Adressaadi VAT Number","Juriidilise isiku nimi (juht)","Juriidilise isiku aadress (Tänav, maja, postiindeks, riik)","Juriidilise isiku registrikood","Ettevõtte VAT number","Hind (ilma KM)","KM","Lõpphind"
            self.kvitungi_faili_data=data
            self.sõidu_faili_data=None
        else:
            #"Tellimuse aeg","Tellimuse aadress","Sõidu hind","Broneeringu tasu","Teemaks","Tühistamise tasu","Jootraha","Valuuta","Maksemeetod","Makse aeg","Distants","Olek"
            self.sõidu_faili_data=data
            self.kvitungi_faili_data=None
    def __str__(self):
        return "sõidu_faili_data="+str(self.sõidu_faili_data)+";kvitungi_faili_data="+str(self.kvitungi_faili_data)
    def hind(self):
        return float(self.kvitungi_faili_data["Lõpphind"])
    def t_sõidu_algus(self):
        return datetime.strptime(self.kvitungi_faili_data["Sõidu kuupäev"],"%d.%m.%Y %H:%M").timestamp()
    def t_tellimine(self):
        return datetime.strptime(self.kvitungi_faili_data["Tellimuse aeg"],"%d.%m.%Y %H:%M").timestamp()
    def t_sõidu_lõpp(self):
        pass
def loe_failist2(file):
    fail=open(file)
    for row in csv.DictReader(fail,skipinitialspace=True):
        sõidud2.append(Sõit({k: v for k, v in row.items()}))
def esimene_ja_viimane_sõit(sõidud):
    esimene=float("inf")
    viimane=-float("inf")
    for sõit in sõidud:
        if sõit["t_algus"].timestamp()<esimene:
            esimene=sõit["t_algus"].timestamp()
        if sõit["t_algus"].timestamp()>viimane:
            viimane=sõit["t_algus"].timestamp()
    return esimene,viimane
def teenitud(t_arr):
    assert type(t_arr)==np.ndarray
    r_per_t_arr=t_arr.copy()
    for i in range(len(t_arr)):
        r=0
        sõite_sel_ajal=0
        for sõit in sõidud:
            if sõit["t_algus"].timestamp()<t_arr[i] and t_arr[i]<sõit["t_lõpp"].timestamp():
                r+=sõit["hind"]/(sõit["t_lõpp"].timestamp()-sõit["t_algus"].timestamp())
                if r!=0:
                    sõite_sel_ajal+=1
                    #print("kahe sõidu ajad kattuvad. t:",t_arr[i],"r:",r)
        r_per_t_arr[i]=r
        #print("t:",t_arr[i],"r:",r,"sõite sel ajal:",sõite_sel_ajal)
    return r_per_t_arr
def kuva_graafikud(originaal, keskmistatud, x0, x1, punkte):
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    x = np.linspace(x0,x1,punkte)
    dates=[datetime.fromtimestamp(ts) for ts in x]
    algus = time()#ajutine
    print("joonistamine algas.")
    plt.plot(dates,originaal(x),color='black',alpha=0.5)
    plt.plot(dates,keskmistatud,color='blue')
    print("joonuistamine aega võttis:",time()-algus)#ajutine
    #punkte,aega:
    #10000,19.416457653045654
    #10000,19.743277549743652

    plt.gcf().autofmt_xdate()
    myFmt = mdates.DateFormatter("%d.%m.%Y %H:%M")
    plt.gca().xaxis.set_major_formatter(myFmt)
    plt.ylim(bottom=min(keskmistatud),top=max(keskmistatud))
    plt.show()
def arvuta_keskmistatu1(punkte, keskmistamise_periood_sekundites, t_esimene, t_viimane):
    t_keskmistamise_algus=time()
    xp=np.linspace(t_esimene,t_viimane,punkte)
    argument_sigma=keskmistamise_periood_sekundites*punkte/(t_viimane-t_esimene)
    keskmistatud=gaussian_filter(teenitud(xp),sigma=argument_sigma)
    print("keskmistamine1 keskmistamine võttis aega:",time()-t_keskmistamise_algus)
    return keskmistatud
def arvuta_keskmistatu3(punkte,keskmistamise_periood_sekundites,t_esimene,t_viimane):
    t_keskmistamise_algus = time()
    väljund=np.zeros(5)
    #gaussian=[]
    #for i in range(-punkte,punkte)
    ajad=np.linspace(t_esimene,t_viimane,punkte)
    for sõit in sõidud:
        n=stats.norm(sõit["t_algus"].timestamp(),keskmistamise_periood_sekundites)
        väljund+=n(ajad)
    print("keskmistamine2 võttis aega:", time() - t_keskmistamise_algus)
    return väljund
def arvuta_keskmistatu2(punkte,keskmistamise_periood_sekundites,t_esimene,t_viimane):
    t_keskmistamise_algus = time()
    väljund=np.ndarray((punkte,))
    s=keskmistamise_periood_sekundites
    dt=(t_viimane-t_esimene)/punkte
    for i in range(punkte):
        t=t_esimene+i*dt
        väljund[i]=0

        väline_jagaja=(2*pi)**(1/2)*s
        e_peal_jagaja=-2*s**2
        for sõit in sõidud:
            if False:
                #print(sõit["t_lõpp"].timestamp()-sõit["t_algus"].timestamp())
                väljund[i]+=(-2*sõit["hind"]/(sõit["t_lõpp"].timestamp()-sõit["t_algus"].timestamp())*e**(-t/(2*s**2))*(e**(sõit["t_algus"].timestamp()/(2*s**2))-e**(sõit["t_lõpp"].timestamp()/(2*s**2)))*s**2)/((2*pi)**(1/2)*s)
            else:
                #print(t-sõit["t_algus"].timestamp())
                väljund[i]+=sõit["hind"]*exp((t-sõit["t_algus"].timestamp())**2/e_peal_jagaja)/väline_jagaja
    print("keskmistamine2 võttis aega:", time() - t_keskmistamise_algus)
    return väljund

def kahe_keskmistamise_graafikud(keskmistatud1, keskmistatud2, x0, x1, punkte):
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    x = np.linspace(x0,x1,punkte)
    dates=[datetime.fromtimestamp(ts) for ts in x]
    algus = time()#ajutine
    print("joonistamine algas.")
    plt.plot(dates,keskmistatud1,color='red')
    plt.plot(dates,keskmistatud2,color='green')
    print("joonistamine aega võttis:",time()-algus)
    plt.gcf().autofmt_xdate()
    myFmt = mdates.DateFormatter("%d.%m.%Y %H:%M")
    plt.gca().xaxis.set_major_formatter(myFmt)
    plt.ylim(bottom=min(keskmistatud1),top=max(keskmistatud1))
    plt.show()

def visualiseeri():
    keskmistamise_standardhälve=float(keskmistamise_stdev.get())*({"sekundit":1, "minutit":60, "tundi":60*60, "ööpäeva":60*60*24}[kesmistamisaja_ühik.get()])
    t_esimene,t_viimane=esimene_ja_viimane_sõit(sõidud)
    kordaja=1
    if boldi_vahendustasu_maha.get():
        kordaja*=0.8
    if tulumaks_maha.get():
        kordaja*=0.8
    if kütusehind_maha.get():
        kordaja*=1-0.14
    liitja=-float(konstantne_kulu.get())/({"sekundis":1, "minutis":60, "tunnis":60*60, "ööpäevas":60*60*24,"nädalas":60*60*24*7}[konstantse_kulu_ühik.get()])
    ühiku_kordaja={"rahaühikut/sekundis":1,"rahaühikut/minutis":1/60,"rahaühikut/tunnis":1/(60*60),"rahaühikut/ööpäevas":1/(60*60*24)}[käibe_ühik.get()]
    # print("t_esimene:",t_esimene)
    # print("t_viimane:",t_viimane)
    # print("keskmistamise_standardhälve:",keskmistamise_standardhälve)
    punkte=10000
    #print(arvuta_keskmistatu2(punkte,keskmistamise_standardhälve,t_esimene,t_viimane))
    kuva_graafikud(lambda x:(teenitud(x)*kordaja+liitja)*ühiku_kordaja,(arvuta_keskmistatu2(punkte,keskmistamise_standardhälve,t_esimene,t_viimane)*kordaja+liitja)*ühiku_kordaja,t_esimene,t_viimane,punkte)
    #kahe_keskmistamise_graafikud((arvuta_keskmistatu1(punkte,keskmistamise_standardhälve,t_esimene,t_viimane)*kordaja+liitja)*ühiku_kordaja,(arvuta_keskmistatu2(punkte,keskmistamise_standardhälve,t_esimene,t_viimane)*kordaja+liitja)*ühiku_kordaja,t_esimene,t_viimane,punkte)


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
        uuenda_tabeli_sisu()
def uuenda_tabeli_sisu():
    for row in tabel.get_children():
        tabel.delete(row)
    global sõite_sõitjatega
    sõite_sõitjatega={}
    for sõit in sõidud:
        if sõit["tellija"] in sõite_sõitjatega:
            sõite_sõitjatega[sõit["tellija"]]+=1
        else:
            sõite_sõitjatega[sõit["tellija"]]=1
    for i in range(len(sõidud)):
        tabel.insert(parent='', index='end', iid=i, text='',values=(sõidud[i]["t_algus"],sõidud[i]["alguse_aadress"],sõidud[i]["t_lõpp"],sõidud[i]["hind"],sõidud[i]["tellija"],sõite_sõitjatega[sõidud[i]["tellija"]],sõidud[i]["arvenumber"],sõidud[i]["makseviis"],sõidud[i]["saaja_aadress"],sõidud[i]["juriidilise_keha_registrikood"],sõidud[i]["adressaadi_VAT_number"],sõidud[i]["juhi_juriidilise_isiku_nimi"],sõidud[i]["juhi_juriidilise_isiku_aadress"],sõidud[i]["juriidilise_isiku_registrikood"],sõidud[i]["ettevõtte_VAT_number"],sõidud[i]["hind_ilma_käibemaksuta"],sõidud[i]["käibemaks_hinnas"]))

    laiused={}
    #for kv in tabel.get_children()[0].items():
    #    laiused[kv[0]]=0
    laiused=[0]*len(kolumnid)
    for line in tabel.get_children():
        for i in range(len(tabel.item(line)['values'])):
            if laiused[i]<len(str(tabel.item(line)['values'][i])):
                laiused[i]=len(str(tabel.item(line)['values'][i]))
    for i in range(len(kolumnid)):
        tabel.column(kolumnid[i],width=laiused[i]*12)
    tabel.column("t_algus",width=123)
    tabel.column("t_lõpp", width=123)
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
ttk.Label(graafiku_tab, text="üle kui pika ajavahemiku keskmistada:").grid(column=0, row=0)
keskmistamise_stdev=ttk.Entry(graafiku_tab)
keskmistamise_stdev.insert(tk.END,"1")
keskmistamise_stdev.grid(column=1,row=0)
kesmistamisaja_ühik=tk.StringVar(root)
#value_inside.set("ööpäeva")
ttk.OptionMenu(graafiku_tab, kesmistamisaja_ühik, "ööpäeva", "sekundit", "minutit", "tundi", "ööpäeva").grid(column=2, row=0)
ttk.Label(graafiku_tab, text="arvuta maha boldi vahendustasu 20%:").grid(column=0, row=1)
boldi_vahendustasu_maha=tk.IntVar()
boldi_vahendustasu_maha.set(1)
ttk.Checkbutton(graafiku_tab,variable=boldi_vahendustasu_maha, onvalue=1,offvalue=0).grid(column=1,row=1)
ttk.Label(graafiku_tab, text="arvuta maha tulumaks 20%:").grid(column=0, row=2)
tulumaks_maha=tk.IntVar()
tulumaks_maha.set(1)
ttk.Checkbutton(graafiku_tab,variable=tulumaks_maha,onvalue=1,offvalue=0).grid(column=1,row=2)
ttk.Label(graafiku_tab, text="kütusehind 14%:").grid(column=0, row=3)
kütusehind_maha=tk.IntVar()
kütusehind_maha.set(1)
ttk.Checkbutton(graafiku_tab,variable=kütusehind_maha,onvalue=1,offvalue=0).grid(column=1,row=3)

ttk.Label(graafiku_tab, text="konstantne kulu maha:").grid(column=0, row=4)
konstantne_kulu=ttk.Entry(graafiku_tab)
konstantne_kulu.insert(tk.END,"125")
konstantne_kulu.grid(column=1,row=4)
ttk.Label(graafiku_tab, text="eurot/").grid(column=2, row=4)
konstantse_kulu_ühik=tk.StringVar(root)
ttk.OptionMenu(graafiku_tab,konstantse_kulu_ühik,"nädalas","nädalas","ööpäevas", "sekundis", "minutis", "tunnis").grid(column=3, row=4)

ttk.Label(graafiku_tab, text="Mis ühikutes käivet kuvada:").grid(column=0, row=5)
käibe_ühik=tk.StringVar(root)
#value_inside.set("rahaühikut/tunnis")
ttk.OptionMenu(graafiku_tab,käibe_ühik,"rahaühikut/tunnis","rahaühikut/sekundis","rahaühikut/minutis","rahaühikut/tunnis","rahaühikut/ööpäevas").grid(column=1,row=5)

ttk.Button(graafiku_tab,text="kuva graafik",command=visualiseeri).grid(column=0,row=6)

nimekirja_tab = ttk.Frame(tabControl)
tabControl.add(nimekirja_tab, text='sõitude nimekiri')
ttk.Label(nimekirja_tab, text="sõite kokku:").grid(column=0, row=1)
sõite_kokku_entry=ttk.Entry(nimekirja_tab,state=tk.DISABLED)
sõite_kokku_entry.grid(row=1,column=1)
kolumnid=("t_algus","alguse_aadress","t_lõpp","hind","tellija","sõite tellijaga","arvenumber","makseviis","saaja_aadress","juriidilise_keha_registrikood","adressaadi_VAT_number","juhi_juriidilise_isiku_nimi","juhi_juriidilise_isiku_aadress","juriidilise_isiku_registrikood","ettevõtte_VAT_number","hind_ilma_käibemaksuta","käibemaks_hinnas")
tabel=ttk.Treeview(nimekirja_tab,columns=kolumnid,show="headings")
# scrollbars
#vsb = ttk.Scrollbar(nimekirja_tab, orient="vertical", command=tabel.yview)
#vsb.place(relx=0.978, rely=0.175, relheight=0.713, relwidth=0.020)
#hsb = ttk.Scrollbar(nimekirja_tab, orient="horizontal", command=tabel.xview)
#hsb.place(relx=0.014, rely=0.875, relheight=0.020, relwidth=0.965)
#tabel.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

lahter_mille_järgi_viimati_sorditi=False
def treeview_sort_column(tabel, col, reverse):
    global lahter_mille_järgi_viimati_sorditi
    reverse=lahter_mille_järgi_viimati_sorditi==col
    lahter_mille_järgi_viimati_sorditi=col
    if col=="sõite tellijaga":
        sõidud.sort(key=lambda x: sõite_sõitjatega[x["tellija"]],reverse=reverse)
    else:
        sõidud.sort(key=lambda x:x[col],reverse=reverse)
    uuenda_tabeli_sisu()
for col in kolumnid:
    tabel.column(col,anchor=tk.CENTER, stretch=tk.NO)
    tabel.heading(col, text=col, command=lambda _col=col: treeview_sort_column(tabel, _col, False))

#tabel.column("#0", width=0,  stretch=tk.NO)
#tabel.column("t_algus",anchor=tk.CENTER, width=80)
#tabel.column("t_lõpp",anchor=tk.CENTER,width=80)
#tabel.column("hind",anchor=tk.CENTER,width=80)

#tabel.heading("#0",text="",anchor=tk.CENTER)
#tabel.heading("t_algus",text="t_algus",anchor=tk.CENTER)
#tabel.heading("t_lõpp",text="t_lõpp",anchor=tk.CENTER)
#tabel.heading("hind",text="hind",anchor=tk.CENTER)
#tabel.heading("sõite sõitjaga",text="sõite sõitjaga",anchor=tk.CENTER)

tabel.grid(row=0)

tabControl.pack(expand=1,fill="both")




root.mainloop()