import json
import re

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

def indent_level(line):
    return line.count("│")

def clean_line(line):
    line = line.strip()
    line = line.replace("├──", "").replace("└──", "")
    line = re.sub(r":[a-z_]+:", "", line)  # remove emojis
    line = line.replace("**", "")
    return line.strip()

def parse_tree(filename):
    root = {}
    stack = [(-1, root)]

    with open(filename, encoding="utf-8") as f:
        for raw in f:
            if "[" not in raw:
                continue

            level = indent_level(raw)
            line = clean_line(raw)

            match = LINK_RE.search(line)
            if not match:
                continue

            title, link = match.groups()

            while stack and stack[-1][0] >= level:
                stack.pop()

            parent = stack[-1][1]

            node = {
                "title": title,
                "link": link,
                "children": {}
            }

            parent[title] = node
            stack.append((level, node["children"]))

    return root


data = parse_tree("data.txt")

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✔ Parsed successfully")
