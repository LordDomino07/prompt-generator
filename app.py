import streamlit as st
import json
import os
import time
from deep_translator import GoogleTranslator
import argostranslate.package
import argostranslate.translate

# Oldal konfiguráció
st.set_page_config(page_title="Prompt Generátor", page_icon="🎨", layout="wide")

st.title("🎨 Képgeneráló Prompt Generátor (JSON sablonokkal)")
st.write("Válaszd ki a sablonokat, vagy írd be szabadon magyarul az egyedi kiegészítést!")

# Argos Translate automatikus előkészítése a háttérben
@st.cache_resource
def init_argos():
    try:
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        installed_packages = argostranslate.package.get_installed_packages()
        
        # Ha még nincs telepítve a hu->en csomag, letöltjük automatikusan
        if not any(p.from_code == "hu" and p.to_code == "en" for p in installed_packages):
            package_to_install = next(
                filter(lambda x: x.from_code == "hu" and x.to_code == "en", available_packages)
            )
            argostranslate.package.install_from_path(package_to_install.download())
    except Exception:
        pass

# Meghívjuk az inicializálást
init_argos()

# JSON adatok betöltése
json_path = "prompts.json"
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    st.error("A 'prompts.json' fájl nem található a mappában! Kérlek, hozd létre.")
    st.stop()

# --- UI ELRENDEZÉS (Két oszlopos kialakítás) ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Alapok és Kompozíció")
    
    sel_ref = st.selectbox("Referencia alap", list(data.get("referencia_alap", {}).keys()))
    sel_hatter = st.selectbox("Háttér környezet", list(data.get("Háttér környezet", {}).keys()))
    sel_haj = st.selectbox("Haj stílus", list(data.get("Haj stílus", {}).keys()))
    sel_kamera_szog = st.selectbox("Kamera szög", list(data.get("kamera szög", {}).keys()))
    sel_poz = st.selectbox("Póz és cselekmény", list(data.get("póz_és_cselekmény", {}).keys()))

with col2:
    st.subheader("🌟 Stílus és Öltözet")
    sel_hangulat = st.selectbox("Hangulat és kisugárzás", list(data.get("hangulat_es_kisugarzas", {}).keys()))
    sel_intenzitas = st.selectbox("Intenzitás szűrő", list(data.get("intenzitas_szuro", {}).keys()))
    sel_evszak = st.selectbox("Évszak", list(data.get("évszakok", {}).keys())) # <-- ÚJ ÉVSZAKOK SELECTBOX
    sel_idojaras = st.selectbox("Időjárás és világítás", list(data.get("időjárás_és_világítás_extra", {}).keys()))
    sel_kamera_beall = st.selectbox("Kamera beállítások", list(data.get("Kamera beállítások", {}).keys()))
    
    st.markdown("---")
    st.markdown("**Ruha és Cipő beállítások:**")
    sel_egybe_ruha = st.selectbox("Egybe ruha szín", list(data.get("Egybe ruha szín", {}).keys()))
    sel_felso = st.selectbox("Felső ruha szín", list(data.get("Felső ruha szín", {}).keys()))
    sel_also = st.selectbox("Alsó ruha szín", list(data.get("Alsó ruha szín", {}).keys()))
    sel_cipo_tipus = st.selectbox("Cipő típus", list(data.get("Cipő típus", {}).keys()))
    sel_cipo_szin = st.selectbox("Cipő szín és anyag", list(data.get("Cipő szín és anyag", {}).keys()))
    sel_oltozet = st.selectbox("Öltözet", list(data.get("Öltözet", {}).keys()))

st.markdown("---")
st.subheader("✍️ Egyedi instrukciók (Magyarul írhatod)")
egyedi_hu = st.text_area("Írd ide szabadon, mit szeretnél még a képre (pl. 'Egy kókuszdiót tart a kezében a parton, miközben mosolyog'):", "")

if st.button("🚀 Prompt Generálása és Fordítása", type="primary"):
    egyedi_en = ""
    if egyedi_hu.strip():
        with st.spinner("Fordítás magyarul angolra..."):
            translated = None
            
            # 1. Próbálkozás a Google Fordítóval
            try:
                time.sleep(0.3)
                translated = GoogleTranslator(source='hu', target='en').translate(egyedi_hu)
            except Exception:
                pass
            
            # 2. Ha a Google nem elérhető, használjuk a beépített helyi Argos motort
            if not translated:
                try:
                    translated = argostranslate.translate.translate(egyedi_hu, "hu", "en")
                except Exception:
                    pass
            
            # 3. Eredmény kezelése
            if translated:
                egyedi_en = translated
                st.success("A fordítás sikeres!")
            else:
                st.warning("⚠️ A fordítás nem sikerült, az eredeti magyar szöveget illesztettük be.")
                egyedi_en = egyedi_hu

    # Összefűzés a JSON értékei alapján
    prompt_elemek = [
        data.get("referencia_alap", {}).get(sel_ref, ""),
        data.get("Háttér környezet", {}).get(sel_hatter, ""),
        data.get("Haj stílus", {}).get(sel_haj, ""),
        data.get("kamera szög", {}).get(sel_kamera_szog, ""),
        data.get("póz_és_cselekmény", {}).get(sel_poz, ""),
        data.get("hangulat_es_kisugarzas", {}).get(sel_hangulat, ""),
        data.get("intenzitas_szuro", {}).get(sel_intenzitas, ""),
        data.get("időjárás_és_világítás_extra", {}).get(sel_idojaras, ""),
        data.get("Kamera beállítások", {}).get(sel_kamera_beall, ""),
        data.get("Egybe ruha szín", {}).get(sel_egybe_ruha, ""),
        data.get("Felső ruha szín", {}).get(sel_felso, ""),
        data.get("Alsó ruha szín", {}).get(sel_also, ""),
        data.get("Cipő típus", {}).get(sel_cipo_tipus, ""),
        data.get("Cipő szín és anyag", {}).get(sel_cipo_szin, ""),
        data.get("Öltözet", {}).get(sel_oltozet, ""),
        egyedi_en
    ]

    # Üres elemek kiszűrése és összefűzése
    vegso_prompt = "\n\n".join([elem for elem in prompt_elemek if elem.strip()])

    st.subheader("📋 Kész Angol Prompt:")
    st.text_area("Másold ki innen:", vegso_prompt, height=220)
    st.success("A prompt sikeresen elkészült!")