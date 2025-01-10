import PyPDF2
import re
import pandas as pd
import os

def pdfs_to_vote_df(folder_path, Congress):
    """
    Debug function that processes all PDF files in a folder, extracts voting data, and creates a DataFrame.
    Skips entries where the congressperson ID is -1 and logs processing steps.

    Args:
        folder_path: Path to the folder containing PDF files.
        Congress: DataFrame containing congressperson data.

    Returns:
        A pandas DataFrame representing votes, with each column representing a congressperson.
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
            print(f"Error during PDF processing for {file_path}: {e}")
            return ""

    def clean_text(text):
        cleaned_text = re.sub(
            r"(DEPARTAMENTO.DE.RELATORÍA.,.AGENDA.Y.ACTAS[\s\S]*?- \d+ -)|-=o=-",
            "",
            text
        )
        cleaned_text = re.sub(
            r"DEPARTAMENTO[\s\S]*?ACTA",
            "",
            cleaned_text
        )
        cleaned_text = re.sub(
            r"SÁREADEREDACCIÓNDEACTAS",
            "",
            cleaned_text
        )
        cleaned_text = re.sub(
            r"- [0-9]*? -",
            "",
            cleaned_text
        )
        cleaned_text = re.sub(
            r"(?<=erra)([\s]*-[\s]*)(?=Garc)",
            "",
            cleaned_text
        )
        cleaned_text = re.sub(r"\n\s*\n", " ", cleaned_text)
        cleaned_text = cleaned_text.replace("\n", " ").strip()
        return cleaned_text
    
    def pdf_to_vote_list(file_path):
        pdf_text = extract_text_from_pdf(file_path)
        if not pdf_text:
            return []
        cleaned_text = clean_text(pdf_text)
        votaciones_raw = re.findall(r"REGISTRO DIGITAL DE.*?-[\s]*[^Gar]", cleaned_text)
        VOTACIONES = []
        for votacion in votaciones_raw:
            votacion_text = re.sub(r" y ", ",", votacion).strip() #Fix ys
            votacion_text = re.sub(r" Y ", ",", votacion_text).strip()
            votacion_text = re.sub(r"[\s]*", "",votacion_text).strip()
            votacion_text = re.sub(
            r"SÁREADEREDACCIÓNDEACTAS",
            "",
            votacion_text
        )
            
            try:
                titulo_votacion = re.findall(r"(?<=REGISTRO DIGITAL DE ).*?(?=CONG.*?[A-Z][a-z])", votacion)[0].strip()
            except:
                continue
            VOTACION = {}
            VOTACION["Nombre de la votacion"] = titulo_votacion
            for i in range(1, len(votacion_text.split("CONGRESISTA"))):
                if "FAVOR" in votacion_text.split("CONGRESISTA")[i]:
                    try:
                        lista = re.findall(r"([A-Z].*?)(?=[,.])", votacion_text.split("CONGRESISTA")[i].split("FAVOR")[1].split(".")[0]+".")
                        VOTACION["A FAVOR"] = lista
                    except:
                        print(votacion_text.split("CONGRESISTA")[i].split(":"))
                    VOTACION["A FAVOR"] = lista
                elif "CONTRA" in votacion_text.split("CONGRESISTA")[i]:
                    lista = re.findall(r"([A-Z].*?)(?=[,.])", votacion_text.split("CONGRESISTA")[i].split("CONTRA")[1].split(".")[0]+".")
                    VOTACION["EN CONTRA"] = lista
                    
                elif "ABST" in votacion_text.split("CONGRESISTA")[i]:
                    if ":" in votacion_text.split("CONGRESISTA")[i][:-2]:
                        lista = re.findall(r"([A-Z].*?)(?=[,.])", votacion_text.split("CONGRESISTA")[i].split(":")[1].split(".")[0])
                    else:
                        lista = re.findall(r"([A-Z].*?)(?=[,.])", votacion_text.split("CONGRESISTA")[i].split(".")[0])
                    VOTACION["ABSTENCION"] = lista
            VOTACIONES.append((VOTACION, votacion_text))
        return VOTACIONES

    def name_to_id(name, Congress):
        names_wo_spaces = dict(enumerate([re.sub(r"[\s*]|[A-Z](?=[A-Z])", "", i.strip()).lower() for i in list(Congress["Congresista"])]))
 
        if "Héctor" in name or name=="LuisAcuñaPeralta" or name=="H´ctorAcuñaPeralta" or name == "SegundoAcuñaPeralta":
            id = 1
        elif "María" in name and "Acuña" in name:
            id = 0
        elif name == "CorderoJonTay":
            id = 32
        elif name == "MaríaCorderoJonTay":
            id = 33
        elif name == "LuisCorderoJonTay" or name == "LuisLuisCorderoJonTay" or name == "LiusCorderoJonTay" or name== "LuisCorderoJontay":
            id = 32
        elif name == "AlcarrazAgüero":
            id = 4
        elif name == "FloresRuiz" or name=="FloreRuiz" or name == "FloresRuIíz":
            id = 49
        elif name == "JeríOré":
            id = 61
        elif name == "RuizRodríguez" or name == "RuozRodríguez":
            id = 111
        elif name == "VenturaÁngel":
            id = 128
        elif name == "EchaizdeNúñezIzaga" or name == "EchaízdeNuñezIzaga" or name == "EchaízdeNúñezÍzaga":
            id = 42
        elif name == "JulonIrigoin" or name == "JulónIrgoin":
            id = 65
        elif name == "RamirezGarcia":
            id = 104
        elif name == "MaríaCórdovaLobatón":
            id = 34
        elif name == "GarciaCorrea":
            id = 50
        elif name == "BazánCalderon":
            id = 15
        elif name == "GonzálesDelgado" or name == "GonzálezDelgado":
            id = 52
        elif name == "ElíasAvalos":
            id = 45
        elif name == "AndersonRamí0rez":
            id = 9
        elif name == "PalaciosHuáman" or name == "PalaciosHuaman":
            id = 91
        elif name == "Guerra-GarcíaCampos" or name == "GerraGarcíaCampos":
            id = 53
        elif name == "ErnestoBustamante":
            id = 20
        elif name == "CoylaJuárez":
            id = 31
        elif name == "ZeaChoquechabi":
            id = 133
        elif name == "EchavarríaRodríguez":
            id = 43
        elif name == "RivasChácara":
            id = 108
        elif name == "VázquezVela":
            id = 127
        elif name == "PaarionaSinche":
            id = 96
        elif name == "BustamenteDonayre":
            id = 20
        elif name == "GhirinosVenegas":
            id = 29
        elif name == "WilliamzZapata":
            id=130
        elif name == "ZeballosMadariagay":
            id = 135
        elif name == "ViciaVásquez":
            id = 30
        else:
            for key, value in names_wo_spaces.items():
                if name.lower() in value:
                    id = key
                    break
            else:
                id = -1
        return id

    def transform_votes_to_id(VOTACIONES, Congress):
        for votacion in VOTACIONES:
            if "A FAVOR" in votacion[0]:
                votacion[0]["A FAVOR"] = [name_to_id(re.sub(r"[\s]*?", "", i), Congress) for i in votacion[0]["A FAVOR"]]
            if "EN CONTRA" in votacion[0]:
                votacion[0]["EN CONTRA"] = [name_to_id(re.sub(r"[\s]*?", "", i), Congress) for i in votacion[0]["EN CONTRA"]]
            if "ABSTENCION" in votacion[0]:
                votacion[0]["ABSTENCION"] = [name_to_id(re.sub(r"[\s]*?", "", i), Congress) for i in votacion[0]["ABSTENCION"]]

        return [i[0] for i in VOTACIONES]

    def create_vote_dataframe(votaciones, congress_df):
        congress_dict = dict(enumerate(congress_df["Congresista"]))
        data = {}

        for vote_data in votaciones:
            vote_name = vote_data["Nombre de la votacion"]
            data[vote_name] = {}

            for congress_id in congress_dict:
                data[vote_name][congress_id] = 2

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
            for congress_id in vote_data.get("ABSTENCION", []):
                if congress_id != -1:
                    data[vote_name][congress_id] = 0
                else:
                    print(f"Skipping invalid ID in 'EN ABSTENCION': {congress_id}")

        df = pd.DataFrame(data)
        df.index = congress_df.index
        print(df.size)
        return df

    print("Starting PDF to vote DataFrame process...")
    all_votaciones = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            votaciones = pdf_to_vote_list(file_path)
            votaciones = transform_votes_to_id(votaciones, Congress)
            all_votaciones.extend(votaciones)
            print(f"Processing file: {file_name}")

    vote_df = create_vote_dataframe(all_votaciones, Congress)
    print("All files processed. Final DataFrame created.")
    return vote_df

