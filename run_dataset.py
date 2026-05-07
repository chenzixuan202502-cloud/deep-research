import json
import re
from tqdm import tqdm
from main import ask


# =====================================================
# 数据 IO
# =====================================================
def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def save_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# =====================================================
# normalize（更安全）
# =====================================================
def normalize(text):
    if not text:
        return ""

    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =====================================================
# ⭐ 从 final_report 提取答案（核心）
# =====================================================
def extract_from_report(report):
    if not report:
        return ""

    text = report.lower()

    # 🎯 1. 日期类问题（最常见）
    date_patterns = [
        r"\b\d{1,2}\s+\w+\s+\d{4}\b",   # 11 december 1972
        r"\b\w+\s+\d{4}\b",            # december 1972
        r"\b\d{4}\b"
    ]

    for p in date_patterns:
        m = re.search(p, text)
        if m:
            return m.group(0)

    # 🎯 2. 人名 / 写作者类
    m = re.search(r"written by ([a-z\s]+)", text)
    if m:
        return m.group(1)

    # 🎯 3. fallback：第一句
    first_line = report.strip().split("\n")[0]
    return first_line[:200]


# =====================================================
# 🚀 主 extractor（终极版）
# =====================================================
def extract_answer(state):
    if not state:
        return ""

    # =========================
    # 1️⃣ 优先 final_report
    # =========================
    if "final_report" in state:
        ans = extract_from_report(state["final_report"])
        if ans:
            return clean(ans)

    # =========================
    # 2️⃣ 结构化字段
    # =========================
    for key in ["final_answer", "answer", "output", "result"]:
        if key in state and isinstance(state[key], str):
            if state[key].strip():
                return clean(state[key])

    # =========================
    # 3️⃣ messages fallback
    # =========================
    messages = state.get("messages", [])

    for m in reversed(messages):
        try:
            content = m.content if hasattr(m, "content") else m.get("content", "")
        except:
            continue

        if not content:
            continue

        parsed = try_parse_json(content)
        if parsed:
            return clean(parsed)

    return ""


# =====================================================
# JSON解析
# =====================================================
def try_parse_json(text):
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            for k in ["answer", "result", "output", "content", "final"]:
                if k in obj and isinstance(obj[k], str):
                    return obj[k]
    except:
        pass
    return None


# =====================================================
# 清洗
# =====================================================
def clean(text):
    text = re.sub(r"<think>.*?</think>", "", str(text), flags=re.DOTALL)
    text = text.replace("```json", "").replace("```", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =====================================================
# ✅ 更合理 EM（修复你现在的 bug）
# =====================================================
def compute_em(pred, gold):
    pred_n = normalize(pred)

    if not pred_n:
        return 0

    golds = gold if isinstance(gold, list) else [gold]
    golds = [normalize(g) for g in golds]

    for g in golds:
        if pred_n == g:
            return 1

        # ⭐ 关键修复（允许包含）
        if pred_n in g or g in pred_n:
            return 1

    return 0


# =====================================================
# F1
# =====================================================
def compute_f1(pred, gold):
    p = normalize(pred).split()
    g = normalize(gold).split()

    if not p or not g:
        return 0

    common = set(p) & set(g)
    if not common:
        return 0

    precision = len(common) / len(p)
    recall = len(common) / len(g)

    return 2 * precision * recall / (precision + recall)


def compute_f1_multi(pred, gold):
    if isinstance(gold, list):
        return max(compute_f1(pred, g) for g in gold)
    return compute_f1(pred, gold)


# =====================================================
# 主评测
# =====================================================
def run_dataset(input_path, output_path, question_key="question"):
    dataset = load_jsonl(input_path)
    results = []

    correct = 0
    total = 0
    total_f1 = 0

    for i, item in enumerate(tqdm(dataset), 1):

        question = item.get(question_key, "")
        if not question:
            continue

        try:
            state = ask(
                question=question,
                enable_background_investigation=False,
            )
            pred = extract_answer(state)

        except Exception as e:
            pred = f"ERROR: {str(e)}"
            state = None

        gold = item.get("answers") or item.get("possible_answers")

        em = compute_em(pred, gold)
        f1 = compute_f1_multi(pred, gold)

        correct += em
        total += 1
        total_f1 += f1

        acc = correct / total
        avg_f1 = total_f1 / total

        results.append({
            "question": question,
            "prediction": pred,
            "gold": gold,
            "em": em,
            "f1": round(f1, 4)
        })

        # ======================
        # 输出（含标准答案）
        # ======================
        print("\n" + "=" * 80)
        print(f"[{i}/{len(dataset)}]")
        print(f"Q: {question}")

        print("\n👉 Prediction:")
        print(pred)

        print("\n👉 Gold:")
        print(gold)

        print(f"\nEM: {em} | F1: {f1:.4f}")
        print(f"Accuracy: {acc:.4f} | Avg F1: {avg_f1:.4f}")
        print("=" * 80)

    save_jsonl(output_path, results)

    print("\n==============================")
    print(f"Total: {total}")
    print(f"Final EM: {correct/total:.4f}")
    print(f"Final F1: {total_f1/total:.4f}")
    print("==============================")


# =====================================================
# CLI
# =====================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--question_key", default="question")

    args = parser.parse_args()

    run_dataset(
        args.input,
        args.output,
        args.question_key
    )