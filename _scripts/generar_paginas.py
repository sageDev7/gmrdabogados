"""Páginas internas de GMRD Abogados: estudio, prácticas (con anclas), insights + 3 artículos, términos,
privacidad y aviso legal (sus textos legales literales), y 404. Toma head/header/footer del index.
Los artículos y legales se convierten desde _contenido/*.txt (texto de su web actual). Idempotente.
Uso: python _scripts/generar_paginas.py"""
import re, json, html
from pathlib import Path

D = Path(__file__).resolve().parent.parent
C = D / "_contenido"
idx = (D / "index.html").read_text(encoding="utf8")
head_tpl = idx[:idx.index("<title>")]
links_head = idx[idx.index('<link rel="preconnect"'):idx.index("</head>")]
links_head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", links_head, flags=re.S)
links_head = re.sub(r'<meta (property="og:|name="twitter:)[^>]*>\n', "", links_head)
top = idx[idx.index("<!-- ============ HEADER ============ -->"):idx.index("<main>")]
f0 = idx.index("<!-- ============ FOOTER")
foot = idx[f0:idx.index('<a class="wa-float', f0)]
cola = idx[idx.index('<a class="wa-float', f0):idx.index('<script src="./main.js')]
cola = re.sub(r'<div class="modal".*?</div>\s*</div>\s*', "", cola, flags=re.S)
JS = re.search(r'<script src="\./main\.js[^"]*"></script>', idx).group(0)

def interna(s):
    s = re.sub(r'href="#(?!")', 'href="./index.html#', s)
    return s.replace('href="./index.html#inicio"', 'href="./index.html"')
top, foot = interna(top), interna(foot)

def page(name, title, desc, body, schema="", robots=""):
    rb = f'<meta name="robots" content="{robots}">\n' if robots else ""
    h = (head_tpl + f'<title>{title}</title>\n<meta name="description" content="{desc}">\n{rb}'
         + '<meta name="color-scheme" content="only light">\n<link rel="icon" type="image/png" href="./favicon.png">\n'
         + links_head + schema + "</head>\n<body>\n\n" + top + "<main>\n" + body + "\n\n</main>\n\n" + foot + cola + JS + "\n</body>\n</html>\n")
    (D / name).write_text(h, encoding="utf8", newline="\n"); print("ok", name)

def cabecera(foto, ruta, h1, intro, extra=""):
    return f'''
<!-- ============ CABECERA DE PÁGINA ============ -->
<section class="ph">
  <div class="ph-bg" style="background-image:url(img/{foto})" aria-hidden="true"></div>
  <div class="wrap ph-in">
    <nav class="ruta rise" aria-label="Ruta"><a href="./index.html">Inicio</a><i class="ti ti-chevron-right" aria-hidden="true"></i>{extra}<span>{ruta}</span></nav>
    <h1 class="ph-h1 rise d1">{h1}</h1>
    <p class="ph-lead rise d2">{intro}</p>
  </div>
</section>'''

CTA = '''
<!-- ============ CTA claro ============ -->
<section class="cta-c">
  <div class="wrap cta-c-in reveal">
    <img src="./img/logo.png" alt="" width="900" height="946" aria-hidden="true">
    <div><h2>¿Necesitás asesoramiento?</h2><p>Atención con cita previa, de lunes a viernes de 9 a 18 hs.</p></div>
    <div class="cta-btns">
      <a class="btn btn-azul js-wa" href="#" data-msg="{wa}">Consultar por WhatsApp</a>
      <a class="btn btn-navy-line" href="./index.html#contacto">Enviar un email</a>
    </div>
  </div>
</section>'''

def limpiar(t):
    t = t.replace("​", "").replace("\r", "")
    lines = [l.strip() for l in t.split("\n")]
    menu = {"INICIO", "SOBRE NOSOTROS", "PRACTICAS", "INSIGHTS", "CONTACTO", "Más", "Protección de Datos y Ciberseguridad",
            "Contratos Inteligentes y Firma Digital", "Inteligencia Artificial y Propiedad Intelectual"}
    return [l for l in lines if l and l not in menu]

def esc(s): return html.escape(s, quote=False)

def parrafo(l):
    m = re.match(r"^([^:]{3,70}):\s+(.+)$", l)
    if m and not re.match(r"^(Art|Ley)\b", m.group(1)):
        return f"<p><strong>{esc(m.group(1))}:</strong> {esc(m.group(2))}</p>"
    m = re.match(r"^(Art\. ?[\w ().°]+?):\s*(.+)$", l)
    if m: return f"<p><strong>{esc(m.group(1))}:</strong> {esc(m.group(2))}</p>"
    return f"<p>{esc(l)}</p>"

def es_h2(l): return bool(re.match(r"^[IVX]+\.\s+[A-ZÁÉÍÓÚÑ0-9 ,:().\-\"/]+$", l)) and l.upper() == l
def es_h3(l): return bool(re.match(r"^\d+(\.\d+)?\.\s+\S", l)) and len(l) < 95 and not l.endswith(".") or bool(re.match(r"^\d\.\d\.\s", l))

# ---------- artículos ----------
ARTS = [
    ("insight-proteccion-de-datos.html", "art_proteccin-de-datos-y-ciberseguridad.txt", "Ley 25.326", "Edición N° 1", "fibra.jpg"),
    ("insight-smart-contracts.html", "art_contratos-inteligentes-y-firma-digital.txt", "Ley 25.506", "Edición N° 2", "torre.jpg"),
    ("insight-ia-propiedad-intelectual.html", "art_inteligencia-artificial-y-propiedad-intelectual.txt", "Ley 11.723", "Edición N° 3", "ciudad.jpg"),
]
for fname, src, tag, edicion, foto in ARTS:
    L = limpiar((C / src).read_text(encoding="utf8"))
    bi = next(i for i, l in enumerate(L) if l.startswith("Por:"))
    autor = L[bi].replace("Por:", "").strip().rstrip(".")
    autor = re.sub(r"\s*\(.*?\)", "", autor).strip()
    bajada, titulo = L[bi - 1], L[bi - 2]
    rest = L[bi + 1:]
    # sumario: hasta el primer encabezado romano
    first = next(i for i, l in enumerate(rest) if es_h2(l))
    pre = [l for l in rest[:first] if l not in ("SUMARIO:",)]
    sumario = ""
    if pre:
        items = []
        for l in pre:
            items += [x.strip() for x in re.split(r"\s+—\s+", l) if x.strip()]
        sumario = '<aside class="sumario"><h2>Sumario</h2><ol>' + "".join(f"<li>{esc(re.sub(r'^[IVX]+\.\s*', '', x))}</li>" for x in items) + "</ol></aside>"
    cuerpo = []
    for l in rest[first:]:
        if es_h2(l): cuerpo.append(f"<h2>{esc(l)}</h2>")
        elif es_h3(l): cuerpo.append(f"<h3>{esc(l)}</h3>")
        else: cuerpo.append(parrafo(l))
    body = cabecera(foto, "Artículo", esc(titulo), esc(bajada), '<a href="./insights.html">Insights</a><i class="ti ti-chevron-right" aria-hidden="true"></i>') + f'''

<section class="articulo">
  <div class="wrap art-grid">
    <article class="art-cuerpo">
      <div class="art-meta"><span class="art-tag">{tag}</span><span>GMRD Doctrina Digital · {edicion}</span><span>Por {esc(autor)}</span></div>
      {sumario}
      {"".join(cuerpo)}
      <p class="art-aviso">Este artículo tiene carácter informativo y no constituye asesoramiento legal. Ante un caso particular, consultá con un profesional.</p>
    </article>
  </div>
</section>
''' + CTA.format(wa="Hola, leí un artículo de GMRD y quisiera hacer una consulta.")
    schema = '<script type="application/ld+json">\n' + json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": titulo,
        "description": bajada, "author": {"@type": "Person", "name": autor}, "publisher": {"@type": "Organization", "name": "GMRD Abogados"}}, ensure_ascii=False) + "\n</script>\n"
    page(fname, f"{titulo[:60]} | GMRD Abogados", esc(bajada[:155]), body, schema)

# ---------- insights ----------
cards = ""
for fname, src, tag, edicion, foto in ARTS:
    L = limpiar((C / src).read_text(encoding="utf8"))
    bi = next(i for i, l in enumerate(L) if l.startswith("Por:"))
    cards += f'''
      <a class="art reveal" href="./{fname}"><span class="art-tag">{tag}</span><h3>{esc(L[bi-2])}</h3><p>{esc(L[bi-1])}</p><span class="art-mas">Leer artículo <i class="ti ti-arrow-right" aria-hidden="true"></i></span></a>'''
body = cabecera("torre.jpg", "Insights", "Doctrina digital <em>y novedades legaltech.</em>",
                "Análisis doctrinarios, novedades normativas y artículos de investigación de GMRD Abogados.") + f'''

<section class="sec sec-claro">
  <div class="wrap">
    <div class="arts arts-3">{cards}
    </div>
  </div>
</section>

<section class="sec sec-navy-2 boletin">
  <div class="wrap boletin-in reveal">
    <div>
      <p class="eyebrow">GMRD Doctrina Digital</p>
      <h2 class="h2">Recibí nuestros análisis <em>en tu correo.</em></h2>
      <p class="lead">Suscribite al boletín para recibir análisis doctrinarios, novedades normativas y artículos de investigación.</p>
    </div>
    <a class="btn btn-azul" href="https://docs.google.com/forms/d/e/1FAIpQLSfi6GZ92R6eF6S8-edEKaNJgiG7E0PyXPitZ0rRDsOJKaBEAQ/viewform" target="_blank" rel="noopener">Suscribirme al boletín</a>
  </div>
</section>
''' + CTA.format(wa="Hola, quisiera hacer una consulta.")
page("insights.html", "Insights | GMRD Abogados",
     "Doctrina digital de GMRD Abogados: protección de datos, smart contracts y firma digital, inteligencia artificial y propiedad intelectual.", body)

# ---------- sobre nosotros ----------
body = cabecera("reunion.jpg", "Sobre nosotros", "Innovación jurídica <em>con solidez profesional.</em>",
                "Una firma de nueva generación para las demandas complejas del ecosistema legal contemporáneo.") + '''

<section class="sec sec-claro sobre">
  <div class="wrap sobre-grid">
    <div class="sobre-txt reveal">
      <p class="eyebrow">La firma</p>
      <h2 class="h2">Una firma <em>de nueva generación.</em></h2>
      <p class="lead">GMRD Abogados combina la agilidad y la visión de una firma joven con la amplia experiencia multidisciplinaria de sus profesionales en las ramas fundamentales del derecho.</p>
      <p>Nuestro enfoque integral nos permite acompañar a corporaciones consolidadas, empresas en expansión, startups y particulares, con un patrocinio técnico riguroso.</p>
    </div>
    <figure class="sobre-foto reveal"><img src="./img/reunion.jpg" alt="Reunión de trabajo en una oficina corporativa" width="1900" height="1069" loading="lazy"></figure>
  </div>
</section>

<section class="sec sec-navy">
  <div class="wrap">
    <div class="sec-head reveal">
      <p class="eyebrow eyebrow-c">Áreas clave</p>
      <h2 class="h2">Patrocinio técnico <em>en las ramas fundamentales.</em></h2>
    </div>
    <div class="claves">
      <article class="clave reveal"><i class="ti ti-building-skyscraper" aria-hidden="true"></i><h3>Corporativo y asesoramiento empresarial</h3><p>Estructuración de negocios, prevención de riesgos operativos y cumplimiento normativo (compliance).</p></article>
      <article class="clave reveal"><i class="ti ti-briefcase" aria-hidden="true"></i><h3>Laboral y administrativo</h3><p>Gestión estratégica de relaciones de trabajo, contrataciones complejas y defensa ante organismos públicos o reguladores.</p></article>
      <article class="clave reveal"><i class="ti ti-gavel" aria-hidden="true"></i><h3>Penal y litigios</h3><p>Defensa técnica y patrocinio en procesos judiciales con un enfoque analítico de alta precisión.</p></article>
    </div>
  </div>
</section>

<section class="sec sec-foto legaltech">
  <div class="foto-bg" aria-hidden="true"></div>
  <div class="wrap lt-grid">
    <div class="lt-txt reveal">
      <p class="eyebrow">Lo que nos diferencia</p>
      <h2 class="h2">Smart contracts <em>e infraestructura blockchain.</em></h2>
      <p class="lead">No nos limitamos a la teoría: conocemos el entorno técnico en el que operan los nuevos negocios digitales.</p>
    </div>
    <div class="lt-txt-2 reveal">
      <p>Auditamos y estructuramos acuerdos programables conectados directamente con la red Ethereum, el estándar descentralizado donde esta tecnología cobra vida y funcionalidad.</p>
      <p>Traducimos la complejidad del código informático al marco regulatorio vigente, con seguridad jurídica, automatización transparente y validez probatoria en activos digitales, DeFi y arquitectura blockchain.</p>
    </div>
  </div>
</section>

<section class="sec sec-claro mision">
  <div class="wrap mision-in reveal">
    <p class="eyebrow eyebrow-c">Nuestra misión</p>
    <blockquote>Unir la excelencia del ejercicio legal tradicional con la transformación digital, ofreciendo a nuestros clientes un acompañamiento preventivo, estratégico y tecnológicamente avanzado ante un mundo en constante evolución.</blockquote>
    <div class="valores"><span>Adaptabilidad</span><span>Empatía</span><span>Honestidad</span><span>Conocimiento técnico</span></div>
  </div>
</section>
''' + CTA.format(wa="Hola, quisiera hacer una consulta.")
page("estudio.html", "Sobre nosotros | GMRD Abogados",
     "GMRD Abogados: firma de nueva generación que une el ejercicio legal tradicional con la transformación digital. Corporativo, laboral, penal y legaltech.", body)

# ---------- prácticas (textos de su web) ----------
PR = [
    ("societario", "ti-building-skyscraper", "Asesoramiento societario y derecho corporativo", "Acompañamos a empresas, startups y fondos en todo su ciclo de vida corporativo.",
     ["Constitución, reestructuración, fusiones y adquisiciones (M&A) de sociedades comerciales (S.A., S.A.S., S.R.L.).",
      "Redacción de acuerdos de accionistas, estatutos a medida y buen gobierno corporativo (corporate governance).",
      "Planificación estratégica, gestión de activos empresariales y cumplimiento normativo (compliance)."]),
    ("laboral", "ti-briefcase", "Derecho laboral y relaciones de trabajo", "Estrategia preventiva y defensa técnica en la gestión del capital humano.",
     ["Redacción y auditoría de contratos laborales ejecutivos y esquemas de contratación remota o transfronteriza.",
      "Negociación colectiva, resolución de conflictos laborales y prevención de contingencias impositivas y previsionales.",
      "Representación ante organismos administrativos de trabajo y patrocinio letrado en litigios laborales complejos."]),
    ("comercio-exterior", "ti-world-upload", "Comercio exterior, aduanas y régimen cambiario", "Soluciones legales en la importación, exportación y circulación transfronteriza de bienes y capitales.",
     ["Asesoramiento integral en derecho aduanero, clasificación arancelaria y valoración impositiva.",
      "Defensa técnica ante sumarios aduaneros, infracciones y reclamos cambiarios ante autoridades regulatorias (BCRA y ARCA).",
      "Estructuración jurídica de contratos de transporte internacional, logística y comercio transfronterizo."]),
    ("migratorio", "ti-plane-departure", "Derecho migratorio corporativo y movilidad internacional", "Gestión legal para la radicación y movilidad de talentos, ejecutivos y nómadas digitales.",
     ["Radicaciones temporarias, permanentes y visados corporativos y ejecutivos ante la Dirección Nacional de Migraciones.",
      "Compliance migratorio para empresas internacionales con personal expatriado o remoto.",
      "Asesoramiento en doble residencia fiscal, convenios de no imposición e integración normativa regional (MERCOSUR y convenios internacionales)."]),
    ("penal", "ti-gavel", "Derecho penal corporativo y litigios", "Defensa técnica y patrocinio de alta precisión en controversias complejas.",
     ["Prevención y patrocinio en delitos económicos, tributarios, penal cambiario y penal aduanero.",
      "Querellas corporativas y defensa estratégica en procesos penales ordinarios y de fuero federal.",
      "Diseño e implementación de programas de prevención de delitos e integridad (criminal compliance)."]),
    ("legaltech", "ti-cpu", "Legaltech, smart contracts y ecosistema blockchain", "Nuestra área de vanguardia, donde la arquitectura digital se integra formalmente con el derecho.",
     ["Auditoría e integración legal en Ethereum: diseño, revisión y encuadre regulatorio de contratos inteligentes ejecutados en la red.",
      "Activos digitales y tokenización: estructuración legal de proyectos Web3, tokenización de activos del mundo real (RWA), finanzas descentralizadas (DeFi) y propiedad intelectual digital.",
      "Validez probatoria y firma digital: evidencias digitales, sellado de tiempo blockchain (timestamping) y seguridad jurídica para entornos 100% transaccionales."]),
    ("internacional", "ti-id", "Derecho internacional, ciudadanías y gestión transfronteriza", "Trámites y representación para personas y empresas con vínculos con España e Italia.",
     ["Gestión integral de ciudadanías: asesoramiento y armado de carpetas probatorias para obtener la ciudadanía (España, Italia, entre otras).",
      "Tramitación de NIE (Número de Identidad de Extranjero) para no residentes y residentes, indispensable para comprar inmuebles, constituir empresas y operar fiscalmente en España.",
      "Recursos e impugnación de multas de tráfico en España: descargos, recursos de alzada y reclamos ante la DGT u organismos locales.",
      "Representación legal ante la administración pública española (AEAT, Extranjería, Registro Mercantil) mediante representación digital directa."]),
]
indice = "".join(f'<a href="#{k}"><i class="ti {ic}" aria-hidden="true"></i>{n:02d}</a>' for n, (k, ic, *_ ) in enumerate(PR, 1))
bloques = ""
for n, (k, ic, t, intro, items) in enumerate(PR, 1):
    lis = "".join(f"<li>{esc(x)}</li>" for x in items)
    bloques += f'''
    <article class="prb reveal" id="{k}">
      <div class="prb-head"><span class="prb-n">{n:02d}</span><i class="ti {ic}" aria-hidden="true"></i></div>
      <div class="prb-body"><h2>{esc(t)}</h2><p class="lead">{esc(intro)}</p><ul class="checks">{lis}</ul></div>
    </article>'''
body = cabecera("torres-azules.jpg", "Prácticas", "Asesoramiento integral, <em>preventivo y estratégico.</em>",
                "Combinamos un profundo dominio de la normativa técnica y procesal con herramientas tecnológicas avanzadas, para soluciones ágiles y con plena validez jurídica.") + f'''

<section class="sec sec-claro practicas-pag">
  <div class="wrap">{bloques}
  </div>
</section>
''' + CTA.format(wa="Hola, quisiera hacer una consulta.")
page("practicas.html", "Prácticas | GMRD Abogados",
     "Societario, laboral, comercio exterior y aduanas, migratorio, penal corporativo, legaltech y blockchain, ciudadanías y trámites en España. GMRD Abogados, CABA.", body)

# ---------- legales (sus textos literales) ----------
LEG = [("terminos.html", "leg_trminos-y-condiciones.txt", "Términos y condiciones", "Condiciones de uso del sitio web de GMRD Abogados."),
       ("privacidad.html", "leg_poltica-y-privacidad.txt", "Política de privacidad", "Política de privacidad y protección de datos personales de GMRD Abogados (Ley 25.326)."),
       ("aviso-legal.html", "leg_aviso-legal.txt", "Aviso legal", "Aviso legal y datos identificativos de GMRD Abogados.")]
for fname, src, titulo, desc in LEG:
    L = limpiar((C / src).read_text(encoding="utf8"))
    L = [l for l in L if l.lower() not in (titulo.lower(), "política y privacidad")]
    if L and L[0].isupper(): L = L[1:]
    out = []
    for l in L:
        if re.match(r"^\d+\.\s+\S", l) and len(l) < 80: out.append(f"<h2>{esc(l)}</h2>")
        elif len(l) < 60 and l.endswith("."): out.append(f'<p class="item">{esc(l)}</p>')
        else: out.append(f"<p>{esc(l)}</p>")
    body = f'''
<section class="legal-hero">
  <div class="wrap">
    <nav class="ruta" aria-label="Ruta"><a href="./index.html">Inicio</a><i class="ti ti-chevron-right" aria-hidden="true"></i><span>{titulo}</span></nav>
    <h1 class="ph-h1">{titulo}</h1>
  </div>
</section>
<section class="legal">
  <div class="wrap legal-in">
    {"".join(out)}
  </div>
</section>'''
    page(fname, f"{titulo} | GMRD Abogados", desc, body)

# ---------- 404 ----------
body = '''
<section class="nf">
  <div class="wrap">
    <span class="nf-num" aria-hidden="true">404</span>
    <h1 class="h2">Esta página <em>no existe.</em></h1>
    <p class="lead">Puede que haya cambiado de dirección. Volvé al inicio o escribinos y te ayudamos.</p>
    <div class="nf-ctas">
      <a class="btn btn-azul" href="./index.html">Volver al inicio</a>
      <a class="btn btn-line js-wa" href="#" data-msg="Hola, quisiera hacer una consulta.">Consultar por WhatsApp</a>
    </div>
  </div>
</section>'''
page("404.html", "Página no encontrada | GMRD Abogados", "La página que buscás no existe o cambió de dirección.", body, robots="noindex")

# ---------- CSS de páginas internas (una sola vez) ----------
css_p = D / "styles.css"; c = css_p.read_text(encoding="utf8")
if "/* ---------- páginas internas" not in c:
    c += '''
/* ---------- páginas internas (generar_paginas.py) ---------- */
.ph{position:relative;min-height:clamp(440px,60vh,620px);display:flex;align-items:flex-end;overflow:hidden;background:var(--navy);margin-top:var(--hdr)}
.ph-bg{position:absolute;inset:0;background-size:cover;background-position:center}
.ph-bg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(13,27,46,.72),rgba(13,27,46,.66) 40%,rgba(13,27,46,.97))}
.ph-in{position:relative;z-index:1;padding-top:4rem;padding-bottom:4rem}
.ruta{display:flex;align-items:center;flex-wrap:wrap;gap:.6rem;margin-bottom:1.4rem;font-family:var(--f-head);font-size:.68rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--cian-l)}
.ruta a:hover{color:var(--blanco)}
.ruta i{font-size:.9rem;color:var(--cian)}
.ruta span{color:var(--blanco)}
.ph-h1{max-width:52rem;font-size:clamp(2.1rem,3.9vw,3.2rem);font-weight:700}
.ph-h1 em{display:block;font-style:normal;color:var(--cian)}
.ph-lead{max-width:44rem;margin-top:1.2rem;font-size:1.12rem;color:#DCE7F2}
.claves{display:grid;grid-template-columns:repeat(3,1fr);gap:1.3rem}
.clave{padding:2.2rem 2rem;background:rgba(255,255,255,.03);border:1px solid var(--line-d);border-top:3px solid var(--cian);border-radius:4px}
.clave i{font-size:1.9rem;color:var(--cian)}
.clave h3{margin:1rem 0 .5rem;font-size:1.12rem}
.lt-txt-2 p+p{margin-top:1rem}
.mision-in{display:flex;flex-direction:column;align-items:center;max-width:58rem;margin:0 auto;text-align:center}
.mision blockquote{font-family:var(--f-head);font-size:clamp(1.25rem,2.2vw,1.65rem);font-weight:500;line-height:1.5;color:var(--ink)}
.valores{display:flex;flex-wrap:wrap;justify-content:center;gap:.6rem;margin-top:2.2rem}
.valores span{padding:.45rem 1rem;border:1px solid var(--line);border-radius:20px;font-family:var(--f-head);font-size:.72rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--acero)}
.prb{display:grid;grid-template-columns:120px 1fr;gap:2.4rem;padding:3rem 0;scroll-margin-top:calc(var(--hdr) + 1rem)}
.prb+.prb{border-top:1px solid var(--line)}
.prb-head{display:flex;flex-direction:column;align-items:flex-start;gap:.8rem}
.prb-n{font-family:var(--f-head);font-size:2.6rem;font-weight:700;line-height:1;color:var(--acero)}
.prb-head i{display:grid;place-items:center;width:3.2rem;height:3.2rem;border-radius:50%;background:var(--navy);font-size:1.5rem;color:var(--cian)}
.prb h2{font-size:clamp(1.4rem,2.4vw,1.8rem);color:var(--ink)}
.prb .lead{margin:.6rem 0 1.2rem;color:var(--muted)}
.checks li{position:relative;padding:.7rem 0 .7rem 1.9rem;color:var(--ink)}
.checks li+li{border-top:1px solid var(--line)}
.checks li::before{content:"\\ea5e";position:absolute;left:0;top:.72rem;font-family:"tabler-icons";font-size:1.05rem;color:var(--acero)}
.arts-3{grid-template-columns:repeat(3,1fr)}
.boletin-in{display:flex;align-items:center;justify-content:space-between;gap:3rem}
.boletin .lead{margin-top:1rem}
.articulo{padding:90px 0 110px;background:var(--hielo);color:#3E4A57}
.art-cuerpo{max-width:46rem;margin:0 auto}
.art-meta{display:flex;flex-wrap:wrap;align-items:center;gap:.6rem 1.2rem;margin-bottom:2rem;padding-bottom:1.4rem;border-bottom:1px solid var(--line);font-family:var(--f-head);font-size:.7rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.sumario{margin:0 0 2.6rem;padding:1.6rem 1.8rem;background:var(--blanco);border:1px solid var(--line);border-left:3px solid var(--acero);border-radius:4px}
.sumario h2{margin:0 0 .8rem;font-size:.8rem;letter-spacing:.18em;text-transform:uppercase;color:var(--acero)}
.sumario ol{padding-left:1.2rem;list-style:upper-roman}
.sumario li{padding:.2rem 0;font-size:.98rem;color:var(--ink)}
.art-cuerpo>h2{margin:2.8rem 0 1rem;font-size:1.02rem;letter-spacing:.06em;line-height:1.4;color:var(--azul)}
.art-cuerpo>h3{margin:1.8rem 0 .6rem;font-size:1.1rem;color:var(--azul)}
.art-cuerpo>p{margin-bottom:1rem;font-size:1.08rem;line-height:1.8}
.art-cuerpo strong{color:var(--ink)}
.art-aviso{margin-top:2.6rem!important;padding-top:1.4rem;border-top:1px solid var(--line);font-size:.92rem!important;font-style:italic;color:var(--muted)}
.cta-c{background:var(--blanco);color:var(--muted);border-top:1px solid var(--line)}
.cta-c-in{display:flex;align-items:center;justify-content:center;gap:3rem;padding-top:3.6rem;padding-bottom:3.6rem}
.cta-c-in img{width:120px;flex:none}
.cta-c h2{font-size:clamp(1.6rem,2.8vw,2.2rem);color:var(--ink)}
.cta-c p{margin-top:.3rem}
.cta-btns{display:grid;gap:.8rem}
.cta-btns .btn{width:100%}
.cta-c .btn-azul:hover{color:var(--acero);border-color:var(--acero)}
.legal-hero{margin-top:var(--hdr);padding:4rem 0 3rem;background:var(--navy)}
.legal{padding:70px 0 110px;background:var(--hielo);color:#3E4A57}
.legal-hero .wrap,.legal .wrap{max-width:calc(48rem + 4rem)}
.legal h2{margin:2.2rem 0 .7rem;font-size:1.2rem;color:var(--ink)}
.legal p{margin-bottom:.8rem}
.legal p.item{position:relative;margin-bottom:.3rem;padding-left:1.2rem}
.legal p.item::before{content:"";position:absolute;left:0;top:.75em;width:.5rem;height:2px;background:var(--acero)}
.nf{min-height:100vh;min-height:100svh;display:flex;align-items:center;padding:calc(var(--hdr) + 3rem) 0 4rem;background:var(--navy)}
.nf .wrap{width:fit-content;max-width:100%}
.nf-num{display:block;margin-bottom:1rem;font-family:var(--f-head);font-weight:700;font-size:clamp(5rem,13vw,9rem);line-height:.85;color:var(--cian)}
.nf .lead{margin:1.2rem 0 2rem;max-width:34rem}
.nf-ctas{display:flex;flex-wrap:wrap;gap:1rem}
@media (max-width:1024px){
  .claves,.arts-3{grid-template-columns:1fr 1fr}
  .claves .clave:last-child,.arts-3 .art:last-child{grid-column:1/-1}
  .boletin-in,.cta-c-in{flex-direction:column;text-align:center;gap:1.6rem}
}
@media (max-width:768px){
  .ph{min-height:auto}
  .ph-in{padding-top:3rem;padding-bottom:3rem;text-align:center}
  .ruta{justify-content:center}
  .ph-h1 em{display:inline}
  .ph-lead{margin-left:auto;margin-right:auto;font-size:1.02rem}
  .claves,.arts-3{grid-template-columns:1fr}
  .claves .clave:last-child,.arts-3 .art:last-child{grid-column:auto}
  .clave{text-align:center}
  .prb{grid-template-columns:1fr;gap:1rem;text-align:center}
  .prb-head{flex-direction:row;justify-content:center;align-items:center}
  .checks li{padding-left:0;text-align:center}
  .checks li::before{position:static;margin-right:.4rem}
  .articulo{padding:56px 0 80px}
  .legal-hero{text-align:center}
  .nf{text-align:center}
  .nf .lead{margin-left:auto;margin-right:auto}
  .nf-ctas{flex-direction:column;align-items:center}
  .nf-ctas .btn,.cta-btns .btn{width:100%;max-width:300px}
  .cta-btns{width:100%;justify-items:center}
}
'''
    css_p.write_text(c, encoding="utf8"); print("css ok")
