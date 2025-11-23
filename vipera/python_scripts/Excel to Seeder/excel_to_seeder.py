import pandas as pd
import json
import os

def excel_or_csv_to_fixture():
    file_path = input("Enter path to Excel/CSV file (e.g. data.xlsx or data.csv): ").strip()
    model_name = input("Enter Django model name (e.g. cms_hub.category): ").strip()
    pk_column = input("Enter column name to use as primary key (e.g. pk or id): ").strip()
    sheet_to_append = None
    ext = os.path.splitext(file_path)[-1].lower()

    # read file
    if ext == ".csv":
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            print("⚠️ UTF-8 decode failed. Trying with ISO-8859-1 encoding...")
            df = pd.read_csv(file_path, encoding="ISO-8859-1")
    elif ext in [".xls", ".xlsx"]:
        xls = pd.ExcelFile(file_path)
        print(f"📄 Available sheets: {', '.join(xls.sheet_names)}")
        sheet_name = input("Enter sheet name to use: ").strip()
        if sheet_name not in xls.sheet_names:
            print("❌ Sheet name not found.")
            return
        sheet_to_append = sheet_name
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    else:
        print("❌ Unsupported file type.")
        return

    # ----- CLEANING (added) -----
    # normalize column names (strip whitespace)
    df.columns = df.columns.astype(str).str.strip()

    # drop rows that are completely empty
    df = df.dropna(how='all')

    # drop columns that are completely blank/empty (treat NaN or empty-string as blank).
    # but don't accidentally drop the pk column here even if it may have some empties (we'll validate later)
    blank_cols = [
        c for c in df.columns
        if c != pk_column and df[c].fillna('').astype(str).str.strip().eq('').all()
    ]
    if blank_cols:
        df = df.drop(columns=blank_cols)

    # also drop columns that pandas named 'Unnamed: ...' just in case
    unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    # Now ensure pk_column exists after cleaning
    if pk_column not in df.columns:
        print(f"❌ Column '{pk_column}' not found after cleaning. Available columns: {list(df.columns)}")
        return

    # drop rows where pk itself is missing
    df = df.dropna(subset=[pk_column])

    # optional: reset index
    df = df.reset_index(drop=True)
    # ----- end cleaning -----

    fixture_data = []
    for _, row in df.iterrows():
        # build fields dict but SKIP columns where the *value* is empty/NaN
        fields = {}
        for col in df.columns:
            if col == pk_column:
                continue
            val = row[col]

            # skip empty cells (NaN or empty string after stripping)
            if pd.isna(val) or (isinstance(val, str) and val.strip() == ""):
                continue

            if isinstance(val, str):
                clean_val = val.replace("_x000D_", "").replace("\\n", "\n")
                # try parse json-like strings
                try:
                    parsed = json.loads(clean_val)
                    if isinstance(parsed, (dict, list)):
                        fields[col] = parsed
                    else:
                        fields[col] = clean_val
                except json.JSONDecodeError:
                    fields[col] = clean_val
            else:
                fields[col] = val

        # safe pk conversion: if invalid pk, skip row with warning
        pk_value = row[pk_column]
        try:
            pk_int = int(pk_value)
        except (ValueError, TypeError):
            print(f"⚠️ Skipping row with invalid pk: {pk_value!r}")
            continue

        entry = {
            "model": model_name,
            "pk": pk_int,
            "fields": fields
        }
        fixture_data.append(entry)

    fixtures_dir = os.path.join(os.getcwd(), "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)

    base_name = os.path.basename(file_path).rsplit(".", 1)[0]
    filename = f"{base_name}_{sheet_to_append or 'default'}_fixture.json"
    json_path = os.path.join(fixtures_dir, filename)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(fixture_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Fixture created: {json_path}")

if __name__ == "__main__":
    excel_or_csv_to_fixture()
