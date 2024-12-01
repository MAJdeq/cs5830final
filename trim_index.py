print("reading index")
with open("enwiki-index.txt", "r") as f:
    index = f.read().split("\n")

print("reading selected")
with open("combined_selected.txt", "r") as f:
    selected = f.read().split("\n")
selected = [i.replace("&", "&amp;").replace("\"", "&quot;") for i in selected]
selected = set(selected)

print("trimming index")
trimmed = [x for x in index if x.split(":", 2)[2] in selected]

print("finding disjoint")
trimmed_set = set([x.split(":", 2)[2] for x in trimmed])

for i in selected:
    if i not in trimmed_set:
        print(i)

print("writing index")
with open("enwiki-index_selected.txt", "w") as f:
    f.write("\n".join(trimmed))