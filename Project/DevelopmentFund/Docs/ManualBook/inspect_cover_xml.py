import docx
from lxml import etree

doc = docx.Document(r"d:\Work\Source\TestCase_Generator\Project\DevelopmentFund\Manual Book\output\User Manual - DF Overview v1.2.docx")

body_elements = doc._body._body[:]
print(f"Total elements in body: {len(body_elements)}")

cover_elements = []
for elem in body_elements:
    cover_elements.append(elem)
    xml_str = etree.tostring(elem, encoding="utf-8").decode("utf-8")
    if 'w:type="page"' in xml_str or 'w:pageBreakBefore' in xml_str:
        break

print(f"Cover elements count: {len(cover_elements)}")
for i, el in enumerate(cover_elements):
    tag = el.tag.split("}")[-1]
    text = "".join(el.itertext()).strip().replace("\n", " ")
    print(f"[{i:2d}] <{tag}>: {text[:80]}")
