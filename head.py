import json

from pyschema import Case
from pydantic import TypeAdapter

Cases = TypeAdapter(list[Case])

d24 = Cases.validate_json(open("2024_cases_fees.json").read())

print(len(d24))

cvg = [c.model_dump(mode="json") for c in d24 if "CVG" in c.case_number]

print(len(cvg))

#json.dump(cvg[:10], open("2024_cases_cvg_head.json","w"))
json.dump(cvg, open("2024_cases_cvg.json","w"))