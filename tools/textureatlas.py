import xml.etree.ElementTree as ET
import os

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
sprite_xml = ET.parse(CURRENT_PATH+"/../temp/"+input("Enter file name: "))
texture_atlas = sprite_xml.getroot()

with open(CURRENT_PATH+"/../temp/result.txt", "w") as file:
    for texture in texture_atlas:
        name = texture.attrib.get("name").replace(".png","")
        x = texture.attrib.get("x")
        y = texture.attrib.get("y")
        w = texture.attrib.get("width")
        h = texture.attrib.get("height")

        file.write(f"{name} {x} {y} {w} {h}\n")