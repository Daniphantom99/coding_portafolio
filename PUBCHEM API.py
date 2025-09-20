import requests
import pandas as pd
import urllib.parse
import time

pd.set_option('display.max_columns', None)

#Your list
smiles= ["CC(=O)OC1=CC=CC=C1C(=O)O"]

def get_cid(smiles):
    try:
        smiles_encoded = urllib.parse.quote(smiles)
        url_cid = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{smiles_encoded}/cids/JSON"
        r = requests.get(url_cid)
        r.raise_for_status()
        data = r.json()
        cids = data.get("IdentifierList", {}).get("CID", [])
        if cids:
            return cids[0]
        else:
            print(f"No CID found for SMILES: {smiles}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting CID for SMILES {smiles}: {e}")
        return None


def get_activity_for_cid(cid):
    url_summary = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/assaysummary/JSON"
    try:
        r = requests.get(url_summary)
        r.raise_for_status()
        data = r.json()

        rows = data.get("Table", {}).get("Row", [])
        if not rows:
            print(f"No assay summary found for CID: {cid}")
            return pd.DataFrame()

        results = []
        for row in rows:
            cells = row.get("Cell", [])
            if len(cells) >= 11:
                results.append({
                    "CID": cid,
                    "AID": cells[0],
                    "Assay_Name": cells[9],
                    "Assay_Type": cells[10],
                    "Activity_Outcome": cells[4],
                    "Description": cells[2]
                })
        return pd.DataFrame(results)

    except requests.exceptions.RequestException as e:
        print(f"Error getting assay summary for CID {cid}: {e}")
        return pd.DataFrame()


def get_activity_from_list(smiles_list):
    all_results = []
    for i, smi in enumerate(smiles_list):
        print(f"Processing SMILES {i + 1}/{len(smiles_list)}: {smi}")

        cid = get_cid(smi)

        if cid:
            df = get_activity_for_cid(cid)
            if not df.empty:
                df['SMILES'] = smi
                all_results.append(df)
        time.sleep(0.5)


    if all_results:
        final = pd.concat(all_results, ignore_index=True)
        final.to_csv("Activity.csv", index = False)
        print(final)
        return final
    else:
        return pd.DataFrame()

get_activity_from_list(smiles)









