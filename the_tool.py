import streamlit as st
import openai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Subsidie Validatie Demo", layout="wide")

st.title("Subsidie aanvraag validatie voor vrijwilligersfeesten")

# Vraag de gebruiker om de OpenAI API sleutel in te voeren
openai_api_key = st.text_input("Voer je OpenAI API sleutel in:", type="password")
if openai_api_key:
    openai.api_key = openai_api_key

# PDF uploaden
uploaded_file = st.file_uploader("Upload je PDF (bijv. activiteiten- of promotieplan)", type=["pdf"])

if uploaded_file is not None:
    try:
        # PDF lezen en tekst extraheren
        reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pdf_text += page_text + "\n"
    except Exception as e:
        st.error(f"Fout bij het lezen van de PDF: {e}")
        pdf_text = ""

    if pdf_text:
        st.subheader("Geëxtraheerde tekst uit de PDF:")
        st.text_area("", pdf_text, height=200)

    # Keuze: Activiteitenplan of Promotieplan
    doc_type = st.radio("Selecteer de documentsoort:", ("Activiteitenplan", "Promotieplan"))

    # Definieer de voorwaarden per documentsoort (Artikel 4) en de algemene voorwaarden (Artikel 5)
    activiteitenplan_conditions = [
        "een omschrijving van de activiteiten.",
        "de eventuele doelgroep(en) waarop de activiteiten gericht zijn;",
        "de start en de einddatum van de activiteiten;",
        "het verwachte aantal deelnemers aan / bezoekers van de activiteiten;",
        "een beschrijving van de wijze waarop de activiteiten bijdragen aan de doelstelling van deze regeling."
    ]

    promotieplan_conditions = [
        "op welke wijze de activiteit onder de aandacht wordt gebracht;",
        "een beschrijving van de manier waarop deelnemers / bezoekers worden geworven."
    ]

    # Algemene voorwaarden (Artikel 5)
    algemene_conditions = [
        "De activiteiten passen binnen de doelstelling van de regeling zoals genoemd in artikel.",
        "De activiteiten worden voornamelijk georganiseerd door vrijwilligers;",
        ("Met de activiteiten (m.u.v. sport en/of culturele evenementen) wordt bijgedragen aan minimaal één van de volgende gemeentelijke beleidseffecten: "
         "De jeugd groeit gezond, veilig en kansrijk op; "
         "Inwoners zijn gezond en ontwikkelen zich naar vermogen; "
         "Inwoners zijn zo zelfredzaam mogelijk en participeren in de samenleving; "
         "Een veilige gemeente om in wonen, te werken en te recreëren.")
    ]

    if st.button("Voorwaarde nalopen"):
        if not openai_api_key:
            st.error("Voer eerst je OpenAI API sleutel in!")
        elif not pdf_text:
            st.error("Geen tekst gevonden in de PDF.")
        else:
            # Kies de voorwaarden op basis van de documentsoort
            if doc_type == "Activiteitenplan":
                conditions_to_check = activiteitenplan_conditions.copy()
            else:
                conditions_to_check = promotieplan_conditions.copy()
            # Voeg de algemene voorwaarden toe
            conditions_to_check.extend(algemene_conditions)

            st.subheader("Resultaten van de validatie:")
            for condition in conditions_to_check:
                # Bouw een prompt per voorwaarde op, met als context de PDF-tekst en de specifieke voorwaarde.
                prompt = (
                    f"Context:\n{pdf_text}\n\n"
                    f"Voorwaarde:\n{condition}\n\n"
                    "Controleer of de voorwaarde aanwezig en voldaan is in de context. Geef een kort en bondig antwoord, "
                    "bijvoorbeeld in de vorm van 'ja' of 'nee' met een korte toelichting."
                )
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Je bent een assistent die subsidie aanvragen controleert."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.0,
                    )
                    answer = response['choices'][0]['message']['content'].strip()
                    st.markdown(f"**Voorwaarde:** {condition}")
                    st.write(f"**Antwoord:** {answer}")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"Fout bij het ophalen van antwoord voor de voorwaarde '{condition}': {e}")
