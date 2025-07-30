import streamlit as st
import pandas as pd
import numpy as np
import locale
from io import BytesIO
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.holtwinters import Holt
import plotly.graph_objects as go
import seaborn as sns
import plotly.express as px
from datetime import datetime

st.title("ASP ConTe Servizi Territoriali - dashboards di monitoraggio e analisi dati")

uploaded_file = st.file_uploader("Carica il file Excel", type=["xlsx"])

if uploaded_file:
    
    df = pd.read_excel(uploaded_file)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df['Distretto'] = df['Distretto'].str.strip()
    df['Distretto'] = df['Distretto'].str.replace('location_on', '', case=False, regex=False)
    df['Distretto'].replace("CATANIA EX CATANIA1", "CATANIA", inplace=True)
    df['Assistito'] = df['Assistito'].str.replace('lock', '', case=False, regex=False)
    
    # Esempio: carichi il tuo DataFrame
    # df = pd.read_csv("...") oppure df = ...

    # 1. Pulizia spazi bianchi
    df['Data'] = df['Data'].astype(str).str.strip()

    # 2. Se hai orario tipo "22/07/2025 11:40", tieni solo la parte della data
    df['Data'] = df['Data'].str.split().str[0]

    # 3. Ora la conversione andrà a buon fine
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
    #df['Data_format'] = df['Data'].dt.strftime('%d/%m/%Y')

    # 4. Mappatura mesi
    mesi_italiani = {
        1: 'gennaio', 2: 'febbraio', 3: 'marzo', 4: 'aprile',
        5: 'maggio', 6: 'giugno', 7: 'luglio', 8: 'agosto',
        9: 'settembre', 10: 'ottobre', 11: 'novembre', 12: 'dicembre'
    }

    df['Mese'] = df['Data'].dt.month.map(mesi_italiani) #estrazione del mese dalla colonna "Data"
    df['Anno'] = df['Data'].dt.year                     #estrazione dell'anno dalla colonna "Data"

    # Rinomina dicitura delle richieste
    df['Richiesta'].replace("Richiesta per DIABETE", "LA DIABBBETEH", inplace=True)
    df['Richiesta'].replace("Richiesta PROTESI ORTOPEDICHE, AUSILI PER LA MOBILITÀ, LA COMUNICAZIONE E OCULARI", "PROTESI ORTOPEDICHE E AUSILI PER LA MOBILITÀ E COMUNICAZIONE", inplace=True)
    df['Richiesta'].replace("Richiesta ASSORBENZA", "ASSORBENZA", inplace=True)
    df['Richiesta'].replace("Richiesta MEDICAZIONI AVANZATE", "MEDICAZIONI AVANZATE", inplace=True)
    df['Richiesta'].replace("Richiesta STOMIE (ileostomie, colostomie)", "STOMIE", inplace=True)
    df['Richiesta'].replace("Richiesta STOMIE (tracheostomie)", "STOMIE", inplace=True)
    df['Richiesta'].replace("Richiesta STOMIE", "STOMIE", inplace=True)
    df['Richiesta'].replace("Richiesta MICROINFUSORI e SENSORI per DIABETE", "MICROINFUSORI E SENSORI PER DIABETE", inplace=True)
    df['Richiesta'].replace("Richiesta CATETERI", "CATETERI", inplace=True)
    df['Richiesta'].replace("Richiesta VENTILATORI POLMONARI", "VENTILATORI POLMONARI", inplace=True)
    df['Richiesta'].replace("Richiesta PROTESI MAMMARIE", "PROTESI MAMMARIE", inplace=True)
    df['Richiesta'].replace("Richiesta INTEGRATORI", "INTEGRATORI", inplace=True)
    df['Richiesta'].replace("Richiesta NUTRIZIONE enterale (PEG)", "NUTRIZIONE ENTERALE", inplace=True)
    df['Richiesta'].replace("Richiesta NUTRIZIONE enterale (PEG) e parenterale (N.endovena)", "NUTRIZIONE ENTERALE E PARENTERALE", inplace=True)
    df['Richiesta'].replace("Richiesta NUTRIZIONE parenterale (N.endovena)", "NUTRIZIONE PARENTERALE", inplace=True)
    df['Richiesta'].replace("Richiesta PROTESI ACUSTICHE", "PROTESI ACUSTICHE", inplace=True)
    df['Richiesta'].replace("Richiesta CONCENTRATORI DI OSSIGENO", "CONCENTRATORI DI OSSIGENO", inplace=True)
    df['Richiesta'].replace("Richiesta OSSIGENO LIQUIDO (bombole)", "OSSIGENO LIQUIDO", inplace=True)
    df['Richiesta'].replace("Gestione Medico di Base e Pediatra (Scelta/Revoca)", "SCELTA/REVOCA MMG E PLS", inplace=True)
    df['Richiesta'].replace("Richiesta ESENZIONE PER PATOLOGIA", "ESENZIONE PER PATOLOGIA", inplace=True)
    df['Richiesta'].replace("RICHIESTA EMISSIONE TESSERA SANITARIA", "EMISSIONE TESSERA SANITARIA", inplace=True)
    #AGGIUNTI ALLA DATA DEL 22/07/2025
    df['Richiesta'].replace("BONUS SOCIALE PER DISAGIO FISICO PER LA FORNITURA DI ENERGIA ELETTRICA", "BONUS SOCIALE", inplace=True)
    df['Richiesta'].replace("Richiesta CELIACHIA", "CELIACHIA", inplace=True)
    df['Richiesta'].replace("Richiesta MALATTIE RARE (farmaci)", "MALATTIE RARE", inplace=True)
    df['Richiesta'].replace("Richiesta per alimenti per INSUFFICIENZA RENALE CRONICA", "INSUFFICIENZA RENALE CRONICA", inplace=True)
    df['Richiesta'].replace("Richiesta per difetti congeniti del metabolismo (FENILCHETONURIA e altri)", "FENILCHETONURIA", inplace=True)
    df['Richiesta'].replace("Richiesta TALASSEMIA", "TALASSEMIA", inplace=True)
    df['Richiesta'].replace("Richiesta VACUUM THERAPY", "VACUUM THERAPY", inplace=True)
    df['Richiesta'].replace("Richiesta SOSTITUTI DEL LATTE MATERNO (contributo fino a 400 euro , non oltre il SESTO mese di vita del neonato", "SOSTITUTO LATTE MATERNO", inplace=True)
    df['Richiesta'].replace("Richiesta PARRUCCA  (contributo euro 300)", "PARRUCCA", inplace=True)


    df['Stato'].replace("ANNULLATA DALL’UFFICIO", "ANNULLATA DA UFFICIO", inplace=True)
    df['Stato'].replace("ANNULLATA DALL’UTENTE", "ANNULLATA DA UTENTE", inplace=True)

    richieste_protesi_e_ausili = [
        "LA DIABBBETEH", "PROTESI ORTOPEDICHE E AUSILI PER LA MOBILITÀ E COMUNICAZIONE", "ASSORBENZA",
        "MEDICAZIONI AVANZATE", "MICROINFUSORI E SENSORI PER DIABETE", "CATETERI",
        "VENTILATORI POLMONARI", "OSSIGENO LIQUIDO", "PROTESI MAMMARIE", "INTEGRATORI",
        "NUTRIZIONE ENTERALE", "NUTRIZIONE PARENTERALE", "NUTRIZIONE ENTERALE E PARENTERALE", "PROTESI ACUSTICHE", "CONCENTRATORI DI OSSIGENO", "BONUS SOCIALE", "CELIACHIA",
        "MALATTIE RARE", "INSUFFICIENZA RENALE CRONICA", "FENILCHETONURIA", "STOMIE", 
        "TALASSEMIA", "VACUUM THERAPY", 'SOSTITUTO LATTE MATERNO'
    ]

    richieste_anagrafe_assistiti = [
        "E01 - ESENZIONE PER ETA’ E REDDITO", "SCELTA/REVOCA MMG E PLS", "ESENZIONE PER PATOLOGIA",
        "EMISSIONE TESSERA SANITARIA", "E03 - TITOLARE ASSEGNO (EX PENSIONE) SOCIALE (o familiare a carico del titolare di assegno sociale)",
        "E02 - ESENZIONE DISOCCUPATO (o familiare a carico del disoccupato)",
        "E04 - TITOLARE DI PENSIONE AL MINIMO (o familiare a carico del titolare di pensione al minimo)"
    ]

    condizioni = [
        df['Richiesta'].isin(richieste_protesi_e_ausili),
        df['Richiesta'].isin(richieste_anagrafe_assistiti)
    ]
    valori = ['Protesi e ausili', 'Anagrafe assistiti']
    df['Ufficio'] = np.select(condizioni, valori, default='Altro')
    df['Indicatore di incompetenza'] = df['Assistito'].str.contains('Richiedente', case=False, na=False)
    numero_delegati = df['Indicatore di incompetenza'].sum() #Variabile numerica - numero di delegati
    df['Richiedente/delegato'] = df['Assistito'].str.extract(r'Richiedente:\s*(.*)', expand=False)
    df['Assistito'] = df['Assistito'].str.replace(r'\s*Richiedente:.*', '', regex=True)

    
    
    #Creazione colonne con indicatore: Ritardo lavorazione istanza
    

    oggi = datetime.now()
    df['Differenza giorni'] = (oggi - df['Data']).dt.days
    #Condizione "IF" ma VETTORIALE per Pandas e datafeatures
    df['Ind. ritardo lavorazione'] = ((df['Differenza giorni'] > giorni_scelti) & (df['Stato'] == 'IN ATTESA'))

    df = df[['Data', 'Anno', 'Mese', 'Differenza giorni', 'Ind. ritardo lavorazione', 'Distretto', 'Assistito', 'Richiedente/delegato', 'Richiesta', 'Stato', 'Ufficio', 'Indicatore di incompetenza']]
    if df['Data'].dtype == 'object':
        df['Data'] = df['Data'].str[:-6]
    perc_delegati = (numero_delegati/(len(df)))*100

    # Definisci le date
    data_inizio = datetime.strptime("2025-05-12", "%Y-%m-%d").date()
    data_fine = datetime.today().date()

    giorni = (data_fine - data_inizio).days
    #print(giorni)
    
    #giorni_scelti = int(input("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nInserisci un valore intero, maggiore di 0, che funga da valore Delta per segnalare le lavorazioni di istanze attualmente in ritardo: "))
    giorni_scelti = st.number_input(
    f"Inserisci un valore intero, maggiore di 0 e minore di {giorni}, che funga da valore Delta per segnalare le lavorazioni di istanze attualmente in ritardo:",
    min_value=1,
    step=1,
    value=1  # valore di default
    )
    media_istanze_giorno = (len(df))/(giorni)
    st.subheader(f"Dataset importato con successo - dati aggiornati al {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"1) Il dataset contiene **{len(df)}** records/istanze caricate in piattaforma dalla data del {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"2) La media giornaliera di istanze inserite in piattaforma è pari a: **{media_istanze_giorno:.2f}**")
    st.write(f"3) Il numero di istanze inserite da un delegato dell'assistito è pari a **{numero_delegati}** - percentuale del **{perc_delegati:.2f}%**")
    
    # Colonne da nascondere
    colonne_da_nascondere = ['Assistito', 'Richiedente/delegato', 'Differenza giorni', 'Ind. ritardo lavorazione']

    # Mostra solo le colonne che non sono da nascondere
    df_no_nominativi = df.drop(columns=colonne_da_nascondere)

    #st.subheader(f"Dataset anonimizzato - {datetime.now().strftime('%d/%m/%Y')}")
    #st.dataframe(df_no_nominativi)
    #st.subheader(f"Dataset completo (NON anonimizzato) - {datetime.now().strftime('%d/%m/%Y')}")
    #st.dataframe(df)

    pivot1 = pd.pivot_table(df, values='Assistito', index=['Distretto', 'Ufficio'], columns='Stato', aggfunc='count')
    #Ordinamento delle colonne della pivot1 del dataset completo df
    pivot1 = pivot1[['COMPLETATA', 'IN ATTESA', 'RESPINTA', 'SOSPESA', 'IN LAVORAZIONE', 'ANNULLATA DA UFFICIO', 'ANNULLATA DA UTENTE',
                      'ATTESA SCELTA UTENTE', 'IN ATTESA DI APPROVAZIONE MEDICA', 'INTEGRAZIONE DOCUMENTAZIONE', 'RIASSEGNATA']]
    stati = ['COMPLETATA', 'IN ATTESA', 'RESPINTA', 'ANNULLATA DA UFFICIO', 'ANNULLATA DA UTENTE' 'ATTESA SCELTA UTENTE',
             'IN ATTESA DI APPROVAZIONE MEDICA', 'IN LAVORAZIONE', 'INTEGRAZIONE DOCUMENTAZIONE', 'RIASSEGNATA', 'SOSPESA']
    
    pivot1['Totale istanze per ufficio e distretto'] = pivot1.fillna(0).sum(axis=1)

    #AGGIUNTA RIGA DI SOMMA - PIVOT1 
    pivot1.loc['Totale istanze per stato', 'COMPLETATA'] = sum_completata = pivot1['COMPLETATA'].sum()
    pivot1.loc['Totale istanze per stato', 'IN ATTESA'] = sum_attesa = pivot1['IN ATTESA'].sum()
    pivot1.loc['Totale istanze per stato', 'RESPINTA'] = sum_respinta = pivot1['RESPINTA'].sum()
    pivot1.loc['Totale istanze per stato', 'SOSPESA'] = sum_sospesa = pivot1['SOSPESA'].sum()
    pivot1.loc['Totale istanze per stato', 'IN LAVORAZIONE'] = sum_lavorazione = pivot1['IN LAVORAZIONE'].sum()
    pivot1.loc['Totale istanze per stato', 'ANNULLATA DA UFFICIO'] = sum_annullata_ufficio = pivot1['ANNULLATA DA UFFICIO'].sum()
    pivot1.loc['Totale istanze per stato', 'ANNULLATA DA UTENTE'] = sum_annullata_utente = pivot1['ANNULLATA DA UTENTE'].sum()
    pivot1.loc['Totale istanze per stato', 'ATTESA SCELTA UTENTE'] = sum_attesa_scelta_utente = pivot1['ATTESA SCELTA UTENTE'].sum()
    pivot1.loc['Totale istanze per stato', 'IN ATTESA DI APPROVAZIONE MEDICA'] = sum_approvazione_medica= pivot1['IN ATTESA DI APPROVAZIONE MEDICA'].sum()
    pivot1.loc['Totale istanze per stato', 'INTEGRAZIONE DOCUMENTAZIONE'] = sum_integrazione_documentazione= pivot1['INTEGRAZIONE DOCUMENTAZIONE'].sum()
    pivot1.loc['Totale istanze per stato', 'RIASSEGNATA'] = sum_riassegnata = pivot1['RIASSEGNATA'].sum()

    
    #st.subheader("Tabella Pivot per Distretto - Ufficio - Stato della richiesta")
    #st.dataframe(pivot1)

    pivot2 = pd.pivot_table(df, values='Assistito', index=['Distretto', 'Ufficio'], columns='Mese', aggfunc='count')
    pivot2['Totale istanze per ufficio e distretto'] = pivot1.fillna(0).sum(axis=1)
    pivot2 = pivot2[['maggio', 'giugno', 'luglio']]
    pivot2.loc['Totale istanze per mese', 'maggio'] = sum_istanze_maggio = pivot2['maggio'].sum()
    pivot2.loc['Totale istanze per mese', 'giugno'] = sum_istanze_giugno = pivot2['giugno'].sum()
    pivot2.loc['Totale istanze per mese', 'luglio'] = sum_istanze_luglio = pivot2['luglio'].sum()

    media_istanze_maggio = (sum_istanze_maggio)/20 #20: quantità giorni da 12 Maggio a 31 Maggio
    media_istanze_giugno = (sum_istanze_giugno)/30
    media_istanze_luglio = (sum_istanze_luglio)/31
    
    #st.subheader("Tabella Pivot per Distretto - Ufficio - Mese")
    #st.dataframe(pivot2)

    # CREAZIONE DELLA TABELLA PIVOT 3 - CONTEGGI ISTANZE IN RITARDO DI LAVORAZIONE

    pivot3 = pd.pivot_table(df, values='Ind. ritardo lavorazione', index=['Distretto', 'Ufficio'], columns='Mese', aggfunc='sum')
    pivot3 = pivot3[['maggio', 'giugno', 'luglio']]
    pivot3.loc['Totale lavorazioni in ritardo per mese', 'maggio'] = sum_lavorazioni_ritardo_istanze_maggio = pivot3['maggio'].sum()
    pivot3.loc['Totale lavorazioni in ritardo per mese', 'giugno'] = sum_lavorazioni_ritardo_istanze_giugno = pivot3['giugno'].sum()
    pivot3.loc['Totale lavorazioni in ritardo per mese', 'luglio'] = sum_lavorazioni_ritardo_istanze_luglio = pivot3['luglio'].sum()
    #st.subheader(f"Tabella Pivot - Quantità di giorni di ritardo lavorazione istanze - sentinella numerica impostata a **{giorni_scelti}**(giorni) da utente")
    #st.dataframe(pivot3)

    
    #CREAZIONE DELLA TABELLA PIVOT 4 - CONTEGGI ISTANZE PER TIPOLOGIA DI RICHIESTA
    pivot4 = pd.pivot_table(df, values='Assistito', index=['Distretto', 'Ufficio'], columns='Richiesta', aggfunc='count')
    #pivot4 = pivot4[richieste_protesi_e_ausili, richieste_anagrafe_assistiti]
  
    pivot4.loc['Totale per tipologia richiesta', 'LA DIABBBETEH'] = sum_diabete = pivot4['LA DIABBBETEH'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'ASSORBENZA'] = sum_assorbenza = pivot4['ASSORBENZA'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'PROTESI ORTOPEDICHE E AUSILI PER LA MOBILITÀ E COMUNICAZIONE'] = sum_ortopediche = pivot4['PROTESI ORTOPEDICHE E AUSILI PER LA MOBILITÀ E COMUNICAZIONE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'MEDICAZIONI AVANZATE'] = sum_medicazioni = pivot4['MEDICAZIONI AVANZATE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'MICROINFUSORI E SENSORI PER DIABETE'] = sum_microinfusore = pivot4['MICROINFUSORI E SENSORI PER DIABETE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'CATETERI'] = sum_cateteri = pivot4['CATETERI'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'VENTILATORI POLMONARI'] = sum_ventilatori = pivot4['VENTILATORI POLMONARI'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'OSSIGENO LIQUIDO'] = sum_ossigenoliquido = pivot4['OSSIGENO LIQUIDO'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'PROTESI MAMMARIE'] = sum_protesimammarie = pivot4['PROTESI MAMMARIE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'INTEGRATORI'] = sum_integratori = pivot4['INTEGRATORI'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'NUTRIZIONE ENTERALE'] = sum_nutrizioneenterale = pivot4['NUTRIZIONE ENTERALE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'NUTRIZIONE ENTERALE E PARENTERALE'] = sum_nutrizioneenteraleparenterale = pivot4['NUTRIZIONE ENTERALE E PARENTERALE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'NUTRIZIONE PARENTERALE'] = sum_nutrizioneparenterale = pivot4['NUTRIZIONE PARENTERALE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'PROTESI ACUSTICHE'] = sum_protesiacustiche = pivot4['PROTESI ACUSTICHE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'CONCENTRATORI DI OSSIGENO'] = sum_concentratoriossigeno = pivot4['CONCENTRATORI DI OSSIGENO'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'BONUS SOCIALE'] = sum_bonussociale = pivot4['BONUS SOCIALE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'CELIACHIA'] = sum_celiachia = pivot4['CELIACHIA'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'MALATTIE RARE'] = sum_malattierare = pivot4['MALATTIE RARE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'INSUFFICIENZA RENALE CRONICA'] = sum_insuffrenale = pivot4['INSUFFICIENZA RENALE CRONICA'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'FENILCHETONURIA'] = sum_fenilchetonuria = pivot4['FENILCHETONURIA'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'STOMIE'] = sum_stomie = pivot4['STOMIE'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'TALASSEMIA'] = sum_talassemia = pivot4['TALASSEMIA'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'VACUUM THERAPY'] = sum_vacuum = pivot4['VACUUM THERAPY'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'E01 - ESENZIONE PER ETA’ E REDDITO'] = sum_E01 = pivot4['E01 - ESENZIONE PER ETA’ E REDDITO'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'E02 - ESENZIONE DISOCCUPATO (o familiare a carico del disoccupato)'] = sum_E02 = pivot4['E02 - ESENZIONE DISOCCUPATO (o familiare a carico del disoccupato)'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'E03 - TITOLARE ASSEGNO (EX PENSIONE) SOCIALE (o familiare a carico del titolare di assegno sociale)'] = sum_E03 = pivot4['E03 - TITOLARE ASSEGNO (EX PENSIONE) SOCIALE (o familiare a carico del titolare di assegno sociale)'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'E04 - TITOLARE DI PENSIONE AL MINIMO (o familiare a carico del titolare di pensione al minimo)'] = sum_E04 = pivot4['E04 - TITOLARE DI PENSIONE AL MINIMO (o familiare a carico del titolare di pensione al minimo)'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'ESENZIONE PER PATOLOGIA'] = sum_esenzionepatologia = pivot4['ESENZIONE PER PATOLOGIA'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'SCELTA/REVOCA MMG E PLS'] = sum_sceltaMMGPLS = pivot4['SCELTA/REVOCA MMG E PLS'].sum()
    pivot4.loc['Totale per tipologia richiesta', 'EMISSIONE TESSERA SANITARIA'] = sum_tesserasanitaria = pivot4['EMISSIONE TESSERA SANITARIA'].sum()

    #st.subheader(f"Tabella Pivot - Quantità istanze per tipologia di richiesta")
    #st.dataframe(pivot4)


    pivot_df = pivot1.reset_index()

    for stato in stati:
        if stato not in pivot_df.columns:
            pivot_df[stato] = 0
        pivot_df[stato] = pd.to_numeric(pivot_df[stato], errors='coerce').fillna(0)

    for stato in stati:
        pivot_df[f'% {stato}'] = ((pivot_df[stato] / pivot_df['Totale istanze per ufficio e distretto']) * 100).round(2)


    indicatori_df = pivot_df[['Distretto', 'Ufficio'] + [f'% {s}' for s in stati]]

    # Calcola la media solo delle colonne delle percentuali
    media_valori = indicatori_df[[f'% {s}' for s in stati]].mean()

    # Crea una nuova riga con valori vuoti per le colonne non numeriche
    nuova_riga = {col: '' for col in ['Distretto', 'Ufficio']}
    nuova_riga.update(media_valori.to_dict())

    # Aggiungi la riga al DataFrame
    indicatori_df.loc['Media percentuale'] = nuova_riga

    # Metti la riga alla fine
    indicatori_df = indicatori_df.reindex(
        [x for x in indicatori_df.index if x != 'Media percentuale'] + ['Media percentuale']
    )

    st.title("Dashboard principale")

    # Creazione dei tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Dataset anonimizzato", "Dataset completo", "Pivot Ufficio - Distretto", "Pivot Distretto - Ufficio - Mese", "Pivot ritardo lavorazione", "Pivot - istanze tipologia", "Pivot percentuali lavorazione"])

    with tab1:
        st.subheader(f"Dataset anonimizzato - {datetime.now().strftime('%d/%m/%Y')}")
        st.dataframe(df_no_nominativi)
    with tab2:
        st.subheader(f"Dataset completo (NON anonimizzato) - {datetime.now().strftime('%d/%m/%Y')}")
        st.dataframe(df)
    with tab3:
        st.subheader("Totale istanze per ufficio e distretto")
        st.dataframe(pivot1)
    with tab4:
        st.subheader("Tabella Pivot per Distretto - Ufficio - Mese")
        st.dataframe(pivot2)
    with tab5:
        st.subheader("Tabella Pivot - Quantità di giorni di ritardo lavorazione istanze - sentinella numerica impostata a **{giorni_scelti}**(giorni) da utente")
        st.dataframe(pivot3)
    with tab6:
        st.subheader("Tabella Pivot - Quantità istanze per tipologia di richiesta")
        st.dataframe(pivot4)
    with tab7:
        st.subheader("Tabella - Indicatori percentuali di lavorazione istanze")
        st.dataframe(indicatori_df)
    # -------------------------
    # CREAZIONE DELLA TABELLA PIVOT (se non è già fatta)
    # -------------------------
    # pivot2 = pd.pivot_table(df, values='Assistito', index=['Distretto', 'Ufficio'], columns='Mese', aggfunc='count')
    # pivot2 = pivot2[['maggio', 'giugno', 'luglio']]

    # ESEMPIO SOLO SE NON HAI `pivot2` PRONTO:
    # df = pd.read_csv('tuo_file.csv')  # oppure qualsiasi sorgente
    # pivot2 = pd.pivot_table(df, values='Assistito', index=['Distretto', 'Ufficio'], columns='Mese', aggfunc='count')
    # pivot2 = pivot2[['maggio', 'giugno', 'luglio']]

    # -------------------------
    # PREPARAZIONE DATI PER I FILTRI
    # -------------------------
    # Crea una colonna "Distretto - Ufficio" combinata per visualizzazione
    pivot2.index = [f"{dist} - {uff}" for dist, uff in pivot2.index]
    pivot2_reset = pivot2.reset_index().rename(columns={'index': 'Distretto - Ufficio'})

    # Ristruttura il DataFrame in formato lungo per Plotly
    df_long = pd.melt(pivot2_reset, id_vars='Distretto - Ufficio', var_name='Mese', value_name='Numero Assistiti')

    # Estrai Distretto e Ufficio separatamente
    df_long[['Distretto', 'Ufficio']] = df_long['Distretto - Ufficio'].str.split(' - ', expand=True)

    # -------------------------
    # FILTRI INTERATTIVI
    # -------------------------
    st.sidebar.header("Filtri per la Heatmap")

    distretti = df_long['Distretto'].unique()
    uffici = df_long['Ufficio'].unique()
    mesi = df_long['Mese'].unique()

    filtro_distretto = st.sidebar.multiselect("Seleziona Distretto", sorted(distretti), default=sorted(distretti))
    filtro_ufficio = st.sidebar.multiselect("Seleziona Ufficio", sorted(uffici), default=sorted(uffici))
    filtro_mese = st.sidebar.multiselect("Seleziona Mese", sorted(mesi), default=sorted(mesi))

    # -------------------------
    # APPLICA I FILTRI
    # -------------------------
    df_filtrato = df_long[
        (df_long['Distretto'].isin(filtro_distretto)) &
        (df_long['Ufficio'].isin(filtro_ufficio)) &
        (df_long['Mese'].isin(filtro_mese))
    ]

    # Ricombina "Distretto - Ufficio" dopo il filtro
    df_filtrato['Distretto - Ufficio'] = df_filtrato['Distretto'] + ' - ' + df_filtrato['Ufficio']
    # -------------------------
    # HEATMAP INTERATTIVA PLOTLY
    # -------------------------
    st.subheader("Heatmap interattiva")
    st.caption(f"-Media giornaliera istanze caricate a maggio: {media_istanze_maggio:.2f}")
    st.caption(f"-Media giornaliera istanze caricate a giugno: {media_istanze_giugno:.2f}")
    st.caption(f"-Media giornaliera istanze caricate a luglio: {media_istanze_luglio:.2f}")

    if df_filtrato.empty:
        st.warning("Nessun dato disponibile con i filtri selezionati.")
    else:
        fig = px.density_heatmap(
        df_filtrato,
        x='Mese',
        y='Distretto - Ufficio',
        z='Numero Assistiti',
        color_continuous_scale='Sunset',
        text_auto=True,
        title="Numero di assistiti per Distretto-Ufficio e Mese",
        width=800, height=600
        )

        # Font globale (tick, hovering, legend)
        fig.update_layout(
            font=dict(family="Arial", size=14, color="black")
        )

        # Tick labels: dimensione personalizzata per asse
        fig.update_xaxes(tickfont=dict(size=16))
        fig.update_yaxes(tickfont=dict(size=16))

        # Cell number formatting
        fig.update_traces(
            textfont=dict(size=18),          # dimensione del numero nelle celle
            selector=dict(type="densityheatmap")
        )

        # Titolo più grande e margini corretti
        fig.update_layout(
            title=dict(text="Istanze mensili", font=dict(size=15)),
            margin=dict(l=120, r=40, t=80, b=80)
        )
    st.plotly_chart(fig, use_container_width=True)

    #indicatori_df = indicatori_df.drop(20)

    #st.subheader("Tabella - Indicatori percentuali di lavorazione istanze")
    #st.dataframe(indicatori_df)
    
    st.subheader("Grafico a barre interattivo della distribuzione")
    pivot_plot = pivot1.reset_index()
    pivot_long = pd.melt(pivot_plot, id_vars=['Distretto', 'Ufficio'], var_name='Stato', value_name='Numero assistiti')
    fig = px.bar(pivot_long, x='Ufficio', y='Numero assistiti', color='Stato', facet_col='Distretto', barmode='group')
    fig.update_layout(xaxis_title="Ufficio", yaxis_title="Numero di assistiti", height=600)
    st.plotly_chart(fig, use_container_width=True)

    try:
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df = df.dropna(subset=['Data'])
        df = df.sort_values('Data')
        dati_giornalieri = df.groupby('Data')['Assistito'].count().reset_index()
        dati_giornalieri['Settimana'] = dati_giornalieri['Data'].dt.to_period('W').apply(lambda r: r.start_time)
        picchi_settimanali = dati_giornalieri.loc[dati_giornalieri.groupby('Settimana')['Assistito'].idxmax()]
        picchi_settimanali = picchi_settimanali.sort_values('Data')

        st.subheader("Andamento temporale interattivo delle richieste")
        fig2 = px.line(dati_giornalieri, x='Data', y='Assistito', markers=True,
                       title=f'Curva temporale - Presentazione istanze dal 12/05/2025 al {datetime.now().strftime('%d/%m/%Y')}',
                       labels={'Assistito': 'Numero di assistiti'})
        fig2.add_scatter(x=picchi_settimanali['Data'], y=picchi_settimanali['Assistito'],
                         mode='lines+markers', name='Picchi settimanali',
                         line=dict(color='red', width=2), marker=dict(color='red', size=8))
        fig2.update_layout(height=600, xaxis_title="Data", yaxis_title="Istanze presentate")
        st.plotly_chart(fig2, use_container_width=True)

        

    except:
        st.warning("Errore nel parsing della colonna Data.")

    
    
        #CREAZIONE PIVOT PER GENERAZIONE DEI DATI PREVISIONALI
    # ========================
    # PREVISIONE CON SES
    # ========================

    st.subheader("Analisi previsionale sui dati aggregati per mese")

    # Creazione tabella pivot generativa
    pivot_generativa = pd.pivot_table(
        df,
        values='Richiesta',
        index=['Mese'],
        aggfunc='count'
    )

    st.write("Simulazione quantità di istanze inserite in piattaforma")

    # Ordina i mesi manualmente
    ordine_mesi = [
        'gennaio', 'febbraio', 'marzo', 'aprile',
        'maggio', 'giugno', 'luglio', 'agosto',
        'settembre', 'ottobre', 'novembre', 'dicembre'
    ]
    pivot_generativa = pivot_generativa.reindex(ordine_mesi).dropna(how='all')

    # Estrai la serie (senza l'indice stringa)
    serie = pivot_generativa['Richiesta'].reset_index(drop=True)

    # Slider: quanti mesi prevedere
    forecast_periods = st.slider("Mesi futuri da prevedere", 1, 12, 3)

    # Modello Holt
    model = Holt(serie)
    fit = model.fit(optimized=True)
    forecast = fit.forecast(forecast_periods)

    # Prepara asse x
    mesi_passati = pivot_generativa.index.tolist()
    mesi_futuri = [f"forecast_{i+1}" for i in range(forecast_periods)]
    x_labels = mesi_passati + mesi_futuri

    # Grafico
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mesi_passati,
        y=serie,
        mode='lines+markers',
        name='Storico'
    ))
    fig.add_trace(go.Scatter(
        x=mesi_futuri,
        y=forecast,
        mode='lines+markers',
        name='Previsione',
        line=dict(dash='dash')
    ))

    fig.update_layout(
        title="Previsione basata su modello predittivo (Holt) - Exponential Smoothing",
        xaxis_title="Mese",
        yaxis_title="Nr. istanze",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    #FUNZIONE DI ESPORTAZIONE DATASETS E PIVOTS PROCESSATI
  
    def to_excel(df1, df2, df3, df4, df5, indicatori_df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df1.to_excel(writer, sheet_name='Data processed', index=False)
                df2.to_excel(writer, sheet_name='Pivot1 - stato richiesta', index=True)
                df3.to_excel(writer, sheet_name='Pivot2 - numeri mensili', index=True)
                df4.to_excel(writer, sheet_name='Pivot3 - numeri ritardo', index=True)
                df5.to_excel(writer, sheet_name='Pivot4 - tipol. richiesta', index=True)
                indicatori_df.to_excel(writer, sheet_name='Pivot5 - Indicatori_efficienza', index=True)
            output.seek(0)
            return output

    excel_data = to_excel(df, pivot1, pivot2, pivot3, pivot4, indicatori_df)

    timestamp = datetime.now().strftime("%d-%m-%Y")
    st.download_button(
    label="📥 Scarica in formato Excel (.xlsx)",
    data=excel_data,
    file_name=f"processed_report_ServiziTerritoriali_{timestamp}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
