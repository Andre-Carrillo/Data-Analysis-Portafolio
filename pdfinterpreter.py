import PyPDF2
import re


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


# Ruta del archivo PDF
if __name__ == "__main__":
    file_path = r".\ACTAS\06-04.set.2024.pdf"
    print(pdf_to_vote_list(file_path))
