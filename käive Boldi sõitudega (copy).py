from io import StringIO
from datetime import datetime,timedelta
from time import time
from numpy import zeros,linspace
from matplotlib.dates import DateFormatter
from csv import DictReader,QUOTE_ALL
from os import scandir
from os.path import isdir
#from math import pi,e,exp,erf
from matplotlib import pyplot as plt
from scipy import special
from sys import argv
t_esimene=None#
t_viimane=None
default_values=["/home/olger/Documents/bolt/kviitungid\n/home/olger/Documents/bolt/sõidud","1","ööpäeva","1","1","1","125","rahaühikut/nädalas","rahaühikut/ööpäevas","50000","12000"]
for i in range(len(argv)-1):
    default_values[i]=argv[i+1]#

ühiku_kordaja={"rahaühikut/sekundis":1,"rahaühikut/minutis":60,"rahaühikut/tunnis":60*60,"rahaühikut/ööpäevas":60*60*24,"rahaühikut/nädalas":60*60*24*7}
failide_loend_sõitude_sisse_lugemise_ajal=""
def loe_failidest(pathid):
    global sõidud2,failide_loend_sõitude_sisse_lugemise_ajal,kviitungi_faili_kirjed,sõidu_faili_kirjed
    failide_loend_sõitude_sisse_lugemise_ajal=pathid
    sõidud2=[]
    kviitungi_faili_kirjed=[]
    sõidu_faili_kirjed=[]
    for path in pathid:
        if isdir(path):
            for file in scandir(path):
                loe_failist2(file)
        else:
            loe_failist2(path)

def ühenda_sõidufaili_ja_kviitungifaili_kirjed():
    algus=time()
    i1=0
    kviitungi_faili_kirjed.sort(key=lambda x:x.t_sõidu_algus())
    sõidu_faili_kirjed.sort(key=lambda x:x.t_tellimine())
    i0=0
    hinnad_sõidufailis=[]
    for sõit in sõidu_faili_kirjed:
        hinnad_sõidufailis.append(float(sõit.sõidu_faili_data["Sõidu hind"]))
    while i1<len(kviitungi_faili_kirjed):
        vasted=[]
        i2=i0
        while i2<len(sõidu_faili_kirjed):
            if hinnad_sõidufailis[i2]==float(kviitungi_faili_kirjed[i1].kviitungi_faili_data["Lõpphind"]) and sõidu_faili_kirjed[i2].t_tellimine()<=kviitungi_faili_kirjed[i1].t_sõidu_algus()<=sõidu_faili_kirjed[i2].t_sõidu_lõpp()<=kviitungi_faili_kirjed[i1].t_kviitung() and not (kviitungi_faili_kirjed[i1].kviitungi_faili_data["Makseviis"]=="Bolt makse" and sõidu_faili_kirjed[i2].sõidu_faili_data["Maksemeetod"]!="app_payment" or kviitungi_faili_kirjed[i1].kviitungi_faili_data["Makseviis"]!="Sularaha" and sõidu_faili_kirjed[i2].sõidu_faili_data["Maksemeetod"]=="cash"):
                #print("klapivad:",kviitungi_faili_kirjed[i1],"ja",sõidu_faili_kirjed[i2])
                vasted.append(sõidu_faili_kirjed.pop(i2))
                hinnad_sõidufailis.pop(i2)
                i0=i2
            else:
                i2+=1
        if len(vasted)==1:
            sõidud2.append(Sõit(kviitungi_faili_data=kviitungi_faili_kirjed.pop(i1).kviitungi_faili_data,sõidu_faili_data=vasted[0].sõidu_faili_data))
        elif len(vasted)>1:
            print("kviitungikirjele",kviitungi_faili_kirjed[i1],"vastavad sõidufailid kirjed:",vasted)
            raise Exception("Mitme sõitja sõidud. Ei saa sõidufaili ja kviitungifaili datat normilt ühendada.")
        else:
            i1+=1
    print("Ühendamieks aega kulus:",time()-algus)


class Sõit:
    def __init__(self,kviitungi_faili_data=None,sõidu_faili_data=None):
        self.kviitungi_faili_data=kviitungi_faili_data
        self.sõidu_faili_data=sõidu_faili_data
    def __str__(self):
        return "sõidu_faili_data="+str(self.sõidu_faili_data)+";kviitungi_faili_data="+str(self.kviitungi_faili_data)
    def __repr__(self):
        return str(self)
    def hind(self):
        if self.kviitungi_faili_data:
            return float(self.kviitungi_faili_data["Lõpphind"])
        else:
            return float(self.sõidu_faili_data["Sõidu hind"])
    def t_sõidu_algus(self,hinnanguline=False):
        if self.kviitungi_faili_data!=None or not hinnanguline:
            return datetime.strptime(self.kviitungi_faili_data["Sõidu kuupäev"],"%d.%m.%Y %H:%M").timestamp()
        else:
            return (self.t_tellimine()+self.t_sõidu_lõpp())/2
    def t_tellimine(self):
        return datetime.strptime(self.sõidu_faili_data["Tellimuse aeg"],"%d.%m.%Y %H:%M").timestamp()
    def t_sõidu_lõpp(self,hinnanguline=False):
        if self.sõidu_faili_data!=None or not hinnanguline:
            return datetime.strptime(self.sõidu_faili_data["Makse aeg"],"%d.%m.%Y %H:%M").timestamp()
        else:
            return (datetime.strptime(self.kviitungi_faili_data["Kuupäev"],"%d.%m.%Y %H:%M")-timedelta(minutes=15)).timestamp()
    def t_kviitung(self):
        return datetime.strptime(self.kviitungi_faili_data["Kuupäev"],"%d.%m.%Y %H:%M").timestamp()
    def tellimuse_aadress(self):
        if self.sõidu_faili_data!=None and self.kviitungi_faili_data!=None and "Tellimuse aadress" in self.kviitungi_faili_data and "Tellimuse aadress" in self.sõidu_faili_data:
            return self.sõidu_faili_data["Tellimuse aadress"]+" ehk ligikaudu "+self.kviitungi_faili_data["Tellimuse aadress"]
        elif self.kviitungi_faili_data!=None and "Tellimuse aadress" in self.kviitungi_faili_data:
            return "ligikaudu"+self.kviitungi_faili_data["Tellimuse aadress"]
        elif self.sõidufaili_data!=None and "Tellimuse aadress" in self.sõidu_faili_data:
            return self.sõidu_faili_data["Tellimuse  aadress"]
def loe_failist2(file):
    fail=open(file)
    csv_fail=StringIO(fail.read().strip("\ufeff"))
    fail.close()
    for row in DictReader(csv_fail,quoting=QUOTE_ALL,skipinitialspace=True):
        data={k: v for k, v in row.items()}
        if "Sõidu kuupäev" in data.keys():#"Arve number","Kuupäev","Tellimuse aadress","Makseviis","Sõidu kuupäev","Saaja","Saaja aadress","Juriidilise keha registrikood","Adressaadi VAT Number","Juriidilise isiku nimi (juht)","Juriidilise isiku aadress (Tänav, maja, postiindeks, riik)","Juriidilise isiku registrikood","Ettevõtte VAT number","Hind (ilma KM)","KM","Lõpphind"
            kviitungi_faili_kirjed.append(Sõit(kviitungi_faili_data=data))
        else:##"Tellimuse aeg","Tellimuse aadress","Sõidu hind","Broneeringu tasu","Teemaks","Tühistamise tasu","Jootraha","Valuuta","Maksemeetod","Makse aeg","Distants","Olek"
            sõidu_faili_kirjed.append(Sõit(sõidu_faili_data=data))
def esimene_ja_viimane_sõit():
    esimene=float("inf")
    viimane=-float("inf")
    for sõit in sõidud2:
        if sõit.t_sõidu_algus(hinnanguline=True)<esimene:
            esimene=sõit.t_sõidu_algus(hinnanguline=True)
        if sõit.t_sõidu_algus(hinnanguline=True)>viimane:
            viimane=sõit.t_sõidu_algus(hinnanguline=True)
    return esimene,viimane
def teenitud2(punkte, t_esimene, t_viimane):
    algus=time()
    väljund=zeros(punkte)
    for i_sõit in range(len(sõidud2)):
        for i in range(min(punkte-1,int(((alguse_ajad[i_sõit]-t_esimene)*punkte)//(t_viimane-t_esimene))),min(punkte-1,int(((lõpu_ajad[i_sõit]-t_esimene)*punkte)//(t_viimane-t_esimene)))):
            väljund[i]+=raha_aja_kohta[i_sõit]
    print("keskmistamta graafiku koostamine võttis aega:",time()-algus)
    return väljund

def kuva_graafikud(originaal, keskmistatud, x0, x1,y_ühik):
    algus = time()
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    plt.plot([datetime.fromtimestamp(ts) for ts in linspace(x0,x1,len(originaal))],originaal,color='black',alpha=0.5)
    plt.plot([datetime.fromtimestamp(ts) for ts in linspace(x0,x1,len(keskmistatud))],keskmistatud,color='blue')
    #punkte,aega:
    #10000,19.416457653045654
    #10000,19.743277549743652

    plt.gcf().autofmt_xdate()
    myFmt = DateFormatter("%d.%m.%Y %H:%M")
    plt.gca().xaxis.set_major_formatter(myFmt)
    plt.ylim(bottom=min(keskmistatud),top=max(keskmistatud))
    plt.ylabel(y_ühik)
    plt.title("Raha Bolt sõitudega")
    print("joonistamine aega võttis:", time() - algus)
    plt.show()
def arvuta_keskmistatu2(punkte, keskmistamise_periood_sekundites, t_esimene, t_viimane):
    t_keskmistamise_algus=time()
    väljund=zeros(punkte)
    s_sqrt2=keskmistamise_periood_sekundites*2**0.5
    t_esimene/=s_sqrt2
    t_viimane/=s_sqrt2
    #väline_jagaja=(2*pi)**(1/2)*s_sqrt2
    #e_peal_jagaja=-2*s_sqrt2**2
    for i_sõit in range(len(sõidud2)):
        if raha_aja_kohta[i_sõit]!=0:
            alguse_aeg=alguse_ajad[i_sõit]/s_sqrt2
            lõpu_aeg=lõpu_ajad[i_sõit]/s_sqrt2
            väljund+=(special.erf(linspace(t_esimene-alguse_aeg,t_viimane-alguse_aeg,punkte))-special.erf(linspace(t_esimene-lõpu_aeg,t_viimane-lõpu_aeg,punkte)))*(raha_aja_kohta[i_sõit]/2)
    print("keskmistamine2 võttis aega:",time()-t_keskmistamise_algus)
    return väljund

def kahe_keskmistamise_graafikud(keskmistatud1, keskmistatud2, x0, x1, punkte):
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    x = linspace(x0,x1,punkte)
    dates=[datetime.fromtimestamp(ts) for ts in x]
    algus = time()#ajutine
    print("joonistamine algas.")
    plt.plot(dates,keskmistatud1,color='red')
    plt.plot(dates,keskmistatud2,color='green')
    print("joonistamine aega võttis:",time()-algus)
    plt.gcf().autofmt_xdate()
    myFmt = DateFormatter("%d.%m.%Y %H:%M")
    plt.gca().xaxis.set_major_formatter(myFmt)
    plt.ylim(bottom=min(keskmistatud1),top=max(keskmistatud1))
    plt.show()

def visualiseeri():
    keskmistamise_standardhälve=float(keskmistamise_stdev.get())*({"sekundit":1, "minutit":60, "tundi":60*60, "ööpäeva":60*60*24}[kesmistamisaja_ühik.get()])
    t_esimene,t_viimane=esimene_ja_viimane_sõit()
    kordaja=1
    if boldi_vahendustasu_maha.get():
        kordaja*=0.8
    if tulumaks_maha.get():
        kordaja*=0.8
    if kütusehind_maha.get():
        kordaja*=1-0.14

    liitja=-float(konstantne_kulu.get())/(ühiku_kordaja[konstantse_kulu_ühik.get()])
    graafikul_ühiku_kordaja=ühiku_kordaja[käibe_ühik.get()]
    #punkte=10000
    #print(arvuta_keskmistatu2(punkte,keskmistamise_standardhälve,t_esimene,t_viimane))
    
    kuva_graafikud((teenitud2(int(punkte_keskmistamata_graafikul.get()), t_esimene, t_viimane) * kordaja + liitja) * graafikul_ühiku_kordaja, (arvuta_keskmistatu2(int(punkte_keskmistatud_graafikul.get()), keskmistamise_standardhälve, t_esimene, t_viimane) * kordaja + liitja) * graafikul_ühiku_kordaja, t_esimene, t_viimane,käibe_ühik.get())
    #kahe_keskmistamise_graafikud((arvuta_keskmistatu1(punkte,keskmistamise_standardhälve,t_esimene,t_viimane)*kordaja+liitja)*graafikul_ühiku_kordaja,(arvuta_keskmistatu2(punkte,keskmistamise_standardhälve,t_esimene,t_viimane)*kordaja+liitja)*graafikul_ühiku_kordaja,t_esimene,t_viimane,punkte)

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

root = tk.Tk()
root.title("Tab Widget")
tabControl = ttk.Notebook(root)
def failide_loend():
    failid = sisendfailide_sisend.get(1.0, tk.END)[:-1]
    if failid == "":
        return []
    else:
        return failid.split("\n")
def tab_vahetus(x):
    failid=failide_loend()
    if failide_loend_sõitude_sisse_lugemise_ajal!=failid:
        loe_data(failid)
def loe_data(failid):
    # print("vana:",failide_loend_sõitude_sisse_lugemise_ajal)
    # print("uus :",failid)
    loe_failidest(failid)
    print(len(kviitungi_faili_kirjed), len(sõidu_faili_kirjed), len(sõidud2))
    ühenda_sõidufaili_ja_kviitungifaili_kirjed()
    print(len(kviitungi_faili_kirjed), len(sõidu_faili_kirjed), len(sõidud2))
    print(kviitungi_faili_kirjed)
    sõidud2.sort(key=lambda x: x.t_sõidu_algus(hinnanguline=True))
    sõite_kokku.config(text="sõite kokku: " + str(len(sõidud2)))
    global alguse_ajad,lõpu_ajad,raha_aja_kohta,t_esimene, t_viimane
    t_esimene, t_viimane = esimene_ja_viimane_sõit()
    alguse_ajad=[]
    lõpu_ajad=[]
    raha_aja_kohta=[]
    for sõit in sõidud2:
        alguse_ajad.append(sõit.t_sõidu_algus(hinnanguline=True))
        lõpu_ajad.append(sõit.t_sõidu_lõpp(hinnanguline=True))
        raha_aja_kohta.append(sõit.hind()/(lõpu_ajad[-1]-alguse_ajad[-1]))
    uuenda_tiheduse_label(keskmistamata_tiheduse_label,punkte_keskmistamata_graafikul)
    uuenda_tiheduse_label(keskmistatud_tiheduse_label,punkte_keskmistatud_graafikul)
    uuenda_tabeli_sisu()
def uuenda_tabeli_sisu():
    global võtmed_datast
    for row_data_osa in tabel.get_children():
        tabel.delete(row_data_osa)
    for col in tabel['columns']:
        tabel.heading(col, text='')
    global sõite_sõitjatega
    sõite_sõitjatega={}
    for sõit in sõidud2:
        if sõit.kviitungi_faili_data!=None and "Saaja" in sõit.kviitungi_faili_data:
            if sõit.kviitungi_faili_data["Saaja"] in sõite_sõitjatega:
                sõite_sõitjatega[sõit.kviitungi_faili_data["Saaja"]]+=1
            else:
                sõite_sõitjatega[sõit.kviitungi_faili_data["Saaja"]]=1


    kviitungifaili_võtmed=set()
    sõidufaili_võtmed=set()
    for sõit in sõidud2:
        if sõit.kviitungi_faili_data:
            for võti in sõit.kviitungi_faili_data.keys():
                kviitungifaili_võtmed.add((võti,"kviitungifailist"))
        if sõit.sõidu_faili_data:
            for võti in sõit.sõidu_faili_data.keys():
                sõidufaili_võtmed.add((võti,"sõidufailist"))
    võtmed_datast=sorted(kviitungifaili_võtmed)+sorted(sõidufaili_võtmed)
    arvutatud_võtmed={"t_algus":lambda x: x.t_sõidu_algus(hinnanguline=True),"alguse_aadress":lambda x: x.tellimuse_aadress(),"t_lõpp":lambda x: x.t_sõidu_lõpp(hinnanguline=True),"hind":lambda x:x.hind(),"tellija":lambda x:x.kviitungi_faili_data["Saaja"],"sõite tellijaga":lambda x:sõite_sõitjatega[x.kviitungi_faili_data["Saaja"]]}
    tabel['columns']=list(arvutatud_võtmed.keys())+võtmed_datast
    for võti in arvutatud_võtmed.keys():
        tabel.column(võti, anchor=tk.CENTER, stretch=tk.NO,width=59)
        tabel.heading(võti,text=võti, command=lambda _col=võti: treeview_sort_column(tabel, _col, False,arvutatud_võtmed))
    for võti in võtmed_datast:
        tabel.column(võti, anchor=tk.CENTER, stretch=tk.NO,width=59)
        tabel.heading(võti,text=võti[0]+" : "+võti[1], command=lambda _col=võti: treeview_sort_column(tabel, _col, False,arvutatud_võtmed))
        #tabel.heading(võti, text=võti, command=lambda _col=võti: treeview_sort_column(tabel, _col, False))

    for i_sõit in range(len(sõidud2)):
        row_arvutatud_osa=[""]*len(arvutatud_võtmed.keys())
        try:
            row_arvutatud_osa[0]=datetime.strptime(sõidud2[i_sõit].kviitungi_faili_data["Sõidu kuupäev"],"%d.%m.%Y %H:%M").strftime("%Y.%m.%d. %H.%M.%S")
        except:
            pass
        try:
            row_arvutatud_osa[1]=sõidud2[i_sõit].tellimuse_aadress()
        except Exception as e:
            print(e)
        try:
            row_arvutatud_osa[2]=datetime.strptime(sõidud2[i_sõit].sõidu_faili_data["Makse aeg"],"%d.%m.%Y %H:%M").strftime("%Y.%m.%d. %H.%M.%S")
        except Exception as e:
            print(e)
        try:
            row_arvutatud_osa[3]=sõidud2[i_sõit].hind()
        except:
            pass
        try:
            row_arvutatud_osa[4]=sõidud2[i_sõit].kviitungi_faili_data["Saaja"]
        except:
            pass
        try:
            row_arvutatud_osa[5]=sõite_sõitjatega[sõidud2[i_sõit].kviitungi_faili_data["Saaja"]]
        except Exception as e:
            print(e)
        row_data_osa=[""]*len(võtmed_datast)
        if sõidud2[i_sõit].kviitungi_faili_data!=None:
            for võti_väärtus in sõidud2[i_sõit].kviitungi_faili_data.items():
                row_data_osa[võtmed_datast.index((võti_väärtus[0],"kviitungifailist"))]=võti_väärtus[1]
        if sõidud2[i_sõit].sõidu_faili_data!=None:
            for võti_väärtus in sõidud2[i_sõit].sõidu_faili_data.items():
                row_data_osa[võtmed_datast.index((võti_väärtus[0],"sõidufailist"))]=võti_väärtus[1]
        tabel.insert(parent='', index='end', iid=i_sõit, text='',values=row_arvutatud_osa+row_data_osa)
#    for i in range(len(sõidud)):
#        tabel.insert(parent='', index='end', iid=i, text='',values=(sõidud[i]["t_algus"],sõidud[i]["alguse_aadress"],sõidud[i]["t_lõpp"],sõidud[i]["hind"],sõidud[i]["tellija"],sõite_sõitjatega[sõidud[i]["tellija"]],sõidud[i]["arvenumber"],sõidud[i]["makseviis"],sõidud[i]["saaja_aadress"],sõidud[i]["juriidilise_keha_registrikood"],sõidud[i]["adressaadi_VAT_number"],sõidud[i]["juhi_juriidilise_isiku_nimi"],sõidud[i]["juhi_juriidilise_isiku_aadress"],sõidud[i]["juriidilise_isiku_registrikood"],sõidud[i]["ettevõtte_VAT_number"],sõidud[i]["hind_ilma_käibemaksuta"],sõidud[i]["käibemaks_hinnas"]))

    #laiused = [0] * len(võtmed)
    #for line in tabel.get_children():
    #    for i in range(len(tabel.item(line)['values'])):
    #        if laiused[i] < len(str(tabel.item(line)['values'][i])):
    #            laiused[i] = len(str(tabel.item(line)['values'][i]))
    #for i in range(len(võtmed)):
    #    print(võtmed[i], ":", int(laiused[i] * tabControl.winfo_width() / sum(laiused)))
    #    tabel.column(võtmed[i], width=int(laiused[i] * nimekirja_tab.winfo_width() / sum(laiused)))

    
        #tabel.column(võtmed[i], width=50)
    #tabel.column("t_algus",width=123)
    #tabel.column("t_lõpp", width=123)
tabControl.bind("<<NotebookTabChanged>>", tab_vahetus)
#def muuda_tabeli_laiust(x):
#    print("x:",x)
#root.bind("<Configure>",muuda_tabeli_laiust)

programmi_kirjelduse_tab=ttk.Frame(tabControl)
tabControl.add(programmi_kirjelduse_tab,text='programmist')
ttk.Label(programmi_kirjelduse_tab,text='See programm võimaldab analüüsida Boldi kaudu tehtud sõidujagamise sõite.').grid(row=0)

sisendfailide_tab=ttk.Frame(tabControl)
tabControl.add(sisendfailide_tab,text='vali sisendfailid')
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
ttk.Label(sisendfailide_tab,text='Selles lahtris olevatest failidest võetakse sisendandmed analüüsimiseks.\nKui Lahtris on kaust, siis kasutatakse sisendiks kõiki selles kasutas olevaid faile.\nKõikide sisendiks antavate failide pathid peavad olema eraldi ridadel.\nSisendik sobivad kviitungifailid, mille saab lehtedelt https://partners.bolt.eu/rider-invoices ja https://partners.bolt.eu/orders .\nJuhul kui sisendiks antakse nii kviitungi-faile kui sõidu-faile, samadest sõitudest, siis see programm ei loe neid 2 kordselt vaid saab aru, et sama sõidu kohta on mitu kirjet.').grid(row=1,columnspan=2)
sisendfailide_sisend=tk.Text(sisendfailide_tab)
sisendfailide_sisend.insert(tk.INSERT,default_values[0])
sisendfailide_sisend.grid(row=2,columnspan=2)
ttk.Button(sisendfailide_tab, text="laadi data uuesti failist.", command=lambda:loe_data(failide_loend())).grid(column=0, row=3)

graafiku_tab = ttk.Frame(tabControl)
tabControl.add(graafiku_tab,text='käibe graafik')
ttk.Label(graafiku_tab, text="üle kui pika ajavahemiku keskmistada:").grid(column=0, row=0)
keskmistamise_stdev=ttk.Entry(graafiku_tab)
keskmistamise_stdev.insert(tk.END,default_values[1])
keskmistamise_stdev.grid(column=1,row=0)
kesmistamisaja_ühik=tk.StringVar(root)
#value_inside.set("ööpäeva")
ttk.OptionMenu(graafiku_tab, kesmistamisaja_ühik,default_values[2], "sekundit", "minutit", "tundi", "ööpäeva").grid(column=2, row=0)
ttk.Label(graafiku_tab, text="arvuta maha boldi vahendustasu 20%:").grid(column=0, row=1)
boldi_vahendustasu_maha=tk.IntVar()
boldi_vahendustasu_maha.set(int(default_values[3]))
ttk.Checkbutton(graafiku_tab,variable=boldi_vahendustasu_maha, onvalue=1,offvalue=0).grid(column=1,row=1)
ttk.Label(graafiku_tab, text="arvuta maha tulumaks 20%:").grid(column=0, row=2)
tulumaks_maha=tk.IntVar()
tulumaks_maha.set(int(default_values[4]))
ttk.Checkbutton(graafiku_tab,variable=tulumaks_maha,onvalue=1,offvalue=0).grid(column=1,row=2)
ttk.Label(graafiku_tab, text="kütusehind 14%:").grid(column=0, row=3)
kütusehind_maha=tk.IntVar()
kütusehind_maha.set(int(default_values[5]))
ttk.Checkbutton(graafiku_tab,variable=kütusehind_maha,onvalue=1,offvalue=0).grid(column=1,row=3)

ttk.Label(graafiku_tab, text="konstantne kulu maha:").grid(column=0, row=4)
konstantne_kulu=ttk.Entry(graafiku_tab)
konstantne_kulu.insert(tk.END,default_values[6])
konstantne_kulu.grid(column=1,row=4)
konstantse_kulu_ühik=tk.StringVar(root)
ttk.OptionMenu(graafiku_tab,konstantse_kulu_ühik,default_values[7],*ühiku_kordaja.keys()).grid(column=2, row=4)

ttk.Label(graafiku_tab, text="Mis ühikutes käivet kuvada:").grid(column=0, row=5)
käibe_ühik=tk.StringVar(root)
#value_inside.set("rahaühikut/tunnis")
ttk.OptionMenu(graafiku_tab,käibe_ühik,default_values[8],*ühiku_kordaja.keys()).grid(column=1,row=5)

def uuenda_tiheduse_label(label, punkte):
    try:
        label.config(text=str((t_viimane-t_esimene)/int(punkte.get()))+"*sek")
    except:
        label.config(text="")
    return True

ttk.Label(graafiku_tab, text="Mitu punkti originaal andmetega graafikule kanda (graafika kvaliteet):").grid(column=0, row=6)
keskmistamata_tiheduse_label=ttk.Label(graafiku_tab, text="(punkt iga ... tagant)")
punkte_keskmistamata_graafikul=ttk.Entry(graafiku_tab)
punkte_keskmistamata_graafikul.config(validatecommand=lambda :uuenda_tiheduse_label(keskmistamata_tiheduse_label,punkte_keskmistamata_graafikul), validate="all")
punkte_keskmistamata_graafikul.insert(tk.END, default_values[9])
punkte_keskmistamata_graafikul.grid(column=1, row=6)
keskmistamata_tiheduse_label.grid(column=2, row=6)

ttk.Label(graafiku_tab, text="Mitu punkti keskmistatud graafikule kanda (graafika kvaliteet):").grid(column=0, row=7)
keskmistatud_tiheduse_label=ttk.Label(graafiku_tab, text="(punkt iga ... tagant)")
punkte_keskmistatud_graafikul=ttk.Entry(graafiku_tab)
punkte_keskmistatud_graafikul.config(validatecommand=lambda :uuenda_tiheduse_label(keskmistatud_tiheduse_label,punkte_keskmistatud_graafikul), validate="all")
punkte_keskmistatud_graafikul.insert(tk.END, default_values[10])
punkte_keskmistatud_graafikul.grid(column=1, row=7)
keskmistatud_tiheduse_label.grid(column=2, row=7)

ttk.Button(graafiku_tab,text="kuva graafik",command=visualiseeri).grid(column=0,row=8)


nimekirja_tab = ttk.Frame(tabControl)
tabControl.add(nimekirja_tab, text='sõitude nimekiri')
sõite_kokku=ttk.Label(nimekirja_tab)
sõite_kokku.grid(column=0, row=1)
#kolumnid=("t_algus","alguse_aadress","t_lõpp","hind","tellija","sõite tellijaga","arvenumber","makseviis","saaja_aadress","juriidilise_keha_registrikood","adressaadi_VAT_number","juhi_juriidilise_isiku_nimi","juhi_juriidilise_isiku_aadress","juriidilise_isiku_registrikood","ettevõtte_VAT_number","hind_ilma_käibemaksuta","käibemaks_hinnas")
tabel=ttk.Treeview(nimekirja_tab,show="headings")
# scrollbars
#vsb = ttk.Scrollbar(nimekirja_tab, orient="vertical", command=tabel.yview)
#vsb.place(relx=0.978, rely=0.175, relheight=0.713, relwidth=0.020)
#hsb = ttk.Scrollbar(nimekirja_tab, orient="horizontal", command=tabel.xview)
#hsb.place(relx=0.014, rely=0.875, relheight=0.020, relwidth=0.965)
#tabel.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

lahter_mille_järgi_viimati_sorditi=False
def treeview_sort_column(tabel, col, reverse,sortimis_funktsioonid):
    global lahter_mille_järgi_viimati_sorditi
    if lahter_mille_järgi_viimati_sorditi==col:
        reverse=True
        lahter_mille_järgi_viimati_sorditi=False
    else:
        reverse=False
        lahter_mille_järgi_viimati_sorditi=col
    print("col:",col,"; reverse:",reverse)
    if col[1]=="kviitungifailist":
        sõidud2.sort(key=lambda x:x.kviitungi_faili_data[col[0]],reverse=reverse)
    elif col[1]=="sõidufailist":
        sõidud2.sort(key=lambda x:x.sõidu_faili_data[col[0]],reverse=reverse)
    else:
        sõidud2.sort(key=sortimis_funktsioonid[col], reverse=reverse)
    uuenda_tabeli_sisu()

tabel.grid(row=0,column=0)
tabControl.pack(expand=1,fill="both")
root.mainloop()