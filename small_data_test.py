import json
import re
from tqdm import tqdm

from main import ask


# -----------------------------
# 数据加载
# -----------------------------
def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


# -----------------------------
# 答案抽取（关键）
# -----------------------------
def extract_answer(state):
    if not state:
        return ""

    msgs = state.get("messages", [])
    if not msgs:
        return ""

    last = msgs[-1]

    if hasattr(last, "content"):
        text = last.content
    elif isinstance(last, dict):
        text = last.get("content", "")
    else:
        text = str(last)

    # 👉 常见：只取最后一句
    return text.strip().split("\n")[-1]


# -----------------------------
# 规范化（EM关键）
# -----------------------------
def normalize(text):
    if not text:
        return ""

    text = text.lower()

    # 去掉常见前缀
    text = re.sub(r"^(the answer is|answer:|final answer:)\s*", "", text)

    # 去标点
    text = re.sub(r"[^\w\s]", "", text)

    return text.strip()


# -----------------------------
# EM计算
# -----------------------------
def compute_em(pred, gold):
    pred = normalize(pred)

    if isinstance(gold, list):
        golds = [normalize(g) for g in gold]
        return int(pred in golds)

    return int(pred == normalize(gold))


# -----------------------------
# 主评测（实时输出）
# -----------------------------
def run_eval(path, max_samples=None):
    correct = 0
    total = 0

    print("\n🚀 Start streaming evaluation...\n")

    for item in tqdm(load_jsonl(path)):
        if max_samples and total >= max_samples:
            break

        question = item["question"]
        gold = item.get("answers")

        try:
            state = ask(question=question)
            pred = extract_answer(state)
        except Exception as e:
            pred = f"ERROR: {e}"

        score = compute_em(pred, gold)

        total += 1
        correct += score

        acc = correct / total

        # -------------------------
        # 🔥 实时输出
        # -------------------------
        print("\n" + "=" * 60)
        print(f"Q{total}: {question}")
        print(f"Pred: {pred}")
        print(f"Gold: {gold}")
        print(f"EM: {score}")
        print(f"Running Acc: {acc:.4f}")
        print("=" * 60 + "\n")

    print("\n====================")
    print(f"Final Samples: {total}")
    print(f"Final Accuracy: {correct / total:.4f}")
    print("====================\n")


if __name__ == "__main__":
    run_eval("data/nq.jsonl", max_samples=20)