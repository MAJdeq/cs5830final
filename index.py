import requests

API_URL = "https://en.wikipedia.org/w/api.php"

def get_category_members(category, cmtype="page|subcat", limit=500):
    members = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmtype": cmtype,  # Fetch both pages and subcategories
        "cmlimit": limit,
        "format": "json"
    }

    while True:
        response = requests.get(API_URL, params=params)
        data = response.json()
        members.extend(data["query"]["categorymembers"])

        if "continue" in data:
            params.update(data["continue"])
        else:
            break

    return members

def fetch_pages_recursive(category):
    pages = set()
    subcategories = set([category])
    seen_categories = set()

    while subcategories:
        current_category = subcategories.pop()
        print(f"Fetching members of category: {current_category} ({len(seen_categories)}/{len(subcategories) + len(seen_categories)})")
        data = get_category_members(current_category)
        seen_categories.add(current_category)

        for member in data:
            if member["title"] in seen_categories:
                continue
            if member["ns"] == 0:  # Pages
                pages.add(member["title"])
            elif member["ns"] == 1:  # Talk Pages
                pages.add(member["title"][5:])
            elif member["ns"] == 14:  # Subcategories
                subcategories.add(member['title'])

    return pages


for i in ["FA", "GA", "A", "B", "C", "Start", "Stub"]:
    all_pages = fetch_pages_recursive(f"Category:{i}-Class_articles")
    with open(f"{i}.txt", "w") as f:
        f.write("\n".join(all_pages))