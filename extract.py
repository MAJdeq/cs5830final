import bz2

print("Reading index...")
index_file = open(f"enwiki-index_selected.txt", "r")
index = index_file.read().split("\n")
index = [x.split(":", 2) for x in index]
index_file.close()

out_file = open("extracted.xml", 'w')

print("Extracting articles...")
multistream = bz2.open("enwiki-multistream.xml.bz2", "rb")
current = 0
found_difference = 0
for i in index:
    title = i[2]
    print(f"{current}/{len(index)} ({title})", end="                                       \r")
    wasted_cycles = 0
    offset_in_block = 0

    page = ""

    while True:
        while "</page>" not in page:
            while "<page>" not in page:
                page = multistream.readline().decode("utf-8")

            page += multistream.readline().decode("utf-8")

        if f"<title>{title}</title>" in page:
            break
        else:
            page = ""

    out_file.write(page)
    current += 1

out_file.close()