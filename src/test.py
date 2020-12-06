import pandas as pd

def convert_csv_to_excel(filename):
    csv = pd.read_csv(filename, header=0)
    GFG = pd.ExcelWriter('preprocessing/spss.xlsx')
    csv.to_excel(GFG, index=False)
    GFG.save()

convert_csv_to_excel('preprocessing/spss.csv')