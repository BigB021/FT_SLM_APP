import pandas as pd
def dataframe_to_tab_string(df: pd.DataFrame) -> str:
    df = df.fillna("")
 
    def clean(v):
        if isinstance(v, float):
            return str(int(v)) if v.is_integer() else f"{v:g}"
        return str(v).strip()
 
    header_line = "\t".join(str(c).strip() for c in df.columns)
    data_lines = [
        "\t".join(clean(v) for v in row)
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join([header_line] + data_lines) + "\n"