#!/usr/bin/env python3
"""Generador de Aerotermia Clara.

Lee los textos de contenido/ y crea la web completa en docs/.
Uso:  python3 build.py
No necesita instalar nada: solo Python 3.
"""
import html
import json
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------- Ajustes
DOMINIO = "https://aerotermiaclara.es"   # sin barra final
MARCA = "Aerotermia Clara"
TITULAR = "Wanderson Badaro"
CORREO = "hola@aerotermiaclara.es"        # cámbialo por el correo real
ADSENSE_ID = ""                           # p. ej. "ca-pub-1234567890123456" cuando AdSense apruebe la web

RAIZ = Path(__file__).parent
CONT = RAIZ / "contenido"
EST = RAIZ / "estatico"
SAL = RAIZ / "docs"

CATEGORIAS = [
    ("precios", "Precios"),
    ("ayudas", "Ayudas"),
    ("comparativas", "Comparativas"),
    ("marcas", "Marcas"),
    ("instalacion", "Instalación"),
    ("consumo", "Consumo"),
    ("guia", "Guía básica"),
    ("problemas", "Problemas"),
]
NOMBRE_CAT = dict(CATEGORIAS)
MENU = [c for c in CATEGORIAS if c[0] != "guia"] + [("calculadora", "Calculadora")]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_larga(iso):
    a, m, d = iso.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {a}"


def leer(ruta):
    """Devuelve (metadatos, cuerpo). Cabecera 'clave: valor' hasta la línea '---'."""
    texto = ruta.read_text(encoding="utf-8")
    cab, _, cuerpo = texto.partition("\n---\n")
    meta = {"faq": []}
    for linea in cab.splitlines():
        if not linea.strip():
            continue
        clave, _, valor = linea.partition(":")
        clave, valor = clave.strip(), valor.strip()
        if clave == "faq":
            p, _, r = valor.partition("|")
            meta["faq"].append((p.strip(), r.strip()))
        else:
            meta[clave] = valor
    return meta, cuerpo.strip()


def url_de(meta):
    tipo = meta.get("tipo", "articulo")
    if tipo == "home":
        return "/"
    if tipo == "pilar":
        return f"/{meta['cat']}/"
    if tipo == "pagina":
        return f"/{meta['slug']}/"
    return f"/{meta['cat']}/{meta['slug']}/"


def relativizar(codigo, url):
    """Convierte los enlaces internos '/x/' en relativos, para que la web
    funcione igual en aerotermiaclara.es y en usuario.github.io/repositorio/."""
    prof = len([p for p in url.split("/") if p])
    pref = "../" * prof or "./"
    return re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{pref}', codigo)


def anuncio(nombre):
    if not ADSENSE_ID:
        return f"<!-- hueco de anuncio: {nombre} -->"
    return (f'<div class="anuncio"><ins class="adsbygoogle" style="display:block" '
            f'data-ad-client="{ADSENSE_ID}" data-ad-format="auto" '
            f'data-full-width-responsive="true"></ins>'
            f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>')


def meter_anuncios(cuerpo):
    """Anuncio tras el 2.º párrafo y antes del 3.er y 5.º <h2>."""
    partes = cuerpo.split("</p>", 2)
    if len(partes) == 3:
        cuerpo = partes[0] + "</p>" + partes[1] + "</p>\n" + anuncio("tras el segundo párrafo") + partes[2]
    trozos = cuerpo.split("<h2")
    for i in (5, 3):
        if len(trozos) > i:
            trozos[i - 1] += anuncio(f"antes del apartado {i}") + "\n"
    return "<h2".join(trozos)


CALCULADORA = (EST / "calculadora.html").read_text(encoding="utf-8") if (EST / "calculadora.html").exists() else ""


def plantilla(meta, cuerpo, url, extra_head=""):
    titulo = meta["title"]
    desc = meta.get("desc", "")
    canon = DOMINIO + url
    menu = "".join(
        '<a href="/%s/"%s>%s</a>' % (s, ' aria-current="page"' if url.startswith("/%s/" % s) else "", n)
        for s, n in MENU)
    ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
           f'?client={ADSENSE_ID}" crossorigin="anonymous"></script>') if ADSENSE_ID else ""
    pagina = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{'website' if url == '/' else 'article'}">
<meta property="og:title" content="{html.escape(titulo)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="{MARCA}">
<meta property="og:locale" content="es_ES">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/estilo.css">
{extra_head}{ads}
</head>
<body>
<a class="saltar" href="#contenido">Saltar al contenido</a>
<header class="cabecera">
  <div class="ancho cabecera-fila">
    <a class="marca" href="/" aria-label="{MARCA}, inicio">
      <svg viewBox="0 0 32 32" width="30" height="30" aria-hidden="true"><circle cx="16" cy="16" r="15" fill="#0E4C6B"/><path d="M7 20c3-6 6-6 9 0s6 6 9 0" fill="none" stroke="#F4B13E" stroke-width="2.6" stroke-linecap="round"/><path d="M7 13c3-6 6-6 9 0s6 6 9 0" fill="none" stroke="#BFE3F2" stroke-width="2.6" stroke-linecap="round"/></svg>
      <span>{MARCA}</span>
    </a>
    <nav class="menu" aria-label="Secciones">{menu}</nav>
  </div>
  <div class="franja" aria-hidden="true"></div>
</header>
<main id="contenido">
{cuerpo}
</main>
<footer class="pie">
  <div class="ancho pie-fila">
    <p><strong>{MARCA}</strong><br>Información independiente sobre aerotermia para viviendas en España. No instalamos ni vendemos equipos.</p>
    <nav aria-label="Enlaces del pie">
      <a href="/guia/">Guía básica</a>
      <a href="/calculadora/">Calculadora</a>
      <a href="/sobre-nosotros/">Quiénes somos</a>
      <a href="/contacto/">Contacto</a>
      <a href="/aviso-legal/">Aviso legal</a>
      <a href="/privacidad/">Privacidad</a>
      <a href="/cookies/">Cookies</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""
    pagina = pagina.replace("{{CALCULADORA}}", CALCULADORA)
    pagina = pagina.replace("{{TITULAR}}", TITULAR).replace("{{CORREO}}", CORREO).replace("{{MARCA}}", MARCA)
    return relativizar(pagina, url)


def migas(pasos):
    """pasos: lista de (nombre, url). Devuelve (html, json-ld)."""
    enlaces = " <span aria-hidden=\"true\">/</span> ".join(
        f'<a href="{u}">{n}</a>' for n, u in pasos[:-1])
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": DOMINIO + u}
                              for i, (n, u) in enumerate(pasos)]}
    return f'<nav class="migas" aria-label="Estás en">{enlaces}</nav>', ld


def bloque_faq(faq):
    if not faq:
        return "", None
    items = "".join(f"<details><summary>{p}</summary><p>{r}</p></details>" for p, r in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": re.sub("<[^>]+>", "", p),
                          "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", r)}}
                         for p, r in faq]}
    return f'<section class="faq"><h2>Preguntas frecuentes</h2>{items}</section>', ld


def ld_script(*objetos):
    return "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>\n'
                   for o in objetos if o)


def tarjeta(meta):
    return (f'<li><a href="{url_de(meta)}">{meta["h1"]}</a>'
            f'<span>{meta.get("resumen", meta.get("desc", ""))}</span></li>')


def main():
    paginas = [leer(p) for p in sorted(CONT.glob("*.html"))]
    articulos = [(m, c) for m, c in paginas if m.get("tipo", "articulo") == "articulo"]
    por_cat = {}
    for m, _ in articulos:
        por_cat.setdefault(m["cat"], []).append(m)
    for lista in por_cat.values():
        lista.sort(key=lambda m: int(m.get("orden", 99)))

    if SAL.exists():
        shutil.rmtree(SAL)
    SAL.mkdir()
    urls = []

    for meta, cuerpo in paginas:
        tipo = meta.get("tipo", "articulo")
        url = url_de(meta)
        fecha = meta.get("fecha", "2026-11-15")
        head = ""

        if tipo == "home":
            listas = ""
            for slug, nombre in CATEGORIAS:
                arts = por_cat.get(slug, [])
                if not arts:
                    continue
                enlaces = "".join(f'<li><a href="{url_de(a)}">{a["h1"]}</a></li>' for a in arts)
                listas += (f'<section class="bloque-cat"><h3><a href="/{slug}/">{nombre}</a></h3>'
                           f'<ul>{enlaces}</ul></section>')
            cuerpo = cuerpo.replace("{{GUIAS}}", listas)
            head = ld_script({"@context": "https://schema.org", "@type": "WebSite",
                              "name": MARCA, "url": DOMINIO + "/", "inLanguage": "es"})
            contenido = cuerpo

        elif tipo == "pilar":
            m_html, m_ld = migas([("Inicio", "/"), (NOMBRE_CAT[meta["cat"]], url)])
            arts = por_cat.get(meta["cat"], [])
            lista = ('<section class="lista-articulos"><h2>Artículos de esta sección</h2><ul>'
                     + "".join(tarjeta(a) for a in arts) + "</ul></section>") if arts else ""
            f_html, f_ld = bloque_faq(meta["faq"])
            head = ld_script(m_ld, f_ld)
            contenido = (f'<article class="ancho texto">{m_html}<h1>{meta["h1"]}</h1>'
                         f'<p class="fecha">Actualizado el {fecha_larga(fecha)}</p>'
                         f'{meter_anuncios(cuerpo)}{lista}{f_html}</article>')

        elif tipo == "pagina":
            m_html, m_ld = migas([("Inicio", "/"), (meta["h1"], url)])
            head = ld_script(m_ld)
            clase = "ancho" if meta.get("ancha") else "ancho texto"
            contenido = f'<article class="{clase}">{m_html}<h1>{meta["h1"]}</h1>{cuerpo}</article>'

        else:  # artículo
            cat = meta["cat"]
            m_html, m_ld = migas([("Inicio", "/"), (NOMBRE_CAT[cat], f"/{cat}/"), (meta["h1"], url)])
            f_html, f_ld = bloque_faq(meta["faq"])
            hermanos = [a for a in por_cat[cat] if a is not meta][:4]
            otros = [a for c, l in por_cat.items() if c != cat for a in l
                     if a["slug"] in meta.get("ver", "").split()]
            rel = hermanos + otros
            relacionados = ('<aside class="relacionados"><h2>Sigue leyendo</h2><ul>'
                            + "".join(tarjeta(a) for a in rel)
                            + f'<li><a href="/calculadora/">Calculadora de precio y ahorro</a>'
                              f'<span>Estima el coste y el ahorro anual para tu vivienda.</span></li>'
                            + "</ul></aside>")
            art_ld = {"@context": "https://schema.org", "@type": "Article",
                      "headline": meta["h1"], "description": meta.get("desc", ""),
                      "datePublished": meta.get("publicado", fecha), "dateModified": fecha,
                      "inLanguage": "es", "mainEntityOfPage": DOMINIO + url,
                      "author": {"@type": "Person", "name": TITULAR, "url": DOMINIO + "/sobre-nosotros/"},
                      "publisher": {"@type": "Organization", "name": MARCA, "url": DOMINIO + "/"}}
            head = ld_script(m_ld, art_ld, f_ld)
            contenido = (f'<article class="ancho texto">{m_html}<h1>{meta["h1"]}</h1>'
                         f'<p class="fecha">Actualizado el {fecha_larga(fecha)} · '
                         f'<a href="/sobre-nosotros/">Cómo verificamos los datos</a></p>'
                         f'{meter_anuncios(cuerpo)}{f_html}{anuncio("final del artículo")}'
                         f'{relacionados}</article>')

        destino = SAL / url.strip("/") / "index.html" if url != "/" else SAL / "index.html"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(plantilla(meta, contenido, url, head), encoding="utf-8")
        if not meta.get("noindex"):
            urls.append((url, fecha))

    # Archivos estáticos
    for f in EST.iterdir():
        if f.name != "calculadora.html":
            shutil.copy(f, SAL / f.name)
    (SAL / ".nojekyll").write_text("")
    (SAL / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n")
    mapa = "".join(f"<url><loc>{DOMINIO}{u}</loc><lastmod>{f}</lastmod></url>\n" for u, f in sorted(urls))
    (SAL / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + mapa + "</urlset>\n")
    # Página 404 (enlaces absolutos: puede mostrarse en cualquier ruta)
    p404 = plantilla({"title": f"Página no encontrada | {MARCA}", "desc": ""},
                     '<article class="ancho texto"><h1>Esta página no existe</h1>'
                     '<p>Puede que el enlace esté mal escrito o que hayamos movido el artículo. '
                     'Vuelve al <a href="/">inicio</a> o abre la <a href="/calculadora/">calculadora</a>.</p></article>',
                     "/")
    (SAL / "404.html").write_text(p404.replace('href="./', 'href="/').replace('src="./', 'src="/'), encoding="utf-8")
    print(f"Hecho: {len(urls)} páginas en {SAL}")


if __name__ == "__main__":
    main()
