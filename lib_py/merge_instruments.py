import json
import yaml
from collections import defaultdict, OrderedDict
import pandas as pd

def import_tables():
    tables = dict(
        questionnaires=pd.read_csv("metadata/questionnaires.csv"),
        questions=pd.read_csv("metadata/questions.csv"),
        answers=pd.read_csv("metadata/answers.csv"),
    )
    return tables

def get_answers(tables):
    answers = defaultdict(list)
    for i, answer in tables["answers"].iterrows():
        answer = dict(answer.dropna())
        key = (answer["questionnaire"], answer["answer_list"])
        answers[key].append(answer)
    return answers

def get_instruments(tables):
    instrument_list = [dict(row.dropna()) for i, row in tables["questionnaires"].iterrows()]
    instruments = dict([(x["questionnaire"], x) for x in instrument_list])
    for instrument in instruments.values():
        instrument["instrument"] = instrument["questionnaire"]
        instrument["questions"] = defaultdict(list)
    return instruments

def fill_questions(tables, instruments, answers):
    for i, item in tables["questions"].iterrows():
        item = dict(item.dropna())
        inst_name = item["questionnaire"]
        q_name = item["question"]
        if "item" in item.keys():
            i_name = item["item"]
        else:
            i_name = "root"
        if not inst_name in instruments:
            instruments[inst_name] = dict(
                instrument=inst_name,
                questions=OrderedDict(),
            )
        if not q_name in instruments[inst_name]["questions"]:
            instruments[inst_name]["questions"][q_name] = dict(
                question=q_name,
                items=OrderedDict(),
            )
        try:
            key = (item["questionnaire"], item["answer_list"])
            item["answers"] = answers[key]
        except:
            pass
        instruments[inst_name]["questions"][q_name]["items"][i_name] = item
    return instruments

def export(instruments, export_json=True, export_yaml=False):
    if export_json:
        with open("ddionrails/instruments.json", "w") as f:
            json.dump(instruments, f)
    if export_yaml:
        with open("ddionrails/instruments.yaml", "w") as f:
            yaml.dump(instruments, f, default_flow_style=False)

def main(export_json=True, export_yaml=False):
    tables = import_tables()
    answers = get_answers(tables)
    instruments = get_instruments(tables)
    fill_questions(tables, instruments, answers)
    export(instruments, export_json, export_yaml)
    return instruments

if __name__ == "__main__":
    instruments = main(export_yaml=True)
