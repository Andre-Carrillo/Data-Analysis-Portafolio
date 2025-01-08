import PyPDF2
import re
import pandas as pd
def pdfs_to_vote_df_debug(folder_path, Congress):
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
            print(f"Extracting text from PDF: {file_path}...")
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                print(f"Text extraction complete for {file_path}.")
                return text
        except Exception as e:
            print(f"Error during PDF processing for {file_path}: {e}")
            return ""

    def clean_text(text):
        print("Cleaning extracted text...")
        cleaned_text = re.sub(
            r"(DEPARTAMENTO.DE.RELATORÍA.,.AGENDA.Y.ACTAS[\s\S]*?- \d+ -)|-=o=-",
            "",
            text
        )
        cleaned_text = re.sub(r"\n\s*\n", " ", cleaned_text)
        cleaned_text = cleaned_text.replace("\n", " ").strip()
        print("Text cleaning complete.")
        return cleaned_text

    def pdf_to_vote_list(file_path):
        print(f"Converting PDF to vote list for {file_path}...")
        pdf_text = extract_text_from_pdf(file_path)
        if not pdf_text:
            return []
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
                    try:
                        lista = re.findall(r"([A-Z].*?)(?=[,.]| y )", votacion_text.split("CONGRESISTA")[i].split("FAVOR")[1].split(".")[0])
                    except:
                        print(votacion_text.split("CONGRESISTA")[i].split(":"))
                    VOTACION["A FAVOR"] = lista
                elif "EN CONTRA" in votacion_text.split("CONGRESISTA")[i]:
                    lista = re.findall(r"([A-Z].*?)(?=[,.]| y )", votacion_text.split("CONGRESISTA")[i].split(":")[1].split(".")[0]+".")
