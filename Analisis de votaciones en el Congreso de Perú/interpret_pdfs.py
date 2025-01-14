from pdfinterpreter import pdfs_to_vote_df
import pandas as pd
 
folders = ["1.4.1", "1.2.3", "1.4.2", "1.3.2", "1.3.1", "1.2.2", "1.2.1", "1.1.1"]

votes = [pdfs_to_vote_df(f"./ACTAS/{folder}", pd.read_csv("Congreso.csv", index_col=0)) for folder in folders]
votes_deleted_corrupted = [vote.loc[:, (vote != 0).any(axis=0)] for vote in votes]

votes_2 = dict(zip(folders, votes_deleted_corrupted))

for name, vote in votes_2.items():
    vote.to_csv(name+".csv")