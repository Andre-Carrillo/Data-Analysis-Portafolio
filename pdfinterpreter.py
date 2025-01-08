import PyPDF2
import re
import pandas as pd
import os

def process_pdfs_to_dataframe(folder_path, congress_df, output_csv_path="voting_data.csv"):
    """
    Processes all PDF files in a specified folder, extracts voting data, maps congressperson names to IDs,
    and compiles the data into a Pandas DataFrame saved as a CSV file.

    Args:
        folder_path (str): Path to the folder containing PDF files.
        congress_df (pd.DataFrame): DataFrame containing congressperson information with a 'Congresista' column.
        output_csv_path (str): Path to save the resulting CSV file.

    Returns:
        pd.DataFrame: DataFrame containing all voting data from the PDFs.
    """

    def extract_text_from_pdf(file_path):
        """Extracts text from a PDF file."""
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted
                return text
        except Exception as e:
            print(f"Error processing PDF {file_path}: {e}")
            return ""

    def clean_text(text):
        """Cleans the extracted text by removing irrelevant lines and formatting."""
        # Remove specific irrelevant sections and separators
        cleaned_text = re.sub(
            r"(DEPARTAMENTO DE RELATORÍA , AGENDA Y ACTAS[\s\S]*?- \d+ -)|-=o=-", 
            "", 
            text
        )
        # Replace multiple newlines with a space
        cleaned_text = re.sub(r"\n\s*\n", " ", cleaned_text)
        # Remove remaining newline characters
        cleaned_text = cleaned_text.replace("\n", " ").strip()
        return cleaned_text

    def extract_votaciones(cleaned_text):
        """Extracts raw voting data from the cleaned text."""
        # Regex to find voting records
        votaciones_raw = re.findall(r"REGISTRO DIGITAL DE(.*?):(.*?)-", cleaned_text)
        return votaciones_raw

    def extract_names(section_text, vote_type):
        """Extracts congressperson names from a section of the voting text."""
        # Updated regex to handle names with lowercase letters and diacritics
        name_regex = r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]*?(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]*)*)(?=[,.]| y )"
        return re.findall(name_regex, section_text)

    def name_to_id(name, Congress):
        """Maps a congressperson's name to their ID based on the Congress DataFrame."""
        # Remove spaces and convert to lowercase for matching
        name_clean = re.sub(r"\s+", "", name).lower()
        names_wo_spaces = {v.lower(): k for k, v in enumerate(Congress["Congresista"])}
        
        #Special cases handling
        special_cases = {
            "héctor": 1,
            "maríaacuña": 0,
            "corderojontay": 32,
            "maríacorderojontay": 33,
            "luiscorderojontay": 32,
        }
        
        if name_clean in special_cases:
            return special_cases[name_clean]
        else:
            return names_wo_spaces.get(name_clean, -1)

    def transform_votes_to_id(votaciones, Congress):
        """Transforms vote lists from names to IDs."""
        for votacion in votaciones:
            if "A FAVOR" in votacion:
                votacion["A FAVOR"] = [name_to_id(re.sub(r"\s*", "", name), Congress) for name in votacion["A FAVOR"]]
            if "EN CONTRA" in votacion:
                votacion["EN CONTRA"] = [name_to_id(re.sub(r"\s*", "", name), Congress) for name in votacion["EN CONTRA"]]
            if "ABSTENCION" in votacion:
                votacion["ABSTENCION"] = [name_to_id(re.sub(r"\s*", "", name), Congress) for name in votacion["ABSTENCION"]]
        return votaciones

    def create_vote_dataframe(votaciones, congress_df):
        """Creates a DataFrame representing votes with congressperson IDs."""
        congress_dict = dict(enumerate(congress_df["Congresista"]))
        data = {}

        for vote_data in votaciones:
            vote_name = vote_data["Nombre de la votacion"]
            data[vote_name] = {}

            # Initialize all congresspeople's votes to 0 (missing) for this vote
            for congress_id in congress_dict:
                if congress_id == -1:
                    continue
                data[vote_name][congress_id] = 0

            # Process votes
            for congress_id in vote_data.get("A FAVOR", []):
                if congress_id == -1:
                    continue
                data[vote_name][congress_id] = 1
            for congress_id in vote_data.get("EN CONTRA", []):
                if congress_id == -1:
                    continue
                data[vote_name][congress_id] = -1
            for congress_id in vote_data.get("ABSTENCION", []):
                if congress_id == -1:
                    continue
                data[vote_name][congress_id] = 0  # Abstention is already 0

        df = pd.DataFrame(data).T  # Transpose for better readability
        df.index.name = "Votación"
        df = df.astype(int)  # Ensure all vote values are integers
        return df

    # Initialize list to collect all voting data
    all_votaciones = []

    # Iterate through all PDF files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing: {file_path}")

            # Extract and clean text
            text = extract_text_from_pdf(file_path)
            if not text:
                print(f"No text extracted from {file_path}. Skipping.")
                continue
            cleaned = clean_text(text)

            # Extract voting records
            votaciones_raw = extract_votaciones(cleaned)
            if not votaciones_raw:
                print(f"No voting records found in {file_path}. Skipping.")
                continue

            # Process each voting record
            for votacion in votaciones_raw:
                votacion_text = votacion[0] + votacion[1]
                # Extract the voting title
                titulo_votacion = re.sub(r"REGISTRO DIGITAL DE ", "", votacion_text.split("CONGRESISTA")[0]).strip()

                # Initialize vote dictionary
                VOTACION = {
                    "Nombre de la votacion": titulo_votacion,
                    "A FAVOR": [],
                    "EN CONTRA": [],
                    "ABSTENCION": []
                }

                # Split into sections based on 'CONGRESISTA'
                sections = votacion_text.split("CONGRESISTA")
                for section in sections[1:]:  # Skip the first split part as it's the title
                    if "FAVOR" in section:
                        try:
                            names_text = section.split("FAVOR")[1]
                            names = extract_names(names_text, "FAVOR")
                            VOTACION["A FAVOR"].extend(names)
                        except IndexError:
                            print(f"Warning: 'FAVOR' section malformed in {file_path}.")
                    elif "EN CONTRA" in section:
                        try:
                            names_text = section.split("EN CONTRA")[1]
                            names = extract_names(names_text, "EN CONTRA")
                            VOTACION["EN CONTRA"].extend(names)
                        except IndexError:
                            print(f"Warning: 'EN CONTRA' section malformed in {file_path}.")
                    elif "ABST" in section:
                        try:
                            names_text = section.split("ABST")[1]
                            names = extract_names(names_text, "ABSTENCION")
                            VOTACION["ABSTENCION"].extend(names)
                        except IndexError:
                            print(f"Warning: 'ABSTENCION' section malformed in {file_path}.")

                all_votaciones.append(VOTACION)

    if not all_votaciones:
        print("No voting data extracted from any PDFs.")
        return pd.DataFrame()

    # Transform votes to IDs
    all_votaciones = transform_votes_to_id(all_votaciones, congress_df)

    # Create DataFrame
    voting_df = create_vote_dataframe(all_votaciones, congress_df)

    # Save to CSV
    # try:
    #     voting_df.to_csv(output_csv_path, encoding='utf-8')
    #     print(f"Voting data successfully saved to {output_csv_path}")
    # except Exception as e:
    #     print(f"Error saving DataFrame to CSV: {e}")

    return voting_df