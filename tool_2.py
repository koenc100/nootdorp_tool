import streamlit as st
import os
import base64
import PyPDF2
from openai import OpenAI

# Initialiseer de OpenAI client met je API-key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def display_pdf(file):
    """
    Converteert de geüploade PDF naar base64 en toont deze in een iframe.
    """
    pdf_bytes = file.read()
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    file.seek(0)

def extract_pdf_text(file):
    """
    Extraheert alle tekst uit de geüploade PDF met PyPDF2.
    """
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    file.seek(0)
    return text

def check_prompt(prompt_type, pdf_text, verbosity):
    """
    Stuurt de juiste prompt naar de OpenAI API, afhankelijk van het gekozen prompt_type en de uitgebreidheid (verbosity).
    """
    if prompt_type == "activiteitenplan_Artikel4":
        if verbosity.lower() == "bondig":
            prompt = f"""[Bondige versie]:
Activiteitenplan:
- Beschrijving van activiteiten, doelgroep, start-/einddatum, aantal deelnemers en bijdrage aanwezig?
Geef een kort antwoord: Voldoet de data aan de voorwaarden?
PDF-tekst:
{pdf_text}"""
        elif verbosity.lower() == "normaal":
            prompt = f"""Controleer in dit ACTIVITEITENPLAN of de tekst bevat:
- Activiteitenbeschrijving, doelgroep, start-/einddatum, aantal deelnemers en bijdrage aan regelgeving.
Geef een beknopte analyse: Voldoen de gegevens aan de voorwaarden?
PDF-tekst:
{pdf_text}"""
        else:  # uitgebreid
            prompt = f"""Je krijgt de tekst van een PDF die een ACTIVITEITENPLAN betreft.
Controleer of de volgende elementen gedetailleerd omschreven zijn:
1. Een uitgebreide beschrijving van de activiteiten.
2. Een duidelijke vermelding van de (mogelijke) doelgroep(en).
3. Precieze start- en einddatum.
4. Een verwacht aantal deelnemers/bezoekers met toelichting.
5. Een uitgebreide uitleg over de bijdrage aan de regelgeving.
Geef vervolgens een uitgebreide analyse en conclusie.
PDF-tekst:
{pdf_text}"""
    elif prompt_type == "promotieplan_Artikel4":
        if verbosity.lower() == "bondig":
            prompt = f"""[Bondige versie]:
Promotieplan:
- Wordt de activiteit effectief onder de aandacht gebracht en wordt de werving duidelijk omschreven?
Geef een kort antwoord: Voldoet de data aan de voorwaarden?
PDF-tekst:
{pdf_text}"""
        elif verbosity.lower() == "normaal":
            prompt = f"""Controleer in dit PROMOTIEPLAN of de tekst bevat:
- Hoe de activiteit onder de aandacht wordt gebracht en hoe werving plaatsvindt.
Geef een beknopte analyse: Voldoen de gegevens aan de voorwaarden?
PDF-tekst:
{pdf_text}"""
        else:  # uitgebreid
            prompt = f"""Je krijgt de tekst van een PDF die een PROMOTIEPLAN betreft.
Controleer of de volgende elementen gedetailleerd omschreven zijn:
1. Een duidelijke omschrijving van hoe de activiteit onder de aandacht wordt gebracht.
2. Een uitgebreide toelichting op de wervingswijze.
Geef vervolgens een uitgebreide analyse en conclusie.
PDF-tekst:
{pdf_text}"""
    elif prompt_type == "activiteitenplan_Artikel5":
        if verbosity.lower() == "bondig":
            prompt = f"""[Bondige versie]:
Activiteitenplan:
- Passen de activiteiten binnen de regelgeving, worden ze door vrijwilligers uitgevoerd en dragen ze bij aan gemeentelijke doelstellingen (gezond, participatie, veilig)?
Geef een kort antwoord: Voldoet de data aan de voorwaarden?
PDF-tekst:
{pdf_text}"""
        elif verbosity.lower() == "normaal":
            prompt = f"""Controleer in dit ACTIVITEITENPLAN of de tekst bevat:
- Of de activiteiten passen binnen de regelgeving.
- Of ze door vrijwilligers worden uitgevoerd.
- Of ze bijdragen aan gemeentelijke doelstellingen (gezond, participatie, veilig).
Geef een beknopte analyse: Voldoen de gegevens aan de voorwaarden?
PDF-tekst:
{pdf_text}"""
        else:  # uitgebreid
            prompt = f"""Je krijgt de tekst van een PDF die een ACTIVITEITENPLAN betreft.
Controleer of de volgende elementen gedetailleerd omschreven zijn:
1. Of de activiteiten nauwkeurig passen binnen de regelgeving.
2. Of de activiteiten worden uitgevoerd door vrijwilligers, met toelichting.
3. Of de activiteiten op een uitgebreide wijze bijdragen aan ten minste één van de volgende gemeentelijke doelstellingen:
   - Gezonde en zelfstandige inwoners.
   - Inwonersparticipatie.
   - Een veilige leefomgeving.
Geef vervolgens een uitgebreide analyse en conclusie.
PDF-tekst:
{pdf_text}"""
    else:
        prompt = "Onbekend prompt type."

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content

def main_page():
    st.title("Subsidie Formulier Checker Demo")
    st.write("Upload een PDF, kies het documenttype, selecteer de uitgebreidheid van de prompt en voer de gewenste check uit.")

    uploaded_file = st.file_uploader("Upload je PDF", type=["pdf"])
    if uploaded_file is not None:
        doc_type = st.radio("Selecteer het documenttype:", ("activiteitenplan", "promotie plan"))
        st.write("Documenttype:", doc_type)

        verbosity = st.select_slider("Kies de uitgebreidheid van de prompt:", options=["Bondig", "Normaal", "Uitgebreid"])
        st.write("Uitgebreidheidsniveau:", verbosity)

        pdf_text = extract_pdf_text(uploaded_file)

        st.markdown(
            """
            <style>
            div.stButton > button {
                height: 3em;
                width: 220px;
                font-size:18px;
            }
            </style>
            """, unsafe_allow_html=True
        )

        st.write("### Kies een check:")
        col1, col2, col3 = st.columns(3)
        result = None

        with col1:
            if st.button("Check Actp. Artikel 4", disabled=(doc_type == "promotie plan")):
                result = check_prompt("activiteitenplan_Artikel4", pdf_text, verbosity)
        with col2:
            if st.button("Check Promo. Artikel 4", disabled=(doc_type == "activiteitenplan")):
                result = check_prompt("promotieplan_Artikel4", pdf_text, verbosity)
        with col3:
            if st.button("Check Actp. Artikel 5", disabled=(doc_type == "promotie plan")):
                result = check_prompt("activiteitenplan_Artikel5", pdf_text, verbosity)

        if result:
            st.subheader("Analyse Resultaat")
            st.write(result)

        st.subheader("Geüploade PDF")
        display_pdf(uploaded_file)

    # Knop om naar de informatiepagina te gaan
    if st.button("Meer Informatie Checks"):
        st.session_state.current_page = "info"

def info_page():
    st.title("Meer Informatie over de Checks")

    # Artikel 4 en 5 zoals in het plaatje
    st.markdown("## Artikel 4")
    st.markdown("**Activiteitenplan**:")
    st.markdown("""
- een omschrijving van de activiteiten.
- de eventuele doelgroep(en) waarop de activiteiten gericht zijn;
- de start en de einddatum van de activiteiten;
- het verwachte aantal deelnemers aan / bezoekers van de activiteiten;
- een beschrijving van de wijze waarop de activiteiten bijdragen aan de doelstelling van deze regeling.
    """)
    st.markdown("**Promotieplan**:")
    st.markdown("""
- op welke wijze de activiteit onder de aandacht wordt gebracht;
- een beschrijving van de manier waarop deelnemers / bezoekers worden geworven.
    """)

    st.markdown("## Artikel 5")
    st.markdown("""
1. De activiteiten passen binnen de doelstelling van de regeling zoals genoemd in artikel.
2. De activiteiten worden voornamelijk georganiseerd door vrijwilligers;
3. Met de activiteiten (m.u.v. sport en/of culturele evenementen) wordt bijgedragen aan minimaal één van de volgende gemeentelijke beleidsdoelstellingen:
   - Collectieve en individuele zelfredzaamheid;
   - Inwoners zijn gezond, veilig en kansrijk op;
   - Inwoners nemen verantwoordelijkheid in de samenleving;
   - Een veilige gemeenschap om in te wonen, te werken en te recreëren.
    """)

    # Link naar de officiële pagina
    st.markdown("Bekijk de volledige artikelen via [deze link](https://lokaleregelgeving.overheid.nl/CVDR601326/2#artikel_4).")

    st.markdown("### Overzicht van de Checks")
    table_markdown = """
| **Document**         | **Artikel** | **Voorwaarden te controleren**                                                                                                                                          |
|----------------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Activiteitenplan** | **Artikel 4** | - Beschrijving van de activiteiten <br> - Doelgroep(en) <br> - Start-/einddatum <br> - Aantal deelnemers/bezoekers <br> - Bijdrage aan de doelstelling van de regeling |
| **Promotieplan**     | **Artikel 4** | - Onder de aandacht brengen <br> - Werving van deelnemers/bezoekers                                                                                                      |
| **Activiteitenplan** | **Artikel 5** | - Passen binnen de doelstelling <br> - Uitgevoerd door vrijwilligers <br> - Bijdrage aan gemeentelijke doelstellingen (gezond, participatie, veilig)                   |
"""
    st.markdown(table_markdown, unsafe_allow_html=True)

    # Flowchart-afbeelding onderaan de pagina
    st.image("flow_LLM.png", caption="Overzicht van de flow (voorwaarde + context -> prompt -> LLM -> output)")

    if st.button("Terug naar Checks"):
        st.session_state.current_page = "main"

# Zorg dat de huidige pagina wordt bijgehouden in de session_state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "main"

if st.session_state.current_page == "main":
    main_page()
elif st.session_state.current_page == "info":
    info_page()
