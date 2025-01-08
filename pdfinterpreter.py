import PyPDF2
import re
import pandas as pd
import os

def pdf_to_vote_df(file_path, Congress):
    """
    Debug function that processes a PDF file, extracts voting data, and creates a DataFrame.
    Skips entries where the congressperson ID is -1 and logs processing steps.

    Args:
        file_path: Path to the PDF file.
        Congress: DataFrame containing congressperson data.

    Returns:
        A pandas DataFrame representing votes.
    """

    def extract_text_from_pdf(file_path):
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            return f"Error al procesar el PDF: {e}"

    def clean_text(text):
        cleaned_text = re.sub(
            r"(DEPARTAMENTO DE RELATORÍA , AGENDA Y ACTAS[\s\S]*?- \d+ -)|-=o=-",
            "",
            text
        )
        cleaned_text = re.sub(r"\n\s*\n", " ", cleaned_text)
        cleaned_text = cleaned_text.replace("\n", " ").strip()
        return cleaned_text

    def pdf_to_vote_list(file_path):
        pdf_text = extract_text_from_pdf(file_path)
        cleaned_text = clean_text(pdf_text)
        votaciones_raw = re.findall(r"REGISTRO DIGITAL DE(.*?):(.*?)-", cleaned_text)
        VOTACIONES = []
        for votacion in votaciones_raw:
            votacion_text = votacion[0] + votacion[1]
            titulo_votacion = re.sub(r"REGISTRO DIGITAL DE ", "", votacion_text.split("CONGRESISTA")[0]).strip()

            VOTACION = {}
            VOTACION["Nombre de la votacion"] = titulo_votacion
            for i in range(1, len(votacion_text.split("CONGRESISTA"))):
                if "FAVOR" in votacion_text.split("CONGRESISTA")[i]:
                    lista = re.findall(r"([A-Z].*?)(?=[,.]| y )", votacion_text.split("CONGRESISTA")[i].split("FAVOR")[1])
                    VOTACION["A FAVOR"] = lista
                elif "EN CONTRA" in votacion_text.split("CONGRESISTA")[i]:
                    lista = re.findall(r"([A-Z].*?)(?=[,.]| y )", votacion_text.split("CONGRESISTA")[i].split(":")[1])
                    VOTACION["EN CONTRA"] = lista
                elif "ABST" in votacion_text.split("CONGRESISTA")[i]:
                    lista = re.findall(r"([A-Z].*?)(?=[,.]| y )", votacion_text.split("CONGRESISTA")[i].split(":")[1][:-2])
                    VOTACION["ABSTENCION"] = lista
            VOTACIONES.append(VOTACION)
        return VOTACIONES

    def name_to_id(name, Congress):
        names_wo_spaces = dict(enumerate([re.sub(r"[\s*]", "", i.strip()).lower() for i in list(Congress["Congresista"])]))
        if "Héctor" in name:
            id = 1
        elif "María" in name and "Acuña" in name:
            id = 0
        elif name == "CorderoJonTay":
            id = 32
        elif name == "MaríaCorderoJonTay":
            id = 33
        elif name == "LuisCorderoJonTay":
            id = 32
        elif name == "AlcarrazAgüero":
            id = 4
        elif name == "FloresRuiz":
            id = 49
        elif name == "JeríOré":
            id = 61
        elif name == "RuizRodríguez":
            id = 111
        elif name == "VenturaÁngel":
            id = 128
        elif name == "EchaizdeNúñezIzaga":
            id = 42
        elif name == "JulonIrigoin":
            id = 65
        elif name == "RamirezGarcia":
            id = 104
        else:
            for key, value in names_wo_spaces.items():
                if name.lower() in value:
                    id = key
                    break
            else:
                print(f"Unknown name: {name}")
                id = -1
        return id

    def transform_votes_to_id(VOTACIONES, Congress):
        for votacion in VOTACIONES:
            if "A FAVOR" in votacion:
                votacion["A FAVOR"] = [name_to_id(re.sub(r"[\s]*?", "", i), Congress) for i in votacion["A FAVOR"]]
            if "EN CONTRA" in votacion:
                votacion["EN CONTRA"] = [name_to_id(re.sub(r"[\s]*?", "", i), Congress) for i in votacion["EN CONTRA"]]
            if "ABSTENCION" in votacion:
                votacion["ABSTENCION"] = [name_to_id(re.sub(r"[\s]*?", "", i), Congress) for i in votacion["ABSTENCION"]]
        return VOTACIONES

    def create_vote_dataframe(votaciones, congress_df):
        congress_dict = dict(enumerate(congress_df["Congresista"]))
        data = {}

        for vote_data in votaciones:
            vote_name = vote_data["Nombre de la votacion"]
            data[vote_name] = {}

            for congress_id in congress_dict:
                data[vote_name][congress_id] = 0

            for congress_id in vote_data.get("A FAVOR", []):
                if congress_id != -1:
                    data[vote_name][congress_id] = 1
                else:
                    print(f"Skipping invalid ID in 'A FAVOR': {congress_id}")
            for congress_id in vote_data.get("EN CONTRA", []):
                if congress_id != -1:
                    data[vote_name][congress_id] = -1
                else:
                    print(f"Skipping invalid ID in 'EN CONTRA': {congress_id}")

        df = pd.DataFrame(data)
        df.index = congress_df.index
        return df

    print("Starting PDF to vote DataFrame process...")
    VOTACIONES = pdf_to_vote_list(file_path)
    VOTACIONES = transform_votes_to_id(VOTACIONES, Congress)
    vote_df = create_vote_dataframe(VOTACIONES, Congress)
    print("Process complete.")
    return vote_df
