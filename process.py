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

def kata_to_hira(text):
    for c in text:
        if is_katakana(c):
            text = text.replace(c, chr(ord(c)-0x60))
    return text

joyo = OrderedDict()
for line in open("joyo.txt", encoding="utf-8"):
    line = line.strip()
    line = re.sub(r"[ ]?\[[^\]]*\]","",line)
    fields = line.split("\t")
    char = fields[0]
    strokes = int(fields[3])
    grade = fields[4]
    readings_text = fields[7]
    if " " in readings_text:
        print(readings_text)
        a = kavfujwerwe
    readings = readings_text.split("、")
    if len(readings) == 0:
        print(fields[7])
        print(readings_text)
        a = kavfujwerwe
    kun = []
    on = []
    special_kun = []
    special_on = []
    for reading in readings:
        if is_special_on_yomi(reading):
            special_on += [kata_to_hira(reading[1:-1])]
        elif is_on_yomi(reading):
            on += [kata_to_hira(reading)]
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
    if len(kun) == 0 and len(on) == 0 and len(special_kun) == 0 and len(special_on) == 0:
        print(fields[7])
        print(readings_text)
        a = kavfujwerwe
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

for entry in root.iter("character"):
    myentry = OrderedDict()
    char = entry.find("literal").text
    grade = entry.find("misc").find("grade")
    if grade == None:
        grade = "X"
    else:
        grade = grade.text
    strokes = int(entry.find("misc").find("stroke_count").text)
    
    joyo_char = char
    
    if char == "稽":
        strokes = 15
    if char == "餌":
        strokes = 15
    if char == "牙":
        strokes = 4
    if char == "葛":
        strokes = 12
    if char == "僅":
        strokes = 13
    if char == "遡":
        strokes = 14
    if char == "遜":
        strokes = 14
    if char == "賭":
        strokes = 16
    if char == "謎":
        strokes = 17
    if char == "謎":
        strokes = 17
    if char == "餅":
        strokes = 15
    if char == "叱":
        grade = "8"
        joyo_char = "𠮟"
    if char == "𠮟":
        grade = "8"
    if char == "剥":
        grade = "8"
        joyo_char = "剝"
    if char == "剝":
        grade = "8"
    if char == "頬":
        grade = "8"
        joyo_char = "頰"
    if char == "剝":
        grade = "8"
    if char == "填":
        grade = "8"
        joyo_char = "塡"
    if char == "剝":
        grade = "8"
        
    
    myentry["c"] = char
    myentry["g"] = grade
    myentry["s"] = strokes
    
    if joyo_char in joyo:
        f = joyo[joyo_char]
        if strokes != f["s"] and char != "頬":
            print(f"stroke mismatch for {char}")
            print(f"joyo: {f['s']}")
            print(f"kanjidic: {strokes}")
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
    elif grade not in ["9", "10", "X"]:
        print(f"jouyou grade mismatch for {char} ({grade})")
        c = asdfawefasdf
        
    
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