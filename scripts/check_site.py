from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"
ROBOTS = ROOT / "robots.txt"
WHATSAPP_NUMBER = "573128949710"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.duplicate_ids = set()
        self.hrefs = []
        self.tags = []
        self.h1_count = 0
        self.section_count = 0
        self.whatsapp_count = 0
        self.lang = None
        self.has_viewport = False
        self.has_description = False
        self.has_canonical = False
        self.has_robots_meta = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.tags.append(tag)

        if tag == "html":
            self.lang = values.get("lang")
        if tag == "h1":
            self.h1_count += 1
        if tag == "section":
            self.section_count += 1
        if tag == "meta" and values.get("name") == "viewport":
            self.has_viewport = True
        if tag == "meta" and values.get("name") == "description":
            self.has_description = bool(values.get("content", "").strip())
        if tag == "meta" and values.get("name") == "robots":
            self.has_robots_meta = values.get("content", "").strip().lower() == "index, follow"
        if tag == "link" and values.get("rel") == "canonical":
            self.has_canonical = bool(values.get("href", "").strip())
        if tag == "a" and "href" in values:
            self.hrefs.append(values["href"])
            if values["href"].startswith("https://wa.me/"):
                self.whatsapp_count += 1

        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.add(element_id)
            self.ids.add(element_id)


def fail(errors, message):
    errors.append(message)


def main():
    errors = []

    if not INDEX.exists():
        fail(errors, "No existe index.html.")
    if not SITEMAP.exists():
        fail(errors, "No existe sitemap.xml.")
    if not ROBOTS.exists():
        fail(errors, "No existe robots.txt.")
    if errors:
        return report(errors)

    html = INDEX.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)

    if parser.lang != "es":
        fail(errors, "El documento debe declarar lang=\"es\".")
    if parser.h1_count != 1:
        fail(errors, f"Se esperaba un unico H1; se encontraron {parser.h1_count}.")
    if parser.section_count != 9:
        fail(errors, f"Se esperaban 9 bloques principales; se encontraron {parser.section_count}.")
    if parser.whatsapp_count != 1:
        fail(errors, f"Se esperaba un unico enlace de WhatsApp; se encontraron {parser.whatsapp_count}.")
    if not parser.has_viewport:
        fail(errors, "Falta la metaetiqueta viewport.")
    if not parser.has_description:
        fail(errors, "Falta una meta description valida.")
    if not parser.has_canonical:
        fail(errors, "Falta el enlace canonical.")
    if not parser.has_robots_meta:
        fail(errors, "Falta la metaetiqueta robots con index, follow.")
    if parser.duplicate_ids:
        fail(errors, f"IDs duplicados: {', '.join(sorted(parser.duplicate_ids))}.")

    prohibited_form_tags = {"form", "input", "select", "textarea"}
    found_form_tags = prohibited_form_tags.intersection(parser.tags)
    if found_form_tags:
        fail(errors, f"El sitio no debe recopilar datos. Etiquetas encontradas: {', '.join(sorted(found_form_tags))}.")

    for href in parser.hrefs:
        if href.startswith("#"):
            if href[1:] not in parser.ids:
                fail(errors, f"Enlace interno roto: {href}.")
            continue

        parsed = urlparse(href)
        if parsed.scheme not in {"https"}:
            fail(errors, f"Enlace con esquema no permitido: {href}.")

        if parsed.netloc == "wa.me":
            if parsed.path.strip("/") != WHATSAPP_NUMBER:
                fail(errors, f"Numero de WhatsApp inesperado: {href}.")
            if "text=" not in parsed.query:
                fail(errors, f"Enlace de WhatsApp sin mensaje inicial: {href}.")

    required_texts = [
        "Evaluación inicial: USD 150",
        "Atención presencial y virtual",
        "Método Neurorest",
        "Método Vertex",
        "La página no solicita, almacena ni procesa datos personales",
        "adultos en Colombia",
    ]
    for text in required_texts:
        if text not in html:
            fail(errors, f"Falta contenido requerido: {text}.")

    forbidden_claims = [
        "cura comprobada",
        "tratamiento definitivo",
        "resultados asegurados",
        "éxito garantizado",
    ]
    lower_html = html.lower()
    for claim in forbidden_claims:
        if claim in lower_html:
            fail(errors, f"Afirmacion sanitaria no permitida: {claim}.")

    sitemap = SITEMAP.read_text(encoding="utf-8")
    if "https://hospsiqui-maker.github.io/menteserena/" not in sitemap:
        fail(errors, "El sitemap no contiene la URL publica esperada.")
    if "<lastmod>2026-06-21</lastmod>" not in sitemap:
        fail(errors, "El sitemap no tiene la fecha de actualizacion esperada.")

    robots = ROBOTS.read_text(encoding="utf-8")
    if "User-agent: *" not in robots or "Allow: /" not in robots:
        fail(errors, "robots.txt no permite el rastreo general.")
    if "Sitemap: https://hospsiqui-maker.github.io/menteserena/sitemap.xml" not in robots:
        fail(errors, "robots.txt no apunta al sitemap publico.")

    json_ld_blocks = re.findall(
        r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>',
        html,
        flags=re.DOTALL,
    )
    if len(json_ld_blocks) != 1:
        fail(errors, f"Se esperaba un bloque JSON-LD; se encontraron {len(json_ld_blocks)}.")
    else:
        try:
            structured_data = json.loads(json_ld_blocks[0])
            if structured_data.get("@type") != "MedicalBusiness":
                fail(errors, "El JSON-LD debe describir un MedicalBusiness.")
            if "address" in structured_data:
                fail(errors, "El JSON-LD no debe publicar una direccion no confirmada.")
            if structured_data.get("telephone") != "+57 312 894 9710":
                fail(errors, "El telefono del JSON-LD no coincide con el publicado.")
        except json.JSONDecodeError as exc:
            fail(errors, f"JSON-LD invalido: {exc}.")

    return report(errors)


def report(errors):
    if errors:
        print("VALIDACION FALLIDA")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDACION CORRECTA")
    print("- HTML semantico y SEO basico")
    print("- Enlaces internos")
    print("- Enlaces de WhatsApp")
    print("- Sitio sin formularios ni captura de datos")
    print("- Contenido esencial y sitemap")
    print("- robots.txt y datos estructurados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
