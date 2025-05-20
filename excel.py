import pandas as pd


import chardet

with open('./data/raw/data.csv', 'rb') as f:
    result = chardet.detect(f.read())
    print(result)
# Load the CSV file
# df = pd.read_csv("./data/raw/data.csv")

# # Find the halfway point
# half = len(df) // 2

# # Split the dataframe
# df_first_half = df.iloc[:half]
# df_second_half = df.iloc[half:]

# # Save to new CSV files
# df_first_half.to_csv("first_half.csv", index=False)
# df_second_half.to_csv("second_half.csv", index=False)



# import chardet

# with open('your_file.csv', 'rb') as f:
#     result = chardet.detect(f.read())
#     print(result)

# df = pd.read_csv("./data/raw/data.csv")
