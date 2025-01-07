import PyPDF2
import re
import pandas as pd

def extract_text_from_pdf(file_path):
    """
    Extrae el texto de un archivo PDF.

    :param file_path: Ruta del archivo PDF.
    :return: Texto extraído del archivo PDF.
    """
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
    """
    Limpia el texto eliminando líneas irrelevantes, paginación, separadores y caracteres de salto de línea.

    :param text: Texto extraído del PDF.
    :return: Texto limpio.
    """
    # Expresión regular para eliminar saltos de paginación y líneas irrelevantes
    cleaned_text = re.sub(
        r"(DEPARTAMENTO DE RELATORÍA , AGENDA Y ACTAS[\s\S]*?- \d+ -)|-=o=-", 
        "", 
        text
    )
    # Eliminar espacios en exceso generados por el reemplazo
    cleaned_text = re.sub(r"\n\s*\n", " ", cleaned_text)
    
    # Eliminar todos los caracteres de salto de línea restantes
    cleaned_text = cleaned_text.replace("\n", " ").strip()
    
    return cleaned_text



def pdf_to_vote_list(file_path):
    """
    Recibe el input del archivo PDF y lo transforma a un diccionario:
    Returns dict

    - Diccionario:
    "Nombre de la votación": str
    "A Favor": list
    "En contra": list
    "Abstención": list
    """
    pdf_text = extract_text_from_pdf(file_path)
    cleaned_text = clean_text(pdf_text)
    votaciones_raw = re.findall(r"REGISTRO DIGITAL DE(.*?):(.*?)-", cleaned_text)
    VOTACIONES = []
    for votacion in votaciones_raw:
        votacion_text = votacion[0]+votacion[1]
        titulo_votacion = re.sub(r"REGISTRO DIGITAL DE ","" ,votacion_text.split("CONGRESISTA")[0]).strip()

        VOTACION={}
        VOTACION["Nombre de la votacion"] = titulo_votacion
        for i in range(1, len(votacion_text.split("CONGRESISTA"))):
            if "FAVOR" in votacion_text.split("CONGRESISTA")[i]:
                voto = 1
                try:
                    lista = re.findall(r"([A-Z].*?)(?=[,.]| y )", votacion_text.split("CONGRESISTA")[i].split("FAVOR")[1])
                except:
                    print(votacion_text.split("CONGRESISTA")[i].split(":"))

                VOTACION["A FAVOR"] = lista
            elif "EN CONTRA" in votacion_text.split("CONGRESISTA")[i]:
                voto = -1
                lista = re.findall(r"([A-Z].*?)(?=[,.]| y )", votacion_text.split("CONGRESISTA")[i].split(":")[1])
                VOTACION["EN CONTRA"] = lista
            elif "ABST" in votacion_text.split("CONGRESISTA")[i]:
                voto = 0
                lista = re.findall(r"([A-Z].*?)(?=[,.]| y )", votacion_text.split("CONGRESISTA")[i].split(":")[1][:-2])
                VOTACION["ABSTENCION"] = lista
        VOTACIONES.append(VOTACION)
    return VOTACIONES

def name_to_id(name, Congress):
    names_wo_spaces = dict(enumerate([re.sub(r"[\s*]", "",i.strip()).lower() for i in list(Congress["Congresista"])]))
    #First we account for brothers in Congress
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
        id=42
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
            print(name)
            id = -1
    return id

def transform_votes_to_id(VOTACIONES, Congress):
    for votacion in VOTACIONES:
        if "A FAVOR" in votacion:
            votacion["A FAVOR"] = [name_to_id(re.sub(r"[\s]*?", "", i),Congress) for i in votacion["A FAVOR"]]
        # Check if 'EN CONTRA' key exists before accessing it
        if "EN CONTRA" in votacion:
            votacion["EN CONTRA"] = [name_to_id(re.sub(r"[\s]*?", "", i),Congress) for i in votacion["EN CONTRA"]]
        # Check if 'ABSTENCION' key exists before accessing it
        if "ABSTENCION" in votacion:
            votacion["ABSTENCION"] = [name_to_id(re.sub(r"[\s]*?", "", i),Congress) for i in votacion["ABSTENCION"]]
    return VOTACIONES


def create_vote_dataframe(votaciones, congress_df):
    """
    Creates a pandas DataFrame representing votes, with the congressperson ID as the index.

    Args:
        votaciones: A list of dictionaries, where each dictionary represents a vote.
        congress_df: The DataFrame containing information about congresspeople.

    Returns:
        A pandas DataFrame.
    """
    
    congress_dict = dict(enumerate(congress_df["Congresista"]))

    data = {}

    for vote_data in votaciones:
        vote_name = vote_data["Nombre de la votacion"]
        data[vote_name] = {}

        # Initialize all congresspeople's votes to NaN (missing) for this vote
        for congress_id in congress_dict:
          data[vote_name][congress_id] = 0

        for congress_id in vote_data.get("A FAVOR", []):
            data[vote_name][congress_id] = 1
        for congress_id in vote_data.get("EN CONTRA", []):
            data[vote_name][congress_id] = -1

    df = pd.DataFrame(data)
    df.index = congress_df.index # The indices of congress_df should already be the congressmen's IDs
    return df

# Example usage (assuming you have the 'VOTACIONES' and 'Congress' DataFrames)
# vote_df = create_vote_dataframe(VOTACIONES, Congress)
# vote_df
def pdf_to_vote_df(file_path, Congress):
    return(create_vote_dataframe(transform_votes_to_id(pdf_to_vote_list(file_path), Congress), Congress))
# Ruta del archivo PDF
# if __name__ == "__main__":
#     file_path = r".\ACTAS\06-04.set.2024.pdf"
#     print(pdf_to_vote_list(file_path))
