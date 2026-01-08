def clean_data(df):
    df = df.dropna(how="all")
    df = df.drop_duplicates()
    return df
