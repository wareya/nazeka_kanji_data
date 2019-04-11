#!python
from lxml import etree
from collections import OrderedDict
import sys
from io import open
import json
import re

ids = OrderedDict()
for line in open("ids.txt", encoding="utf-8"):
    line = line.strip()
    if not line.startswith("U+"):
        continue
    fields = line.split("\t")[1:]
    c = fields[0]
    decomps = fields[1:]
    composition = ""
    if len(decomps) != 1:
        for decomp in decomps:
            if "J" in decomp:
                composition = re.sub(r"\[[^\]]*\]","",decomp)
    if composition == "":
        composition = re.sub(r"\[[^\]]*\]","",decomps[0])
    ids[c] = composition

def is_katakana(c):
    c = ord(c)
    if c >= 0x30A0 and c <= 0x30FF:
        return True
    else:
        return False

def is_on_yomi(text):
    for c in text:
        if is_katakana(c):
            return True
    return False

def is_special(text):
    if "（" in text:
        return True
    else:
        return False

def is_special_on_yomi(text):
    return is_on_yomi(text) and is_special(text)

joyo = OrderedDict()
for line in open("joyo.txt", encoding="utf-8"):
    line = line.strip()
    fields = line.split("\t")
    char = fields[0]
    strokes = int(fields[3])
    grade = fields[4]
    readings_text = fields[7]
    readings_text = re.sub(r"[ ]?\[[^\]]*\]","",readings_text)
    if " " in readings_text:
        print(readings_text)
        a = kavfujwerwe
    readings = readings_text.split("、")
    kun = []
    on = []
    special_kun = []
    special_on = []
    for reading in readings:
        if is_special_on_yomi(reading):
            special_on += [reading[1:-1]]
        elif is_on_yomi(reading):
            on += [reading]
        elif is_special(reading):
            special_kun += [reading[1:-1]]
        else:
            kun += [reading]
    data = OrderedDict()
    data["s"] = strokes
    data["g"] = grade
    data["k"] = kun
    data["o"] = on
    data["ks"] = special_kun
    data["os"] = special_on
    joyo[char] = data

kanjidic = []

parser = etree.XMLParser(resolve_entities=False)
root = etree.parse("kanjidic2.xml", parser);
for ent in root.iter(etree.Entity):
    if ent.getparent() is not None:
        if not ent.getparent().text:
            ent.getparent().text = ""
        if ent.text:
            ent.getparent().text += ent.text
        if ent.tail:
            ent.getparent().text += ent.tail
root = root.getroot();

# chars with incorrect stroke counts:
# 稽 - 16, should be 15
# there are probably many, MANY others, but this one is in the jouyou kanji.
for entry in root.iter("character"):
    myentry = OrderedDict()
    char = entry.find("literal").text
    grade = entry.find("misc").find("grade")
    if grade == None:
        grade = "X"
    else:
        grade = grade.text
    strokes = int(entry.find("misc").find("stroke_count").text)
    
    if char == "稽":
        strokes = 15
    
    myentry["c"] = char
    myentry["g"] = grade
    myentry["s"] = strokes
    
    if char in joyo:
        f = joyo[char]
        if strokes != f["s"]:
            print(f"stroke mismatch for {char}")
            c = asdfawefasdf
        if f["g"] == "S" and grade != "8":
            print(f"jouyou grade mismatch for {char} ({f['g']} vs {grade})")
        if f["g"] != "S" and f["g"] != grade:
            print(f"kyouiku grade mismatch for {char} ({f['g']} vs {grade})")
        
        if len(f["o"]) > 0:
            myentry["o"] = f["o"]
        if len(f["k"]) > 0:
            myentry["k"] = f["k"]
        if len(f["os"]) > 0:
            myentry["os"] = f["os"]
        if len(f["ks"]) > 0:
            myentry["ks"] = f["ks"]
    
    if char in ids:
        myentry["z"] = ids[char]
    
    kanjidic += [myentry]

f = open("kanjidata.json", "w", newline="\n", encoding="utf-8")
f.write("[\n")
for i, entry in enumerate(kanjidic):
    f.write(json.dumps(entry, ensure_ascii=False))
    if i+1 < len(kanjidic):
        f.write(',')
    f.write('\n')
f.write("]\n")