from datasets import load_dataset
import json

print("loading dataset...")

ds = load_dataset("nq_open")

print(ds)

split = "validation" if "validation" in ds else list(ds.keys())[0]

print("using split:", split)

with open("data/nq.jsonl", "w") as f:
    for i, x in enumerate(ds[split]):
        f.write(json.dumps({
            "question": x["question"],
            "answers": x["answer"]
        }) + "\n")

print("done")