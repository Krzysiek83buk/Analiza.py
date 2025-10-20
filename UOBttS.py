import streamlit as st
import math
import time
import pandas as pd

st.set_page_config(
    page_title="Analiza Zakładów Piłkarskich",
    page_icon="⚽",
    layout="wide"
)

# Tytuł aplikacji
st.title("⚽ ANALIZA MECZU OVER/UNDER 2.5 & BTTS")
st.markdown("---")

# Funkcje z Twojego kodu (NIE RUSZAJ TEGO!)
def oblicz_momentum(wyniki):
    if not wyniki:
        return 0
    
    momentum = 0
    wagi = [0.1, 0.15, 0.2, 0.25, 0.3]
    
    for i, wynik in enumerate(wyniki[-5:]):
        try:
            g1, g2 = map(int, wynik.split(':'))
            suma_goli = g1 + g2
            momentum += (suma_goli / 5) * wagi[i]
        except:
            continue
    
    return momentum

def oblicz_odchylenie_standardowe(wyniki):
    if len(wyniki) < 2:
        return 0
    
    sumy_goli = []
    for wynik in wyniki:
        try:
            g1, g2 = map(int, wynik.split(':'))
            sumy_goli.append(g1 + g2)
        except:
            continue
    
    if not sumy_goli:
        return 0
    
    srednia = sum(sumy_goli) / len(sumy_goli)
    wariancja = sum((x - srednia) ** 2 for x in sumy_goli) / len(sumy_goli)
    odchylenie = math.sqrt(wariancja)
    
    return odchylenie

def oblicz_kurs_fair(prawdopodobienstwo):
    if prawdopodobienstwo <= 0:
        return 99.9
    return round(100 / prawdopodobienstwo, 2)

def analiza_xg(xg_gosp, xg_gosc):
    srednie_xg_mecz = xg_gosp + xg_gosc
    
    if srednie_xg_mecz > 3.2:
        korekta_over = 8
    elif srednie_xg_mecz > 2.8:
        korekta_over = 5
    elif srednie_xg_mecz > 2.4:
        korekta_over = 2
    elif srednie_xg_mecz < 1.8:
        korekta_over = -8
    elif srednie_xg_mecz < 2.2:
        korekta_over = -5
    elif srednie_xg_mecz < 2.4:
        korekta_over = -2
    else:
        korekta_over = 0
    
    min_xg = min(xg_gosp, xg_gosc)
    max_xg = max(xg_gosp, xg_gosc)
    
    if min_xg > 1.4 and max_xg > 1.6:
        korekta_btts = 7
    elif min_xg > 1.2 and max_xg > 1.4:
        korekta_btts = 4
    elif min_xg > 1.0 and max_xg > 1.2:
        korekta_btts = 2
    elif min_xg < 0.6 or max_xg < 0.8:
        korekta_btts = -7
    elif min_xg < 0.8 or max_xg < 1.0:
        korekta_btts = -4
    elif min_xg < 1.0 or max_xg < 1.2:
        korekta_btts = -2
    else:
        korekta_btts = 0
    
    btts_potencjal = (xg_gosp + xg_gosc) / 2
    
    return korekta_over, korekta_btts, srednie_xg_mecz, btts_potencjal

def czy_dobry_value_bet(prawdopodobienstwo, value, momentum, odchylenie_gosp, odchylenie_gosc, typ_zakladu, xg_wskaznik):
    if prawdopodobienstwo < 40:
        return False, "Zbyt niska szansa (<40%)"
    
    if value < 5:
        return False, "Niewystarczająca przewaga value (<5%)"
    
    if odchylenie_gosp > 2.0 or odchylenie_gosc > 2.0:
        return False, "Zbyt niestabilne wyniki (odchylenie > 2.0)"
    
    if typ_zakladu == "OVER":
        if momentum < 0.8:
            return False, "Niskie momentum ofensywne (<0.😎"
        if xg_wskaznik < 2.4:
            return False, "Niskie xG (<2.4) nie wspiera OVER"
    elif typ_zakladu == "UNDER":
        if momentum > 1.2:
            return False, "Zbyt wysokie momentum dla under (>1.2)"
        if xg_wskaznik > 3.0:
            return False, "Wysokie xG (>3.0) nie wspiera UNDER"
    elif typ_zakladu == "BTTS_TAK":
        if momentum < 0.8:
            return False, "Niskie momentum BTTS (<0.😎"
        if xg_wskaznik < 1.0:
            return False, "Niskie xG (<1.0) nie wspiera BTTS TAK"
    elif typ_zakladu == "BTTS_NIE":
        if momentum > 1.2:
            return False, "Zbyt wysokie momentum dla BTTS nie (>1.2)"
        if xg_wskaznik > 1.4:
            return False, "Wysokie xG (>1.4) nie wspiera BTTS NIE"
    
    return True, "DOBRY VALUE BET - spełnia wszystkie kryteria"

# GŁÓWNA FUNKCJA APLIKACJI
def main():
    # Panel boczny z danymi wejściowymi
    with st.sidebar:
        st.header("⚙️ DANE WEJŚCIOWE")
        
        st.subheader("📊 Wyniki Ostatnich Meczów")
        st.caption("Format: 1:1 0:2 2:1 (oddziel spacjami)")
        
        wyniki_gosp = st.text_input("Gospodarze:", "1:1 0:2 2:1 1:0 2:0 2:0")
        wyniki_gosc = st.text_input("Goście:", "2:4 1:1 1:1 1:0 0:2 4:0")
        
        st.subheader("🎯 Wskaźniki Historyczne (%)")
        col1, col2 = st.columns(2)
        with col1:
            btts_gosp = st.slider("Gospodarze BTTS", 0, 100, 33)
            over_gosp = st.slider("Gospodarze Over 2.5", 0, 100, 17)
        with col2:
            btts_gosc = st.slider("Goście BTTS", 0, 100, 80)
            over_gosc = st.slider("Goście Over 2.5", 0, 100, 33)
        
        st.subheader("📈 Wskaźniki xG")
        xg_gosp = st.number_input("Gospodarze xG", value=0.98, step=0.1)
        xg_gosc = st.number_input("Goście xG", value=1.75, step=0.1)
        
        st.subheader("💰 Kursy Bukmachera")
        over_buk = st.number_input("Over 2.5", value=1.82, step=0.01)
        under_buk = st.number_input("Under 2.5", value=1.98, step=0.01)
        btts_tak_buk = st.number_input("BTTS TAK", value=1.70, step=0.01)
        btts_nie_buk = st.number_input("BTTS NIE", value=2.07, step=0.01)
    
    # Główna zawartość
    if st.button("🎯 ROZPOCZNIJ ANALIZĘ", type="primary", use_container_width=True):
        with st.spinner("🔄 Analizuję dane... Proszę czekać"):
            time.sleep(2)
            
            # Konwersja danych
            wyniki_gosp = wyniki_gosp.split()
            wyniki_gosc = wyniki_gosc.split()
            
            # Obliczenia (uproszczone dla demonstracji)
            momentum_gosp = oblicz_momentum(wyniki_gosp)
            momentum_gosc = oblicz_momentum(wyniki_gosc)
            odchylenie_gosp = oblicz_odchylenie_standardowe(wyniki_gosp)
            odchylenie_gosc = oblicz_odchylenie_standardowe(wyniki_gosc)
            
            # Symulacja wyników (TUTAJ WKLEJ SWOJĄ PEŁNĄ LOGIKĘ Z CARNETS)
            over_mecz = 25.5
            btts_mecz = 42.0
            over_value = -53.6
            under_value = 47.6
            btts_tak_value = -28.6
            btts_nie_value = 20.0
            
            # WYŚWIETLANIE WYNIKÓW
            st.success("✅ Analiza zakończona!")
            
            # Karty z wynikami
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 OVER/UNDER 2.5")
                if over_mecz <= 38:
                    st.error(f"UNDER 2.5 - MOCNA REKOMENDACJA")
                    st.metric("Szansa UNDER", f"{100-over_mecz:.1f}%", f"+{under_value:.1f}%")
                elif over_mecz <= 45:
                    st.warning(f"UNDER 2.5 - REKOMENDACJA")
                    st.metric("Szansa UNDER", f"{100-over_mecz:.1f}%", f"+{under_value:.1f}%")
                else:
                    st.info("BRAK CLEAR SIGNAL")
                    st.metric("Szansa OVER", f"{over_mecz:.1f}%", f"{over_value:.1f}%")
            
            with col2:
                st.subheader("🔔 BTTS TAK/NIE")
                if btts_mecz <= 38:
                    st.error(f"BTTS NIE - MOCNA REKOMENDACJA")
                    st.metric("Szansa NIE", f"{100-btts_mecz:.1f}%", f"+{btts_nie_value:.1f}%")
                elif btts_mecz <= 45:
                    st.warning(f"BTTS NIE - REKOMENDACJA")
                    st.metric("Szansa NIE", f"{100-btts_mecz:.1f}%", f"+{btts_nie_value:.1f}%")
                else:
                    st.info("BRAK CLEAR SIGNAL")
                    st.metric("Szansa TAK", f"{btts_mecz:.1f}%", f"{btts_tak_value:.1f}%")
            
            # Szczegółowe statystyki
            with st.expander("📋 SZCZEGÓŁOWE STATYSTYKI"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Momentum Gospodarzy", f"{momentum_gosp:.2f}")
                    st.metric("Odchylenie Gospodarzy", f"{odchylenie_gosp:.2f}")
                with col2:
                    st.metric("Momentum Gości", f"{momentum_gosc:.2f}")
                    st.metric("Odchylenie Gości", f"{odchylenie_gosc:.2f}")
                with col3:
                    st.metric("Suma xG", f"{xg_gosp + xg_gosc:.2f}")
                    st.metric("Potencjał BTTS", f"{(xg_gosp + xg_gosc)/2:.2f}")
            
            # Value Bets
            st.subheader("💎 QUALITY VALUE BETS")
            if under_value > 5 and btts_nie_value > 5:
                st.success("🎯 UNDER 2.5 - DOBRY VALUE BET!")
                st.success("🎯 BTTS NIE - DOBRY VALUE BET!")
                st.info("*Strategia:* Stawiaj 1-3% bankrollu na każdy z tych zakładów")
            else:
                st.warning("⚠️ Brak quality value bets w tym meczu")

if _name_ == "_main_":
    main()
