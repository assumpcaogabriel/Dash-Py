import os
import requests
from datetime import datetime
from typing import List

# Leitura de variáveis de ambiente (pode ser substituído por st.secrets no Streamlit Cloud)
AZURE_ORG = os.getenv("radixeng")
AZURE_PROJECT = os.getenv("Technos_Evolução")
AZURE_PAT = os.getenv("4l0nRtUdc8bTtPvuZC9CACpTkcIIx7IBaQiJHNUANHanixsz8Am2JQQJ99BCACAAAAAQMXV9AAASAZDO22ny")

def get_auth():
    return ("", AZURE_PAT)

def get_teams():
    url = f"https://dev.azure.com/{AZURE_ORG}/_apis/projects/{AZURE_PROJECT}/teams?api-version=7.0"
    res = requests.get(url, auth=get_auth())
    res.raise_for_status()
    return res.json()["value"]

def get_iterations(team_name: str):
    url = f"https://dev.azure.com/{AZURE_ORG}/{AZURE_PROJECT}/{team_name}/_apis/work/teamsettings/iterations?api-version=7.0"
    res = requests.get(url, auth=get_auth())
    res.raise_for_status()
    return res.json()["value"]

def filter_iterations_by_date(iterations, start, end):
    result = []
    for it in iterations:
        if "attributes" in it and "startDate" in it["attributes"] and "finishDate" in it["attributes"]:
            sd = datetime.strptime(it["attributes"]["startDate"], "%Y-%m-%dT%H:%M:%SZ").date()
            fd = datetime.strptime(it["attributes"]["finishDate"], "%Y-%m-%dT%H:%M:%SZ").date()
            if sd <= end and fd >= start:
                result.append(it)
    return result

def get_work_items_by_iteration(team_name: str, iteration_path: str) -> List[int]:
    url = f"https://dev.azure.com/{AZURE_ORG}/{AZURE_PROJECT}/{team_name}/_apis/work/teamsettings/iterations/{iteration_path}/workitems?api-version=7.0"
    res = requests.get(url, auth=get_auth())
    res.raise_for_status()
    return [item["id"] for item in res.json()["workItemRelations"]]

def get_work_items_details(ids: List[int]):
    chunks = [ids[i:i+200] for i in range(0, len(ids), 200)]
    all_items = []
    for chunk in chunks:
        ids_str = ",".join(map(str, chunk))
        url = f"https://dev.azure.com/{AZURE_ORG}/{AZURE_PROJECT}/_apis/wit/workitems?ids={ids_str}&$expand=all&api-version=7.0"
        res = requests.get(url, auth=get_auth())
        res.raise_for_status()
        all_items.extend(res.json()["value"])
    return all_items

def parse_work_items(raw_items):
    parsed = []
    for item in raw_items:
        fields = item["fields"]
        parsed.append({
            "ID": str(item["id"]),
            "Titulo": fields.get("System.Title", ""),
            "Tipo": fields.get("System.WorkItemType", ""),
            "Estado": fields.get("System.State", ""),
            "Responsavel": fields.get("System.AssignedTo", {}).get("displayName") if isinstance(fields.get("System.AssignedTo"), dict) else None,
            "Parent": str(fields.get("System.Parent", "")) if "System.Parent" in fields else None,
            "IterationPath": fields.get("System.IterationPath", ""),
            "Tamanho": fields.get("Microsoft.VSTS.Scheduling.TShirtSize", "")
        })
    return parsed