import streamlit as st
import pandas as pd
import locale
from streamlit_echarts import st_echarts

# Funktion zur Berechnung der Kapitalentwicklung
def berechne_werte(startkapital, monatliche_einzahlung, kapitalwachstum_pro_tag, anlegeranzahl, anlegerwachstum_pro_monat, tage, gebuehr_prozent):
    gesamtkapital = [startkapital * anlegeranzahl]
    einzelkapital = [startkapital]  # Kapitalentwicklung für einen Anleger
    umsatz = [1]
    for tag in range(1, tage + 1):
        if tag % 30 == 0:  # Monatliche Anpassungen
            anlegeranzahl *= (1 + anlegerwachstum_pro_monat / 100)  # Anlegerwachstum
            gesamtkapital[-1] += monatliche_einzahlung * anlegeranzahl
            einzelkapital[-1] += monatliche_einzahlung

        gewinn_gesamt = gesamtkapital[-1] * kapitalwachstum_pro_tag / 100
        gesamtkapital.append(gesamtkapital[-1] + gewinn_gesamt)
        gewinn_einzel = einzelkapital[-1] * kapitalwachstum_pro_tag / 100
        einzelkapital.append(einzelkapital[-1] + gewinn_einzel)
        tagesumsatz = gewinn_gesamt * gebuehr_prozent / 100
        umsatz.append(umsatz[-1] + tagesumsatz)
    return gesamtkapital, umsatz, einzelkapital

# Funktion zur Aggregation der Daten basierend auf dem Zeitrahmen
def aggregiere_daten(daten, zeitrahmen):
    df = pd.DataFrame({"Werte": daten})
    if zeitrahmen == "30 Tage (Monat)":
        return df
    elif zeitrahmen == "90 Tage (Quartal)":
        return df.iloc[::2, :]  # Jeden zweiten Tag
    elif zeitrahmen == "12 Monate (Jahr)":
        return df.iloc[::30, :]  # Monatlich
    elif zeitrahmen == "12 Quartale (3 Jahre)":
        return df.iloc[::90, :]  # Quartalsweise
    elif zeitrahmen == "12 halbe Jahre (5 Jahre)":
        return df.iloc[::180, :]  # Halbjährlich
    elif zeitrahmen == "10 Jahre":
        return df.iloc[::365, :]  # Jährlich
    else:
        return df


def zeige_wachstumsdaten(daten, titel):
    locale.setlocale(locale.LC_ALL, 'de_DE')

    startwert = daten[0]
    endwert = daten[-1]
    wachstum = ((endwert - startwert) / startwert) * 100 if startwert != 0 else 0
    pnl = endwert - startwert
    
    formatted_startwert = locale.format_string("%0.2f", startwert, grouping=True)
    formatted_endwert = locale.format_string("%0.2f", endwert, grouping=True)
    formatted_pnl = locale.format_string("%0.2f", pnl, grouping=True)
    formatted_wachstum = locale.format_string("%0.2f", wachstum, grouping=True)

    
    st.subheader(titel)
    st.markdown(f'''
                **P&L:** :green[{formatted_pnl}] €  
                **Wachstum:** {formatted_wachstum} %  
                **Startwert:** {formatted_startwert} €  
                **Endwert:** {formatted_endwert} €
                ''')

# Streamlit App
def main():
    st.title("Kapital- und Umsatzentwicklung")

    # Eingabe-Widgets
    zeitrahmen = st.sidebar.selectbox(
        "Zeitraum auswählen:",
        ("30 Tage (Monat)", "90 Tage (Quartal)", "12 Monate (Jahr)", "12 Quartale (3 Jahre)", "12 halbe Jahre (5 Jahre)", "10 Jahre")
    )
    anlegeranzahl_start = st.sidebar.number_input("Anlegeranzahl zu Beginn der Rechnung", value=50)
    startkapital = st.sidebar.number_input("Durchschnittsstartkapital pro Anleger (€)", value=10000)
    monatliche_einzahlung = st.sidebar.number_input("Durchschnittlich weitere Einzahlung (pro Monat pro Anleger)", value=200)
    kapitalwachstum_pro_tag = st.sidebar.number_input("Durchschnittliches Kapitalwachstum pro Tag (in %)", value=1)
    gebuehr_prozent = st.sidebar.number_input("Unsere Gebühr (in %)", value=10)
    anlegerwachstum_pro_monat = st.sidebar.number_input("Durchschnittliches Wachstum der Anleger pro Monat (in %)", value=5)

    # Berechnung durchführen
    tage = {"30 Tage (Monat)": 30, "90 Tage (Quartal)": 90, "12 Monate (Jahr)": 365, "12 Quartale (3 Jahre)": 3*365, "12 halbe Jahre (5 Jahre)": 5*365, "10 Jahre": 10*365}[zeitrahmen]
    kapital, umsatz, einzelkapital = berechne_werte(startkapital, monatliche_einzahlung, kapitalwachstum_pro_tag, anlegeranzahl_start, anlegerwachstum_pro_monat, tage, gebuehr_prozent)
    kapital_aggregiert = aggregiere_daten(kapital, zeitrahmen)
    umsatz_aggregiert = aggregiere_daten(umsatz, zeitrahmen)
    einzelkapital_aggregiert = aggregiere_daten(einzelkapital, zeitrahmen)
    
    # ECharts-Diagramm für Umsatzentwicklung
    options_umsatz = {
        "xAxis": {"type": "category", "data": list(umsatz_aggregiert.index)},
        "yAxis": {"type": "value"},
        "series": [{"data": list(umsatz_aggregiert['Werte']), "type": "line"}],
        "tooltip": {
            "trigger": "axis"
            }
    }
    st.subheader("Umsatzwachstum (Gebühren)")
    zeige_wachstumsdaten(umsatz, "")
    st_echarts(options=options_umsatz)


    # ECharts-Diagramm für Kapitalentwicklung
    options_kapital = {
        "xAxis": {"type": "category", "data": list(kapital_aggregiert.index)},
        "yAxis": {"type": "value"},
        "series": [{"data": list(kapital_aggregiert['Werte']), "type": "line"}],
        "tooltip": {"trigger": "axis"}
    }
    st.subheader("Gesamtwachstum Kapital")
    zeige_wachstumsdaten(kapital, "")
    st_echarts(options=options_kapital)


    options_einzelkapital = {
        "xAxis": {"type": "category", "data": list(einzelkapital_aggregiert.index)},
        "yAxis": {"type": "value"},
        "series": [{"data": list(einzelkapital_aggregiert['Werte']), "type": "line"}],
        "tooltip": {"trigger": "axis"}
    }
    st.subheader("Kapitalwachstum pro Anleger")
    zeige_wachstumsdaten(einzelkapital, "")
    st_echarts(options=options_einzelkapital)

if __name__ == "__main__":
    main()
