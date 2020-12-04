import pandas as pd

def convert_csv_to_excel(filename):
    csv = pd.read_csv(filename, header=0)
    GFG = pd.ExcelWriter('posts.xlsx')
    csv.to_excel(GFG, index=False)
    GFG.save()

convert_csv_to_excel('posts.csv')