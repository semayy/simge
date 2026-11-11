from html import escape
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BASE = "https://simge-soydan-akademik.semdiyar.chatgpt.site"
NAME = "Simge Filoğlu Soydan"
PERSON = BASE + "/#person"
ORCID = "https://orcid.org/0000-0002-5829-1854"
DERGIPARK = "https://dergipark.org.tr/tr/pub/@simge-soydan"
UNIVERSITY = "https://hacibayram.edu.tr/api/files/1/Hac%C4%B1bayram%20AHBV/polatli-myo%28tr-TR%29/2025%20%C3%B6z%20de%C4%9Ferlendirme/Cocuk%20Gelisimi%20Ozdegerlendirme%20Raporu.pdf"
CV = "https://openaccess.ahievran.edu.tr/bitstreams/9913492c-754d-4f4c-a1c4-cf6487f839d6/download"
URLS = {"tr": BASE + "/", "en": BASE + "/en/"}
COPY = json.loads((ROOT / "src/profile.json").read_text())
RECORDS = json.loads((ROOT / "src/publications.json").read_text())
SOURCES = {
    "article": RECORDS[0]["url"], "doctorate": RECORDS[1]["url"],
    "exercises": RECORDS[3]["url"], "masters": RECORDS[4]["url"],
    "university": UNIVERSITY, "cv": CV,
}
TEMPLATE = Template((ROOT / "src/page.html").read_text())


def grid_letters():
    alphabet = "AKTÖÜİVMÇŞENLRUZPĞBYHCDIOS"
    words = {1: (4, "DR."), 4: (2, "SİMGE"), 8: (1, "FİLOĞLU"), 12: (3, "SOYDAN")}
    seed = 1729
    key_index = 0
    cells = []
    for row in range(17):
        start, word = words.get(row, (0, ""))
        for column in range(10):
            seed = (seed * 16807) % 2147483647
            if start <= column < start + len(word):
                letter = word[column - start]
                delay = 170 + key_index * 61 + (row - 1) * 58
                cells.append(f'<span class="key" style="--delay:{delay}ms">{letter}</span>')
                key_index += 1
            else:
                cells.append(f"<span>{alphabet[seed % len(alphabet)]}</span>")
    return "".join(cells)


def record_html(record, lang, labels):
    original = record["lang"]
    title = escape(record[lang])
    native = "" if original == lang else (
        f'<p class="original">{escape(labels["original"])} · '
        f'<span lang="{original}">{escape(record[original])}</span></p>'
    )
    note = record.get("note" + lang.title())
    note_html = f'<p class="record-note">{escape(note)}</p>' if note else ""
    identifier = f'<span class="identifier">{escape(record["identifier"])}</span>' if record.get("identifier") else ""
    return f'''<li class="record" id="{record["id"]}" data-kind="{record["type"]}">
      <div class="record-kind">{escape(record.get("year", ""))}<span>{escape(labels["types"][record["type"]])}</span></div>
      <article><h3>{title}</h3>{native}
        <p class="record-meta">{escape(record["authors"])}<br>{escape(record["venue"])}</p>
        {note_html}{identifier}<a class="source-link" href="{escape(record["url"])}" aria-label="{escape(labels["source"] + ' — ' + record[lang])}">{escape(labels["source"])} <svg class="icon" aria-hidden="true"><use href="#i-external"/></svg></a>
      </article>
    </li>'''



def featured_books(lang):
    assets = {
        "easy-reading-exercises": ("kolay-okuma-egzersizleri", 440, 623),
        "maximum-reading": ("maksimum-okuma-maksimum-algilama", 422, 660),
    }
    cards = []
    for record in RECORDS:
        if record["id"] not in assets:
            continue
        filename, width, height = assets[record["id"]]
        cards.append(f'''<li><a class="book-card" href="#{record["id"]}">
          <span class="book-image"><img src="/images/{filename}.webp" width="{width}" height="{height}" loading="lazy" decoding="async" alt=""></span>
          <span class="book-info"><span class="book-title">{escape(record[lang])}</span>
          <span class="book-publisher">{escape(record["venue"])} <svg class="icon" aria-hidden="true"><use href="#i-down"/></svg></span></span>
        </a></li>''')
    return "".join(cards)


def structured_data(lang, labels):
    work_types = {"article": "ScholarlyArticle", "book": "Book", "thesis": "Thesis", "proceedings": "ScholarlyArticle", "talk": "CreativeWork"}
    items = []
    for position, record in enumerate(RECORDS, 1):
        work = {
            "@type": work_types[record["type"]],
            "name": record[record["lang"]], "inLanguage": record["lang"], "url": record["url"],
        }
        if record["id"] == "pisman-tavuk":
            work["author"] = {"@type": "Person", "name": "Tolga Akpınar"}
            work["editor"] = {"@id": PERSON}
        else:
            work["author"] = [
                {"@id": PERSON} if name in ("Simge Soydan", "Simge Filoğlu") else {"@type": "Person", "name": name}
                for name in record["authors"].split(" · ")
            ]
        if record.get("year"):
            work["datePublished"] = record["year"]
        if record.get("identifier"):
            work["identifier"] = record["identifier"]
        items.append({"@type": "ListItem", "position": position, "item": work})
    data = {"@context": "https://schema.org", "@graph": [
        {"@type": "ProfilePage", "@id": URLS[lang] + "#profile-page", "url": URLS[lang],
         "name": labels["title"], "description": labels["description"], "inLanguage": lang,
         "mainEntity": {"@id": PERSON}},
        {"@type": "Person", "@id": PERSON, "name": NAME, "honorificPrefix": "Dr.",
         "alternateName": ["Simge Soydan", "Simge Filoğlu", "Simge Filoglu Soydan"],
         "jobTitle": labels["role"], "url": URLS["tr"], "description": labels["bio"][0],
         "sameAs": [ORCID, DERGIPARK, "https://www.instagram.com/dr.simgesoydan/"],
         "worksFor": {"@type": "CollegeOrUniversity", "name": "Ankara Hacı Bayram Veli Üniversitesi",
                      "url": "https://hacibayram.edu.tr/"},
         "alumniOf": [{"@type": "CollegeOrUniversity", "name": institution}
                      for institution in ("Ankara Üniversitesi", "Ahi Evran Üniversitesi")],
         "knowsAbout": labels["topics"]},
        {"@type": "ItemList", "@id": URLS[lang] + "#publications", "name": labels["publications"],
         "numberOfItems": len(items), "itemListElement": items},
    ]}
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")


def build_page(lang, labels):
    other = "en" if lang == "tr" else "tr"
    timeline = "".join(
        f'<li><span class="year">{escape(year)}</span><div><h3>{escape(title)}</h3>'
        f'<p>{escape(description)}</p><a class="source-link" href="{escape(SOURCES[source])}">'
        f'{escape(labels["source"])} <svg class="icon" aria-hidden="true"><use href="#i-external"/></svg></a></div></li>'
        for year, title, description, source in labels["timeline"]
    )
    values = {key: escape(value) for key, value in labels.items() if isinstance(value, str)}
    values.update(
        lang=lang, other=other, canonical=URLS[lang], tr_url=URLS["tr"], en_url=URLS["en"],
        other_url="/en/" if other == "en" else "/", other_label="English" if other == "en" else "Türkçe",
        locale="tr_TR" if lang == "tr" else "en_US", name=NAME, orcid=ORCID, dergipark=DERGIPARK,
        university=UNIVERSITY, letters=grid_letters(), timeline=timeline, record_count=len(RECORDS),
        bio="".join(f"<p>{escape(p)}</p>" for p in labels["bio"]),
        topics="".join(f"<li>{escape(topic)}</li>" for topic in labels["topics"]),
        entries="".join(record_html(record, lang, labels) for record in RECORDS),
        book_cards=featured_books(lang),
        types="".join(f'<option value="{key}">{escape(value)}</option>' for key, value in labels["types"].items()),
        schema=structured_data(lang, labels),
    )
    destination = DIST if lang == "tr" else DIST / lang
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(TEMPLATE.substitute(values), encoding="utf-8")


for language, labels in COPY.items():
    build_page(language, labels)

(DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
(DIST / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + "".join(
        f"  <url><loc>{url}</loc>"
        + "".join(f'<xhtml:link rel="alternate" hreflang="{lang}" href="{target}"/>' for lang, target in URLS.items())
        + f'<xhtml:link rel="alternate" hreflang="x-default" href="{URLS["tr"]}"/></url>\n'
        for url in URLS.values()
    ) + "</urlset>\n",
    encoding="utf-8",
)
