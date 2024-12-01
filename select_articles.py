import random

for i in ["FA", "GA", "A", "B", "C", "Start", "Stub"]:
    file = open(f"{i}.txt", "r")
    items = file.read().split("\n")
    file.close()
    random.shuffle(items)
    selected = items[:6000]
    with open(f"{i}_selected.txt", "w") as f:
        f.write("\n".join(selected))