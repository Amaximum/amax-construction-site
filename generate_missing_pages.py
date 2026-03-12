#!/usr/bin/env python3
"""
generate_missing_pages.py
Creates all 78 pages that exist on WordPress but are missing from the new static site.
Exact URL slugs preserved for SEO migration.
Run: python generate_missing_pages.py
"""
import os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL  = "https://amaximumconstruction.com"
EMAIL     = "amaximumconstructioncorp@gmail.com"
PHONE     = "+1-647-XXX-XXXX"

# ── NAV ──────────────────────────────────────────────────────────────────────
NAV = """\
<div class="topbar-wrap shell">
  <header class="topbar" role="banner">
    <a class="logo" href="/" aria-label="aMaximum Construction home">
      <img src="/img/logo.png" alt="aMaximum Construction" width="140" height="40">
    </a>
    <div class="topbar-right">
      <nav class="nav" id="siteNav" aria-label="Main navigation">
        <a href="/">Home</a>
        <a href="/#services">Services</a>
        <a href="/locations/">Locations</a>
        <a href="/blog/">Blog</a>
        <a href="/portfolio/">Portfolio</a>
        <a href="/#contact">Contact</a>
      </nav>
      <a class="btn btn-primary btn-sm nav-quote" href="/#contact">Get Free Quote</a>
      <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false">&#9776;</button>
    </div>
  </header>
</div>"""

# ── FOOTER ────────────────────────────────────────────────────────────────────
FOOTER = """\
<footer class="site-footer">
  <div class="shell">
    <div class="footer-cols">
      <div class="footer-col footer-brand">
        <a href="/" class="footer-logo-link"><img src="/img/logo.png" alt="aMaximum Construction" class="footer-logo"></a>
        <p>Licensed and insured construction &amp; renovation services in Toronto &amp; GTA.</p>
        <a href="mailto:amaximumconstructioncorp@gmail.com" class="footer-email">amaximumconstructioncorp@gmail.com</a>
      </div>
      <div class="footer-col">
        <h4>Services</h4>
        <ul>
          <li><a href="/general-contractor-in-toronto/">General Contractor</a></li>
          <li><a href="/deck-builder/">Deck Building</a></li>
          <li><a href="/fence-contractor-in-toronto/">Fence Installation</a></li>
          <li><a href="/carpenter-services-toronto/">Carpentry</a></li>
          <li><a href="/handyman-service-in-toronto/">Handyman</a></li>
          <li><a href="/basement-renovation-service-in-toronto/">Basement Renovation</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Service Areas</h4>
        <ul>
          <li><a href="/general-contractor-in-toronto/">Toronto</a></li>
          <li><a href="/general-contractor-in-north-york/">North York</a></li>
          <li><a href="/general-contractor-in-markham/">Markham</a></li>
          <li><a href="/general-contractor-in-richmond-hill/">Richmond Hill</a></li>
          <li><a href="/general-contractor-in-vaughan/">Vaughan</a></li>
          <li><a href="/locations/">All Locations &rarr;</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/portfolio/">Portfolio</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/why-choose-us/">Why Choose Us</a></li>
          <li><a href="/#contact">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bar">
      <span>&copy; 2026 aMaximum Construction. Licensed &amp; Insured.</span>
      <span>Toronto &amp; GTA</span>
    </div>
  </div>
</footer>"""

SCRIPTS = f"""\
<script>
const menuBtn = document.getElementById('menuBtn');
const siteNav = document.getElementById('siteNav');
if (menuBtn && siteNav) {{
  menuBtn.addEventListener('click', () => {{
    const exp = menuBtn.getAttribute('aria-expanded') === 'true';
    menuBtn.setAttribute('aria-expanded', !exp);
    siteNav.classList.toggle('open');
  }});
}}
const m  = document.getElementById('bookingModal');
const b  = document.getElementById('bookingBtn');
const x  = document.getElementById('modalClose');
const ov = document.getElementById('modalOverlay');
const cc = document.getElementById('cancelBtn');
const f  = document.getElementById('bookingForm');
const bd = document.getElementById('bookDate');
if (bd) bd.min = new Date().toISOString().split('T')[0];
const openModal  = () => {{ m.classList.add('active');    document.body.style.overflow = 'hidden'; }};
const closeModal = () => {{ m.classList.remove('active'); document.body.style.overflow = '';       }};
if (b)  b.addEventListener('click', openModal);
if (x)  x.addEventListener('click', closeModal);
if (ov) ov.addEventListener('click', closeModal);
if (cc) cc.addEventListener('click', closeModal);
if (f) f.addEventListener('submit', e => {{
  e.preventDefault();
  const d = Object.fromEntries(new FormData(f));
  const subj = encodeURIComponent(d.service || document.title);
  const body = encodeURIComponent(
    `Name: ${{d.name}}\\nPhone: ${{d.phone}}\\nEmail: ${{d.email}}\\nAddress: ${{d.address}}\\nDate: ${{d.date}}\\nTime: ${{d.time}}\\n\\n${{d.details || 'N/A'}}`
  );
  window.location.href = `mailto:{EMAIL}?subject=${{subj}}&body=${{body}}`;
  f.reset();
  setTimeout(closeModal, 500);
}});
</script>"""


def modal(location_name, service_label):
    return f"""\
<div id="bookingModal" class="modal">
  <div class="modal-overlay" id="modalOverlay"></div>
  <div class="modal-content">
    <button class="modal-close" id="modalClose">&times;</button>
    <h2>Free Consultation — {location_name}</h2>
    <form id="bookingForm">
      <input type="hidden" name="service" value="{service_label} — {location_name}">
      <div class="form-row">
        <div class="form-group"><label>Name *</label><input type="text" name="name" required></div>
        <div class="form-group"><label>Phone *</label><input type="tel" name="phone" required></div>
      </div>
      <div class="form-group"><label>Email *</label><input type="email" name="email" required></div>
      <div class="form-group"><label>Address in {location_name} *</label><input type="text" name="address" required></div>
      <div class="form-row">
        <div class="form-group"><label>Preferred Date *</label><input type="date" id="bookDate" name="date" required></div>
        <div class="form-group"><label>Preferred Time *</label>
          <select name="time" required>
            <option value="">Select...</option>
            <option>8–10 AM</option><option>10–12 PM</option>
            <option>12–2 PM</option><option>2–4 PM</option>
          </select>
        </div>
      </div>
      <div class="form-group"><label>Project Details</label>
        <textarea name="details" rows="3" placeholder="Describe your project briefly..."></textarea>
      </div>
      <div style="display:flex;gap:12px;margin-top:20px">
        <button type="button" class="btn" id="cancelBtn" style="background:#e6eaf0;color:#121826">Cancel</button>
        <button type="submit" class="btn">Send Request</button>
      </div>
    </form>
  </div>
</div>"""


def build_schema(slug, service_type, location_name, faqs):
    canonical = f"{BASE_URL}/{slug}/"
    schemas = [
        {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "aMaximum Construction",
            "url": canonical,
            "telephone": PHONE,
            "email": EMAIL,
            "areaServed": {"@type": "City", "name": location_name, "addressRegion": "ON", "addressCountry": "CA"},
            "serviceType": service_type,
            "priceRange": "$$",
            "paymentAccepted": "Cash, Credit Card, E-Transfer",
            "currenciesAccepted": "CAD",
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL + "/"},
                {"@type": "ListItem", "position": 2, "name": f"{service_type} — {location_name}", "item": f"{BASE_URL}/{slug}/"},
            ],
        },
    ]
    if faqs:
        schemas.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faqs
            ],
        })
    return json.dumps(schemas, ensure_ascii=False, indent=2)


def build_page(slug, meta_title, meta_desc, h1, hero_sub, content_html, cta_h2, cta_p,
               location_name, service_type, service_label, faqs):
    canonical = f"{BASE_URL}/{slug}/"
    schema = build_schema(slug, service_type, location_name, faqs)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{meta_desc}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{meta_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="aMaximum Construction">
  <link rel="canonical" href="{canonical}">
  <title>{meta_title}</title>
  <link rel="stylesheet" href="/css/styles.css">
  <script type="application/ld+json">
{schema}
  </script>
</head>
<body>
{NAV}
<div class="page-hero">
  <h1>{h1}</h1>
  <p>{hero_sub}</p>
</div>
<div class="container">
  <div class="content">
{content_html}
  </div>
  <div class="cta-section">
    <h2>{cta_h2}</h2>
    <p>{cta_p}</p>
    <button class="btn" id="bookingBtn">Get Free Quote</button>
  </div>
</div>
{modal(location_name, service_label)}
{SCRIPTS}
{FOOTER}
</body>
</html>
"""


def write_page(slug, html):
    folder = os.path.join(BASE_DIR, slug)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  OK  /{slug}/")


# ═══════════════════════════════════════════════════════════════════════════════
#  BATHROOM RENOVATION
# ═══════════════════════════════════════════════════════════════════════════════

def gen_bathroom(loc_name, slug):
    faqs = [
        (f"How much does a bathroom renovation cost in {loc_name}?",
         f"Bathroom renovations in {loc_name} typically range from $8,000–$15,000 for a standard update and $20,000–$40,000+ for a full luxury remodel. aMaximum Construction provides detailed, transparent quotes tailored to your scope and budget."),
        (f"How long does a bathroom renovation take in {loc_name}?",
         f"A standard bathroom renovation in {loc_name} takes 2–4 weeks. Full gut-and-rebuild projects with plumbing relocations may take 4–6 weeks. We provide a firm timeline before work begins."),
        ("Do I need a permit for a bathroom renovation?",
         "Plumbing and electrical changes in bathrooms require permits in Ontario. aMaximum Construction manages all permit applications and inspections, ensuring your renovation meets Ontario Building Code."),
        (f"Can you update just fixtures without a full renovation in {loc_name}?",
         f"Yes. aMaximum Construction offers partial bathroom updates in {loc_name} — replacing fixtures, vanities, toilets, or tile without a complete gut renovation. We tailor the scope to your needs and budget."),
    ]
    content = f"""\
    <h2>Expert Bathroom Renovation in {loc_name}</h2>
    <p>aMaximum Construction delivers complete bathroom renovations in {loc_name} — from simple fixture upgrades to full luxury transformations. Our licensed team handles design, plumbing, electrical, tile work, and finish carpentry under one roof.</p>
    <p>Whether you're updating a dated main bathroom or creating a spa-like ensuite, we manage every detail so you don't have to.</p>

    <h2>Our Bathroom Renovation Services in {loc_name}</h2>
    <ul>
      <li><strong>Full Gut &amp; Rebuild</strong> — Complete bathroom transformation from subfloor up</li>
      <li><strong>Shower &amp; Tub Replacement</strong> — Walk-in showers, freestanding tubs, custom tile surrounds</li>
      <li><strong>Vanity &amp; Storage</strong> — Custom cabinetry, floating vanities, medicine cabinets</li>
      <li><strong>Tile &amp; Flooring</strong> — Porcelain, ceramic, natural stone, heated floors</li>
      <li><strong>Plumbing Upgrades</strong> — New fixtures, pipe relocation, water-efficient fittings</li>
      <li><strong>Electrical &amp; Lighting</strong> — Pot lights, vanity lighting, GFCI outlets, exhaust fans</li>
      <li><strong>Accessibility Renovations</strong> — Walk-in showers, grab bars, barrier-free design</li>
    </ul>

    <h2>Why {loc_name} Homeowners Choose aMaximum</h2>
    <p>We are a licensed and insured contractor with a proven track record of bathroom renovations across {loc_name}. Our team handles permits, coordinates all trades, and communicates clearly throughout the project. No subcontractor surprises — just quality results delivered on schedule.</p>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Bathroom Renovation in {loc_name} | Licensed Contractors | aMaximum Construction",
        meta_desc=f"Expert bathroom renovation services in {loc_name}. Full gut rebuilds, shower upgrades, tile, plumbing & electrical. Licensed, permit-managed. Free quotes.",
        h1=f"Bathroom Renovation in {loc_name}",
        hero_sub=f"Licensed bathroom renovation contractors serving {loc_name}. Quality craftsmanship, transparent pricing, permit-managed projects.",
        content_html=content,
        cta_h2=f"Ready to Renovate Your Bathroom in {loc_name}?",
        cta_p="Get a free, no-obligation consultation. We'll visit your home, discuss your vision, and provide a detailed written quote.",
        location_name=loc_name,
        service_type="Bathroom Renovation",
        service_label="Bathroom Renovation",
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  BASEMENT RENOVATION (best-* variants)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_best_basement(loc_name, slug):
    faqs = [
        (f"How much does basement renovation cost in {loc_name}?",
         f"Basement renovation in {loc_name} ranges from $25,000–$50,000 for a standard finish and $60,000–$100,000+ for a full in-law suite with kitchen and bathroom. aMaximum Construction provides detailed quotes based on your specific layout and goals."),
        (f"Do I need a permit to finish my basement in {loc_name}?",
         f"Yes — basement finishing that includes framing, electrical, plumbing, or HVAC work requires a building permit in {loc_name}. aMaximum Construction handles all permit applications and inspections."),
        (f"How long does a basement renovation take in {loc_name}?",
         f"A standard basement finish in {loc_name} takes 6–10 weeks. Projects with in-law suites, bathrooms, or wet bars may take 10–16 weeks. We provide a firm project schedule before work begins."),
        ("Can a finished basement be used as a rental unit?",
         "Yes, with the proper permits and inspections. aMaximum Construction designs and builds legal secondary suites in compliance with Ontario Building Code and local zoning bylaws, maximizing your rental income potential."),
    ]
    content = f"""\
    <h2>Best Basement Renovation Service in {loc_name}</h2>
    <p>aMaximum Construction is recognized as one of the top basement renovation contractors in {loc_name}. We transform unfinished or outdated basements into beautiful, functional living spaces — family rooms, home offices, in-law suites, home gyms, and more.</p>
    <p>Our full-service approach covers design, framing, electrical, plumbing, insulation, drywall, flooring, and finishing — all permit-managed and delivered on schedule.</p>

    <h2>Basement Renovation Services We Offer in {loc_name}</h2>
    <ul>
      <li><strong>Full Basement Finishing</strong> — Transform raw space into livable square footage</li>
      <li><strong>In-Law Suites</strong> — Legal secondary units with separate entrance, kitchen, and bathroom</li>
      <li><strong>Basement Bathrooms</strong> — Rough-in, full bath, or powder room additions</li>
      <li><strong>Waterproofing</strong> — Interior and exterior waterproofing, sump pump installation</li>
      <li><strong>Egress Windows</strong> — Code-compliant window enlargement for bedrooms</li>
      <li><strong>Underpinning &amp; Lowering</strong> — Increase ceiling height for comfortable living space</li>
      <li><strong>Home Theatres &amp; Recreation Rooms</strong> — Entertainment-focused basement designs</li>
    </ul>

    <h2>Why We're the Best Choice for Basement Renovation in {loc_name}</h2>
    <p>Our team has completed hundreds of basement renovations across {loc_name} and the GTA. We are fully licensed, insured, and committed to transparent communication from first quote to final walkthrough. Every project is permit-managed and built to Ontario Building Code.</p>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Best Basement Renovation Service in {loc_name} | aMaximum Construction",
        meta_desc=f"Top-rated basement renovation contractors in {loc_name}. In-law suites, full finishing, waterproofing & bathroom additions. Licensed, permit-managed. Free quotes.",
        h1=f"Best Basement Renovation Service in {loc_name}",
        hero_sub=f"Award-winning basement renovation in {loc_name}. Licensed contractors, full project management, permit-managed.",
        content_html=content,
        cta_h2=f"Start Your Basement Renovation in {loc_name}",
        cta_p="Book a free in-home consultation. We'll assess your space, discuss your goals, and provide a detailed written quote.",
        location_name=loc_name,
        service_type="Basement Renovation",
        service_label="Basement Renovation",
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  RENOVATION SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

def gen_renovation_services(loc_name, slug):
    faqs = [
        (f"What renovation services does aMaximum offer in {loc_name}?",
         f"aMaximum Construction offers full-scope home renovation services in {loc_name} including kitchen renovations, bathroom remodels, basement finishing, additions, and whole-home renovations. We manage every trade from demo to final finish."),
        (f"How do I get a renovation quote in {loc_name}?",
         f"Contact aMaximum Construction to schedule a free in-home consultation in {loc_name}. We'll assess your space, discuss your goals and budget, and provide a detailed written quote within 48 hours."),
        ("Do you manage permits for renovation projects?",
         "Yes. aMaximum Construction manages all building permit applications and inspections for renovation projects in Ontario. We ensure every project meets Ontario Building Code requirements."),
        (f"How long do home renovations take in {loc_name}?",
         f"Project timelines vary by scope. A bathroom renovation in {loc_name} takes 2–4 weeks; a kitchen renovation 4–8 weeks; a full basement finish 6–12 weeks; a home addition 3–6 months. We provide a detailed schedule before starting."),
    ]
    content = f"""\
    <h2>Complete Home Renovation Services in {loc_name}</h2>
    <p>aMaximum Construction is a licensed general contractor providing comprehensive home renovation services throughout {loc_name} and the Greater Toronto Area. From single-room updates to whole-home transformations, our experienced team delivers quality results on time and on budget.</p>

    <h2>Renovation Services Available in {loc_name}</h2>
    <ul>
      <li><strong>Kitchen Renovations</strong> — Custom cabinetry, countertops, appliance installation, backsplash</li>
      <li><strong>Bathroom Renovations</strong> — Tile, vanities, showers, plumbing, electrical</li>
      <li><strong>Basement Finishing</strong> — Family rooms, in-law suites, home offices, gyms</li>
      <li><strong>Home Additions</strong> — Second storeys, rear additions, garage conversions</li>
      <li><strong>Interior Renovations</strong> — Open-concept layouts, flooring, trim, painting</li>
      <li><strong>Exterior Renovations</strong> — Siding, windows, doors, decks, landscaping</li>
      <li><strong>General Contracting</strong> — Full project management for any scope</li>
    </ul>

    <h2>Our Renovation Process in {loc_name}</h2>
    <ol>
      <li><strong>Free Consultation</strong> — We visit your home and discuss your vision</li>
      <li><strong>Detailed Quote</strong> — Written, itemized proposal with no hidden costs</li>
      <li><strong>Permit Management</strong> — We handle all permit applications</li>
      <li><strong>Construction</strong> — Licensed trades, quality materials, daily updates</li>
      <li><strong>Final Walkthrough</strong> — We don't consider the job done until you're satisfied</li>
    </ol>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Home Renovation Services in {loc_name} | aMaximum Construction",
        meta_desc=f"Complete home renovation services in {loc_name}. Kitchens, bathrooms, basements, additions & more. Licensed, permit-managed contractor. Free quotes.",
        h1=f"Home Renovation Services in {loc_name}",
        hero_sub=f"Licensed renovation contractor in {loc_name}. Full project management, transparent pricing, quality guaranteed.",
        content_html=content,
        cta_h2=f"Start Your Renovation Project in {loc_name}",
        cta_p="Contact us for a free in-home consultation and detailed written quote. No obligation, no pressure.",
        location_name=loc_name,
        service_type="Home Renovation",
        service_label="Home Renovation",
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  DEMOLITION
# ═══════════════════════════════════════════════════════════════════════════════

def gen_demolition(loc_name, slug):
    faqs = [
        (f"What demolition services are available in {loc_name}?",
         f"aMaximum Construction provides interior demolition, basement demolition, structure removal, deck and fence demolition, shed removal, and full property demolition in {loc_name}. We handle debris removal and disposal."),
        (f"Do I need a permit for demolition in {loc_name}?",
         f"Structural demolition and full building demolition require permits in {loc_name}. Interior demolition for renovation purposes may not. aMaximum Construction advises on permit requirements and manages applications as needed."),
        (f"How much does demolition cost in {loc_name}?",
         f"Demolition costs in {loc_name} depend on scope and structure type. Interior room demo starts around $1,500–$3,000. Full structure removal is priced per project after assessment. Contact us for a free quote."),
        ("Do you handle asbestos and hazardous materials?",
         "We work with certified abatement contractors for asbestos, lead paint, and other hazardous materials. Safe removal of hazardous materials is always completed before demolition proceeds."),
    ]
    content = f"""\
    <h2>Professional Demolition Services in {loc_name}</h2>
    <p>aMaximum Construction provides safe, efficient demolition services throughout {loc_name} and the GTA. Whether you need interior demo for a renovation, complete structure removal, or targeted selective demolition, our experienced crew completes the work safely, cleanly, and on schedule.</p>

    <h2>Demolition Services We Offer in {loc_name}</h2>
    <ul>
      <li><strong>Interior Demolition</strong> — Wall removal, floor demo, fixture strip-out for renovations</li>
      <li><strong>Basement Demolition</strong> — Complete basement gut for renovation or underpinning</li>
      <li><strong>Structure Removal</strong> — Sheds, garages, decks, fences, outbuildings</li>
      <li><strong>Selective Demolition</strong> — Targeted removal preserving surrounding structure</li>
      <li><strong>Full Building Demolition</strong> — Complete residential demolition for new builds</li>
      <li><strong>Debris Removal</strong> — Full clean-up and disposal, bin rental included</li>
    </ul>

    <h2>Safe Demolition Practices in {loc_name}</h2>
    <p>Every demolition project in {loc_name} begins with a thorough assessment to identify structural elements, utilities, and potential hazardous materials. We disconnect utilities, coordinate with the city, and implement dust and debris containment before any work begins.</p>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Demolition Services in {loc_name} | Licensed Contractor | aMaximum Construction",
        meta_desc=f"Professional demolition services in {loc_name}. Interior demo, structure removal, debris disposal. Licensed, insured. Free quotes.",
        h1=f"Demolition Services in {loc_name}",
        hero_sub=f"Safe, efficient demolition contractor in {loc_name}. Interior to full structure — licensed, insured, fully managed.",
        content_html=content,
        cta_h2=f"Get a Demolition Quote in {loc_name}",
        cta_p="Contact us for a free assessment. We'll visit the site, evaluate the scope, and provide a detailed written quote.",
        location_name=loc_name,
        service_type="Demolition",
        service_label="Demolition",
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  CARPENTER
# ═══════════════════════════════════════════════════════════════════════════════

def gen_carpenter(loc_name, slug):
    faqs = [
        (f"What carpentry services does aMaximum offer in {loc_name}?",
         f"aMaximum Construction provides custom cabinetry, trim and moulding, built-in shelving, staircase work, door installation, and finish carpentry for renovations throughout {loc_name}."),
        (f"How much do carpenter services cost in {loc_name}?",
         f"Carpentry costs in {loc_name} vary by project complexity. Trim installation runs $3–$8 per linear foot; custom built-ins start around $2,000; full cabinetry projects are quoted by scope. Contact us for a free estimate."),
        ("Do you build custom cabinets in {loc_name}?".replace("{loc_name}", loc_name),
         f"Yes. aMaximum Construction builds and installs custom cabinets for kitchens, bathrooms, laundry rooms, and built-in entertainment units throughout {loc_name}. We work with your design vision and budget."),
    ]
    content = f"""\
    <h2>Professional Carpenter Services in {loc_name}</h2>
    <p>aMaximum Construction provides skilled carpentry services throughout {loc_name} and the GTA. From precision trim work to custom built-ins, our experienced carpenters deliver craftsmanship that elevates any space.</p>

    <h2>Carpentry Services in {loc_name}</h2>
    <ul>
      <li><strong>Trim &amp; Moulding</strong> — Baseboards, crown moulding, door casings, wainscoting</li>
      <li><strong>Custom Cabinetry</strong> — Kitchen, bathroom, laundry, and storage cabinets</li>
      <li><strong>Built-In Shelving</strong> — Bookcases, entertainment units, closet systems</li>
      <li><strong>Staircase Work</strong> — Railings, balusters, treads, newel posts</li>
      <li><strong>Door Installation</strong> — Interior and exterior doors, frames, hardware</li>
      <li><strong>Finish Carpentry</strong> — All interior finishing details for renovations</li>
      <li><strong>Deck &amp; Outdoor Structures</strong> — Cedar decks, pergolas, privacy screens</li>
    </ul>

    <h2>Why Choose aMaximum for Carpentry in {loc_name}?</h2>
    <p>Our carpenters bring decades of combined experience to every project in {loc_name}. We use quality materials, precise techniques, and take pride in clean, lasting results. All carpentry work is backed by our workmanship warranty.</p>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Carpenter Services in {loc_name} | Custom Carpentry | aMaximum Construction",
        meta_desc=f"Professional carpenter services in {loc_name}. Custom cabinets, trim, built-ins, staircases & finish carpentry. Licensed, insured. Free quotes.",
        h1=f"Carpenter Services in {loc_name}",
        hero_sub=f"Skilled carpentry contractor in {loc_name}. Custom cabinetry, trim work, built-ins — quality craftsmanship guaranteed.",
        content_html=content,
        cta_h2=f"Get a Carpentry Quote in {loc_name}",
        cta_p="Contact us for a free consultation. We'll discuss your project and provide a detailed written quote.",
        location_name=loc_name,
        service_type="Carpentry",
        service_label="Carpenter Services",
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  HANDYMAN — LOCATION VARIANTS (neighbourhoods)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_handyman_location(loc_name, slug):
    faqs = [
        (f"What handyman services are available in {loc_name}?",
         f"aMaximum Construction offers a full range of handyman services in {loc_name} including drywall repair, painting, fixture installation, furniture assembly, minor plumbing, and general home repairs."),
        (f"How much does a handyman cost in {loc_name}?",
         f"Handyman rates in {loc_name} typically start at $80–$120/hour, with minimum call-out fees. Many small jobs are flat-rated. Contact us for a free quote on your specific tasks."),
        (f"Can I book a handyman for same-week service in {loc_name}?",
         f"Yes, aMaximum Construction often has availability within the same week for handyman work in {loc_name}. Contact us to check current scheduling."),
    ]
    content = f"""\
    <h2>Reliable Handyman Services in {loc_name}</h2>
    <p>aMaximum Construction provides trusted handyman services throughout {loc_name}. Our skilled tradespeople handle the to-do list items that pile up — repairs, installations, minor renovations, and general maintenance — completed efficiently and to a high standard.</p>

    <h2>Common Handyman Tasks in {loc_name}</h2>
    <ul>
      <li><strong>Drywall Repair</strong> — Holes, cracks, water damage patches</li>
      <li><strong>Painting</strong> — Interior and exterior painting, touch-ups</li>
      <li><strong>Fixture Installation</strong> — Lights, ceiling fans, faucets, toilets</li>
      <li><strong>Door &amp; Window Repairs</strong> — Adjustments, weatherstripping, lock installation</li>
      <li><strong>Furniture Assembly</strong> — IKEA, flat-pack, and custom assembly</li>
      <li><strong>Shelving &amp; Mounting</strong> — TV mounting, shelves, picture hanging</li>
      <li><strong>Minor Plumbing</strong> — Leaks, fixture swaps, drain cleaning</li>
      <li><strong>Caulking &amp; Sealing</strong> — Bathroom, kitchen, exterior</li>
      <li><strong>General Repairs</strong> — Whatever's on your list</li>
    </ul>

    <h2>Serving {loc_name} and Surrounding Areas</h2>
    <p>Our handyman team serves {loc_name} and nearby communities across the GTA. We arrive on time, work cleanly, and leave your home better than we found it. No job is too small.</p>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Handyman Services in {loc_name} | aMaximum Construction",
        meta_desc=f"Reliable handyman services in {loc_name}. Drywall repair, painting, fixture installation, furniture assembly & more. Licensed, insured. Book today.",
        h1=f"Handyman Services in {loc_name}",
        hero_sub=f"Trusted handyman serving {loc_name}. All repairs and installations handled quickly and professionally.",
        content_html=content,
        cta_h2=f"Book a Handyman in {loc_name}",
        cta_p="Contact us to schedule your handyman visit. We'll handle your full to-do list efficiently.",
        location_name=loc_name,
        service_type="Handyman",
        service_label="Handyman Services",
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  HANDYMAN SPECIALTY SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

def gen_handyman_specialty(service_name, slug, desc, service_items, faqs_data):
    faqs = [(q, a) for q, a in faqs_data]
    content = f"""\
    <h2>{service_name} — aMaximum Construction</h2>
    <p>{desc}</p>

    <h2>What's Included</h2>
    <ul>
      {"".join(f"<li>{item}</li>" for item in service_items)}
    </ul>

    <h2>Serving Toronto &amp; GTA</h2>
    <p>aMaximum Construction provides {service_name.lower()} throughout Toronto, North York, Markham, Richmond Hill, Vaughan, Aurora, Newmarket, and surrounding GTA communities. Fast scheduling, transparent pricing, quality guaranteed.</p>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"{service_name} | Toronto GTA | aMaximum Construction",
        meta_desc=f"Professional {service_name.lower()} in Toronto & GTA. Licensed, insured handyman contractor. Fast scheduling, transparent pricing. Free quotes.",
        h1=service_name,
        hero_sub=f"Licensed {service_name.lower()} serving Toronto & GTA. Quality work, fair prices, fast turnaround.",
        content_html=content,
        cta_h2=f"Book {service_name} Today",
        cta_p="Contact us for a free quote. We serve Toronto, North York, Markham, Richmond Hill, Vaughan, and all GTA communities.",
        location_name="Toronto & GTA",
        service_type=service_name,
        service_label=service_name,
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  DECK VARIANTS
# ═══════════════════════════════════════════════════════════════════════════════

def gen_deck_railing(loc_name, slug):
    faqs = [
        (f"What deck railing options are available in {loc_name}?",
         f"aMaximum Construction installs wood, aluminum, glass, cable, and composite railings for decks in {loc_name}. We help you choose the right style for your home and budget."),
        (f"Do deck railings require a permit in {loc_name}?",
         f"Deck railings over 600mm (24\") from grade require a building permit in Ontario. aMaximum Construction manages permit applications for railing projects in {loc_name}."),
        (f"How much do deck railings cost in {loc_name}?",
         f"Deck railing installation in {loc_name} typically ranges from $150–$400+ per linear foot depending on material. Wood and aluminum are most affordable; glass and cable are premium options."),
    ]
    content = f"""\
    <h2>Deck Railing Installation in {loc_name}</h2>
    <p>aMaximum Construction installs custom deck railings throughout {loc_name} and the GTA. We offer a full range of railing styles — from classic wood to modern glass — all built to Ontario Building Code specifications and designed to complement your home's exterior.</p>

    <h2>Deck Railing Options in {loc_name}</h2>
    <ul>
      <li><strong>Wood Railings</strong> — Cedar or pressure-treated, classic and affordable</li>
      <li><strong>Aluminum Railings</strong> — Low-maintenance, durable, powder-coated finishes</li>
      <li><strong>Glass Railings</strong> — Tempered glass panels for unobstructed views</li>
      <li><strong>Cable Railings</strong> — Stainless steel cables for a modern, open look</li>
      <li><strong>Composite Railings</strong> — Low-maintenance with a natural wood appearance</li>
      <li><strong>Wrought Iron</strong> — Traditional decorative railings for classic homes</li>
    </ul>

    <h2>Code-Compliant Railing Installation in {loc_name}</h2>
    <p>All deck railings installed by aMaximum Construction in {loc_name} meet Ontario Building Code requirements for height, balusters spacing, and structural attachment. We manage permits and pass all required inspections.</p>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Deck Railing Installation in {loc_name} | aMaximum Construction",
        meta_desc=f"Custom deck railing installation in {loc_name}. Wood, aluminum, glass & cable railings. Code-compliant, licensed contractor. Free quotes.",
        h1=f"Deck Railing Installation in {loc_name}",
        hero_sub=f"Custom deck railings in {loc_name}. All materials and styles, code-compliant, professionally installed.",
        content_html=content,
        cta_h2=f"Get a Deck Railing Quote in {loc_name}",
        cta_p="Contact us for a free consultation and quote. We'll help you choose the right railing style for your home.",
        location_name=loc_name,
        service_type="Deck Railing",
        service_label="Deck Railing Installation",
        faqs=faqs,
    )


def gen_deck_contractor(loc_name, slug):
    faqs = [
        (f"How much does a deck cost in {loc_name}?",
         f"Deck construction in {loc_name} typically ranges from $15,000–$30,000 for a standard pressure-treated deck and $30,000–$60,000+ for composite or multi-level decks. Contact aMaximum Construction for a free, detailed quote."),
        (f"Do I need a permit for a deck in {loc_name}?",
         f"Yes, decks over 24 inches from grade require a building permit in Ontario. aMaximum Construction manages permit applications for all deck projects in {loc_name}."),
        (f"How long does deck construction take in {loc_name}?",
         f"A standard deck in {loc_name} typically takes 1–3 weeks to build once permits are approved. Larger multi-level decks may take 3–5 weeks. We provide a firm timeline upfront."),
    ]
    content = f"""\
    <h2>Expert Deck Contractor in {loc_name}</h2>
    <p>aMaximum Construction is a licensed deck contractor serving {loc_name} and the Greater Toronto Area. We design and build custom decks — pressure-treated, composite, cedar, and multi-level — that are built to last and built to code.</p>

    <h2>Deck Building Services in {loc_name}</h2>
    <ul>
      <li><strong>Pressure-Treated Decks</strong> — Durable and affordable, ideal for {loc_name} climate</li>
      <li><strong>Composite Decks</strong> — Trex, TimberTech, and other premium composites</li>
      <li><strong>Cedar Decks</strong> — Natural beauty with excellent weather resistance</li>
      <li><strong>Multi-Level Decks</strong> — Custom designs maximizing your outdoor space</li>
      <li><strong>Deck Railings</strong> — Wood, aluminum, glass, and cable options</li>
      <li><strong>Pergolas &amp; Shade Structures</strong> — Extend your outdoor living season</li>
      <li><strong>Deck Repairs &amp; Refinishing</strong> — Restore your existing deck</li>
    </ul>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Deck Contractor in {loc_name} | Custom Deck Builder | aMaximum Construction",
        meta_desc=f"Licensed deck contractor in {loc_name}. Custom decks — pressure-treated, composite, cedar, multi-level. Permit-managed. Free quotes.",
        h1=f"Deck Contractor in {loc_name}",
        hero_sub=f"Licensed deck builder serving {loc_name}. Custom designs, quality materials, code-compliant construction.",
        content_html=content,
        cta_h2=f"Get a Free Deck Quote in {loc_name}",
        cta_p="Contact us for a free in-person consultation and detailed written quote for your deck project.",
        location_name=loc_name,
        service_type="Deck Construction",
        service_label="Deck Building",
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERLOCKING / PAVING
# ═══════════════════════════════════════════════════════════════════════════════

def gen_interlocking(loc_name, slug):
    faqs = [
        (f"What interlocking services does aMaximum offer in {loc_name}?",
         f"aMaximum Construction installs interlocking stone driveways, patios, walkways, pool surrounds, and retaining walls throughout {loc_name}. We work with concrete pavers, natural stone, and brick."),
        (f"How much does interlocking cost in {loc_name}?",
         f"Interlocking installation in {loc_name} typically ranges from $15–$35+ per square foot depending on material and complexity. Contact us for a free site assessment and detailed quote."),
        ("How long does interlocking installation take?",
         "Most residential interlocking projects take 2–5 days. Larger driveways or complex designs may take up to 2 weeks. Proper base preparation is critical for longevity — we never rush this step."),
    ]
    content = f"""\
    <h2>Interlocking Stone Services in {loc_name}</h2>
    <p>aMaximum Construction designs and installs premium interlocking stone driveways, patios, walkways, and outdoor features throughout {loc_name}. Our experienced crew delivers beautiful, durable results using quality pavers and proper base construction techniques.</p>

    <h2>Interlocking Services in {loc_name}</h2>
    <ul>
      <li><strong>Interlocking Driveways</strong> — Concrete pavers, natural stone, brick</li>
      <li><strong>Patio Installation</strong> — Custom patio designs for outdoor entertaining</li>
      <li><strong>Walkways &amp; Pathways</strong> — Front entry, garden, and pool pathways</li>
      <li><strong>Retaining Walls</strong> — Structural and decorative stone walls</li>
      <li><strong>Steps &amp; Landings</strong> — Natural stone and concrete paver steps</li>
      <li><strong>Pool Surrounds</strong> — Slip-resistant, durable pool deck paving</li>
      <li><strong>Repairs &amp; Releveling</strong> — Sunken or shifted paver restoration</li>
    </ul>

    <h2>Quality Interlocking Installation in {loc_name}</h2>
    <p>Long-lasting interlocking starts with proper base preparation — excavation, compacted granular base, and sand bedding. aMaximum Construction never cuts corners on base work. Our installations are designed to handle {loc_name}'s freeze-thaw cycles and remain level and stable for decades.</p>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Interlocking Stone Services in {loc_name} | aMaximum Construction",
        meta_desc=f"Professional interlocking stone installation in {loc_name}. Driveways, patios, walkways & retaining walls. Licensed contractor. Free quotes.",
        h1=f"Interlocking Stone Services in {loc_name}",
        hero_sub=f"Premium interlocking contractor in {loc_name}. Driveways, patios, walkways — built to last.",
        content_html=content,
        cta_h2=f"Get an Interlocking Quote in {loc_name}",
        cta_p="Contact us for a free site assessment and detailed quote for your interlocking project.",
        location_name=loc_name,
        service_type="Interlocking Stone",
        service_label="Interlocking Installation",
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  CHRISTMAS LIGHTS
# ═══════════════════════════════════════════════════════════════════════════════

def gen_christmas_lights(loc_name, slug):
    faqs = [
        (f"When should I book Christmas light installation in {loc_name}?",
         f"Book by late October or early November for best availability. aMaximum Construction's {loc_name} Christmas light installation slots fill quickly — contact us early to secure your preferred date."),
        (f"What does Christmas light installation cost in {loc_name}?",
         f"Professional Christmas light installation in {loc_name} typically ranges from $500–$2,500+ depending on home size and design complexity. We provide a free quote after assessing your property."),
        ("Do you provide the lights or do I supply them?",
         "aMaximum Construction provides professional-grade LED lights, clips, and all installation hardware. We also offer takedown and storage services so your lights are ready again next year."),
        ("Do you take the lights down after the season?",
         "Yes. Our seasonal package includes post-season takedown and storage of lights. We'll hang them again next year — just schedule your installation for the following season."),
    ]
    content = f"""\
    <h2>Professional Christmas Light Installation in {loc_name}</h2>
    <p>aMaximum Construction provides professional Christmas light installation services throughout {loc_name} and the GTA. Our team designs, installs, and takes down beautiful holiday displays — safely and efficiently — so you can enjoy the season without the hassle.</p>

    <h2>Our Christmas Light Services in {loc_name}</h2>
    <ul>
      <li><strong>Custom Light Design</strong> — Roofline, trees, shrubs, pathways, and more</li>
      <li><strong>Professional-Grade LED Lights</strong> — Brighter, more energy-efficient than store-bought</li>
      <li><strong>Safe Installation</strong> — Proper clips, no damage to your home</li>
      <li><strong>Post-Season Takedown</strong> — We remove everything when the season ends</li>
      <li><strong>Storage</strong> — Lights stored and ready for next year</li>
      <li><strong>Commercial Displays</strong> — Business and commercial property holiday lighting</li>
    </ul>

    <h2>Why Professional Installation in {loc_name}?</h2>
    <p>Working on ladders and rooftops during winter in {loc_name} is dangerous. Our insured crew handles all the height work safely, uses professional-grade equipment, and delivers a result that looks far better than typical DIY installations. Spend the season with your family, not on a ladder.</p>

    <h2>Frequently Asked Questions</h2>
    <dl>
      {"".join(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>" for q, a in faqs)}
    </dl>"""

    return build_page(
        slug=slug,
        meta_title=f"Christmas Light Installation in {loc_name} | aMaximum Construction",
        meta_desc=f"Professional Christmas light installation in {loc_name}. Custom designs, LED lights, takedown & storage included. Book early — slots fill fast.",
        h1=f"Christmas Light Installation in {loc_name}",
        hero_sub=f"Professional holiday light installation serving {loc_name}. We handle setup, takedown & storage.",
        content_html=content,
        cta_h2=f"Book Christmas Lights in {loc_name}",
        cta_p="Contact us for a free quote. Book early — holiday season slots fill up fast.",
        location_name=loc_name,
        service_type="Christmas Light Installation",
        service_label="Christmas Light Installation",
        faqs=faqs,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  SIMPLE COMPANY / INFO PAGES
# ═══════════════════════════════════════════════════════════════════════════════

def gen_simple_page(slug, title, meta_desc, h1, hero_sub, content_html):
    canonical = f"{BASE_URL}/{slug}/"
    schema = json.dumps([{
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "aMaximum Construction",
        "url": canonical,
        "telephone": PHONE,
        "email": EMAIL,
    }], ensure_ascii=False, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{meta_desc}">
  <meta name="robots" content="index, follow">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="aMaximum Construction">
  <link rel="canonical" href="{canonical}">
  <title>{title}</title>
  <link rel="stylesheet" href="/css/styles.css">
  <script type="application/ld+json">
{schema}
  </script>
</head>
<body>
{NAV}
<div class="page-hero">
  <h1>{h1}</h1>
  <p>{hero_sub}</p>
</div>
<div class="container">
  <div class="content">
{content_html}
  </div>
  <div class="cta-section">
    <h2>Ready to Get Started?</h2>
    <p>Contact aMaximum Construction for a free consultation and quote.</p>
    <a href="/#contact" class="btn">Contact Us</a>
  </div>
</div>
{FOOTER}
<script>
const menuBtn = document.getElementById('menuBtn');
const siteNav = document.getElementById('siteNav');
if (menuBtn && siteNav) {{
  menuBtn.addEventListener('click', () => {{
    const exp = menuBtn.getAttribute('aria-expanded') === 'true';
    menuBtn.setAttribute('aria-expanded', !exp);
    siteNav.classList.toggle('open');
  }});
}}
</script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════════════════
#  GENERATE ALL PAGES
# ═══════════════════════════════════════════════════════════════════════════════

pages = []

# ── BATHROOM RENOVATION ───────────────────────────────────────────────────────
pages.append(("bathroom-renovation-aurora",           gen_bathroom("Aurora", "bathroom-renovation-aurora")))
pages.append(("bathroom-renovation-richmond-hill",    gen_bathroom("Richmond Hill", "bathroom-renovation-richmond-hill")))
pages.append(("bathroom-renovation-mississauga",      gen_bathroom("Mississauga", "bathroom-renovation-mississauga")))
pages.append(("interior-bathroom-renovation-toronto", gen_bathroom("Toronto", "interior-bathroom-renovation-toronto")))
pages.append(("bathrooms-renovation-in-north-york",   gen_bathroom("North York", "bathrooms-renovation-in-north-york")))
pages.append(("basement-bathroom-renovation-richmond-hill", gen_bathroom("Richmond Hill", "basement-bathroom-renovation-richmond-hill")))

# ── BASEMENT ──────────────────────────────────────────────────────────────────
pages.append(("best-basement-renovation-service-in-aurora",    gen_best_basement("Aurora", "best-basement-renovation-service-in-aurora")))
pages.append(("best-basement-renovation-service-in-newmarket", gen_best_basement("Newmarket", "best-basement-renovation-service-in-newmarket")))
pages.append(("best-basement-renovation-service-richmond-hill",gen_best_basement("Richmond Hill", "best-basement-renovation-service-richmond-hill")))
pages.append(("basement-and-bathroom-renovation-in-north-york",gen_best_basement("North York", "basement-and-bathroom-renovation-in-north-york")))
pages.append(("basement-renovation-in-toronto",                gen_best_basement("Toronto", "basement-renovation-in-toronto")))
pages.append(("1-basement-renovation-near-me",                 gen_best_basement("Toronto & GTA", "1-basement-renovation-near-me")))

# ── RENOVATION SERVICES ───────────────────────────────────────────────────────
pages.append(("renovation-service",                  gen_renovation_services("Toronto & GTA", "renovation-service")))
pages.append(("renovation-services-in-north-york",   gen_renovation_services("North York", "renovation-services-in-north-york")))
pages.append(("renovation-services-in-vaughan",      gen_renovation_services("Vaughan", "renovation-services-in-vaughan")))
pages.append(("renovation-services-in-toronto-gta",  gen_renovation_services("Toronto & GTA", "renovation-services-in-toronto-gta")))
pages.append(("renovation-services-in-richmond-hill",gen_renovation_services("Richmond Hill", "renovation-services-in-richmond-hill")))
pages.append(("renovation-services-in-aurora",       gen_renovation_services("Aurora", "renovation-services-in-aurora")))
pages.append(("renovation-services-in-newmarket",    gen_renovation_services("Newmarket", "renovation-services-in-newmarket")))

# ── DEMOLITION ────────────────────────────────────────────────────────────────
pages.append(("demolition-services",                      gen_demolition("Toronto & GTA", "demolition-services")))
pages.append(("demolition-services-oakville",             gen_demolition("Oakville", "demolition-services-oakville")))
pages.append(("demolition-services-scarborough",          gen_demolition("Scarborough", "demolition-services-scarborough")))
pages.append(("demolition-services-etobicoke",            gen_demolition("Etobicoke", "demolition-services-etobicoke")))
pages.append(("demolition-services-mississauga",          gen_demolition("Mississauga", "demolition-services-mississauga")))
pages.append(("demolition-services-nobleton",             gen_demolition("Nobleton", "demolition-services-nobleton")))
pages.append(("demolition-service-brampton",              gen_demolition("Brampton", "demolition-service-brampton")))
pages.append(("demolition-service-in-whitchurch-stouffville", gen_demolition("Whitchurch-Stouffville", "demolition-service-in-whitchurch-stouffville")))
pages.append(("demolition-service-in-king-city",          gen_demolition("King City", "demolition-service-in-king-city")))

# ── CARPENTER ─────────────────────────────────────────────────────────────────
pages.append(("carpenter-services-brampton",    gen_carpenter("Brampton", "carpenter-services-brampton")))
pages.append(("carpenter-services-mississauga", gen_carpenter("Mississauga", "carpenter-services-mississauga")))
pages.append(("carpenter-services",             gen_carpenter("Toronto & GTA", "carpenter-services")))

# ── GENERAL CONTRACTOR EXTRAS ─────────────────────────────────────────────────
pages.append(("general-contractor-in-king-city",            gen_renovation_services("King City", "general-contractor-in-king-city")))
pages.append(("general-contractor-in-nobleton",             gen_renovation_services("Nobleton", "general-contractor-in-nobleton")))
pages.append(("general-contractor-in-whitchurch-stouffville", gen_renovation_services("Whitchurch-Stouffville", "general-contractor-in-whitchurch-stouffville")))
pages.append(("general-contractor-services",                gen_renovation_services("Toronto & GTA", "general-contractor-services")))
pages.append(("general-contractor-services-near-me",        gen_renovation_services("Toronto & GTA", "general-contractor-services-near-me")))

# ── HANDYMAN SPECIALTY ────────────────────────────────────────────────────────
pages.append(("handyman-drywall-repair", gen_handyman_specialty(
    "Drywall Repair Services", "handyman-drywall-repair",
    "aMaximum Construction provides professional drywall repair services throughout Toronto and the GTA. From small nail holes to large water-damaged sections, our skilled team patches, tapes, and finishes drywall to a seamless result.",
    ["Nail and screw hole patching", "Crack repair and taping", "Water damage patch and restoration",
     "Large hole repair and backing installation", "Texture matching and finishing", "Full drywall replacement", "Smooth skim coat finish"],
    [("How much does drywall repair cost in Toronto?",
      "Small patches (under 6 inches) typically cost $100–$200. Medium repairs $200–$500. Large or water-damaged sections are quoted by scope. Contact us for a free assessment."),
     ("Can you match existing texture after drywall repair?",
      "Yes. Our team is experienced in matching orange peel, knockdown, skip trowel, and smooth finishes. We take time to blend the repair seamlessly with surrounding walls."),
     ("How long does drywall repair take?",
      "Most repairs are completed in 1–2 visits. Compound needs 24 hours to dry between coats. Large repairs may take 2–3 days for proper drying and finishing.")]
)))

pages.append(("handyman-furniture-assembly", gen_handyman_specialty(
    "Furniture Assembly Services", "handyman-furniture-assembly",
    "aMaximum Construction provides professional furniture assembly services in Toronto and the GTA. We assemble IKEA, flat-pack, and any brand of furniture quickly and correctly — saving you time and frustration.",
    ["IKEA furniture assembly", "Flat-pack and ready-to-assemble furniture", "Office furniture and desks",
     "Wardrobes and closet systems", "Beds and bed frames", "Bookshelves and cabinets", "Outdoor furniture assembly"],
    [("How much does furniture assembly cost in Toronto?",
      "Furniture assembly typically costs $80–$150 per hour. Simple pieces like a bookshelf may take under an hour; complex wardrobes or multiple pieces may take 2–4 hours. We provide estimates upfront."),
     ("Do you assemble IKEA furniture?",
      "Yes — IKEA assembly is one of our most common requests. We assemble all IKEA product lines including PAX wardrobes, KALLAX shelving, MALM beds, and kitchen units."),
     ("Can you take away packaging and cardboard?",
      "Yes, we remove and dispose of all packaging materials at no extra charge.")]
)))

pages.append(("handyman-painting-services", gen_handyman_specialty(
    "Handyman Painting Services", "handyman-painting-services",
    "aMaximum Construction provides professional interior and exterior painting services throughout Toronto and the GTA. From single rooms to whole-home repaints, our painters deliver clean, smooth, lasting results.",
    ["Interior room painting", "Exterior house painting", "Trim, baseboard and door painting",
     "Ceiling painting", "Cabinet painting and refinishing", "Touch-ups and spot painting", "Wallpaper removal and painting"],
    [("How much does interior painting cost in Toronto?",
      "Interior painting in Toronto typically ranges from $300–$700 per room depending on size and condition. Whole-home repaints are quoted by square footage. Contact us for a free, itemized quote."),
     ("Do you move furniture before painting?",
      "We move small furniture and protect large pieces with drop cloths. We recommend removing fragile or valuable items before our crew arrives."),
     ("What paint brands do you use?",
      "We use premium paints from Benjamin Moore, Sherwin-Williams, and other quality brands. We're happy to work with paint you've selected or recommend the best product for your surface.")]
)))

pages.append(("electrical-handyman-services", gen_handyman_specialty(
    "Electrical Handyman Services", "electrical-handyman-services",
    "aMaximum Construction provides licensed electrical handyman services throughout Toronto and the GTA. We handle residential electrical repairs, fixture installation, and upgrades — all work performed or supervised by licensed electricians.",
    ["Light fixture installation and replacement", "Ceiling fan installation", "Outlet and switch replacement",
     "GFCI outlet installation", "Dimmer switch installation", "Under-cabinet lighting", "Electrical troubleshooting"],
    [("Are your electricians licensed in Ontario?",
      "Yes. All electrical work is performed or directly supervised by ESA-licensed electricians. Permits are pulled for work that requires them."),
     ("How much does electrical handyman work cost in Toronto?",
      "Simple fixture swaps start at $120–$200. Ceiling fan installation $150–$250. GFCI outlet installation $100–$150 per outlet. Rates vary by complexity — contact us for a free quote."),
     ("Can you install a ceiling fan where there's no existing fixture?",
      "Yes, we can install a new electrical box and run wiring to support a ceiling fan where none existed. This may require a permit depending on scope.")]
)))

pages.append(("handyman-plumbing-services", gen_handyman_specialty(
    "Handyman Plumbing Services", "handyman-plumbing-services",
    "aMaximum Construction provides handyman plumbing services for minor repairs and fixture replacements throughout Toronto and the GTA. Our skilled tradespeople handle everyday plumbing tasks quickly and professionally.",
    ["Faucet replacement and repair", "Toilet installation and repair", "Showerhead replacement",
     "Under-sink plumbing", "Drain cleaning and unclogging", "Shut-off valve replacement", "Caulking around tubs and sinks"],
    [("What plumbing tasks can a handyman handle in Toronto?",
      "Handyman plumbing covers fixture swaps, minor leaks, toilet repairs, faucet installation, and drain clearing. For new rough-in plumbing or major pipe work, a licensed plumber is required — we can coordinate that too."),
     ("How much does handyman plumbing cost in Toronto?",
      "Faucet installation typically costs $150–$250. Toilet replacement $200–$350. Minor leak repairs $100–$200. Prices vary by complexity — contact us for a free quote."),
     ("Do you handle emergency plumbing calls?",
      "For burst pipes or major flooding, call a licensed plumber immediately. For non-emergency fixture issues, aMaximum Construction can typically schedule within 1–3 business days.")]
)))

# ── HANDYMAN LOCATIONS (neighbourhoods) ───────────────────────────────────────
pages.append(("handyman-services-in-markham",    gen_handyman_location("Markham", "handyman-services-in-markham")))
pages.append(("handyman-services-bayview-glen",  gen_handyman_location("Bayview Glen", "handyman-services-bayview-glen")))
pages.append(("handyman-services-king-creek",    gen_handyman_location("King Creek", "handyman-services-king-creek")))
pages.append(("handyman-services-unionville",    gen_handyman_location("Unionville", "handyman-services-unionville")))
pages.append(("handyman-services-in-thornhill-woods", gen_handyman_location("Thornhill Woods", "handyman-services-in-thornhill-woods")))
pages.append(("handyman-services-in-glenville",  gen_handyman_location("Glenville", "handyman-services-in-glenville")))
pages.append(("handyman-services-in-maple",      gen_handyman_location("Maple", "handyman-services-in-maple")))

# ── DECK EXTRAS ───────────────────────────────────────────────────────────────
pages.append(("deck-railing-vaughan",              gen_deck_railing("Vaughan", "deck-railing-vaughan")))
pages.append(("deck-railing-builder-markham",      gen_deck_railing("Markham", "deck-railing-builder-markham")))
pages.append(("deck-railing-installation-in-king-city", gen_deck_railing("King City", "deck-railing-installation-in-king-city")))
pages.append(("deck-railings-toronto",             gen_deck_railing("Toronto", "deck-railings-toronto")))
pages.append(("deck-contractor-concord",           gen_deck_contractor("Concord", "deck-contractor-concord")))
pages.append(("deck-contractor-kleinburg",         gen_deck_contractor("Kleinburg", "deck-contractor-kleinburg")))
pages.append(("deck-contractor-in-thornhill",      gen_deck_contractor("Thornhill", "deck-contractor-in-thornhill")))
pages.append(("deck-contractor-east-gwillimbury",  gen_deck_contractor("East Gwillimbury", "deck-contractor-east-gwillimbury")))
pages.append(("wood-deck-repair-in-unionville",    gen_deck_contractor("Unionville", "wood-deck-repair-in-unionville")))

# ── INTERLOCKING / PAVING ─────────────────────────────────────────────────────
pages.append(("interlocking-paver-services",               gen_interlocking("Toronto & GTA", "interlocking-paver-services")))
pages.append(("interlocking-stone-services-north-york",    gen_interlocking("North York", "interlocking-stone-services-north-york")))
pages.append(("interlock-paving-contractor-richmond-hill", gen_interlocking("Richmond Hill", "interlock-paving-contractor-richmond-hill")))
pages.append(("interlock-paving-contractor-in-east-gwillimbury", gen_interlocking("East Gwillimbury", "interlock-paving-contractor-in-east-gwillimbury")))

# ── CHRISTMAS LIGHTS ──────────────────────────────────────────────────────────
pages.append(("christmas-lights-installation-in-forest-hill",   gen_christmas_lights("Forest Hill", "christmas-lights-installation-in-forest-hill")))
pages.append(("christmas-lights-installation-in-richmond-hill",  gen_christmas_lights("Richmond Hill", "christmas-lights-installation-in-richmond-hill")))
pages.append(("christmas-lights-installation-toronto-gta",       gen_christmas_lights("Toronto & GTA", "christmas-lights-installation-toronto-gta")))
pages.append(("professional-christmas-lights-installer-aurora",  gen_christmas_lights("Aurora", "professional-christmas-lights-installer-aurora")))

# ── FENCE ─────────────────────────────────────────────────────────────────────
pages.append(("fence-installer-aurora", gen_simple_page(
    "fence-installer-aurora",
    "Fence Installer in Aurora | aMaximum Construction",
    "Professional fence installation in Aurora. Wood, vinyl, chain-link & aluminum fences. Licensed contractor, free quotes.",
    "Fence Installer in Aurora",
    "Licensed fence installation contractor serving Aurora. All fence types, permit-managed.",
    """    <h2>Professional Fence Installation in Aurora</h2>
    <p>aMaximum Construction installs all types of fences throughout Aurora — wood privacy fences, vinyl, aluminum, chain-link, and decorative options. Our crew handles everything from permits to post-setting to final finishing.</p>
    <h2>Fence Types We Install in Aurora</h2>
    <ul>
      <li><strong>Wood Fences</strong> — Cedar privacy, picket, and board-on-board</li>
      <li><strong>Vinyl Fences</strong> — Low-maintenance, weather-resistant</li>
      <li><strong>Aluminum Fences</strong> — Decorative, durable, powder-coated</li>
      <li><strong>Chain-Link Fences</strong> — Practical and cost-effective</li>
      <li><strong>Composite Fences</strong> — Realistic wood look with low maintenance</li>
    </ul>
    <p>All fence installations in Aurora comply with local zoning setback requirements. aMaximum Construction advises on permit requirements and manages applications when needed.</p>"""
)))

# ── EXCAVATION ────────────────────────────────────────────────────────────────
pages.append(("excavation-services", gen_simple_page(
    "excavation-services",
    "Excavation Services Toronto & GTA | aMaximum Construction",
    "Professional excavation services in Toronto & GTA. Foundation excavation, grading, trenching & site prep. Licensed contractor. Free quotes.",
    "Excavation Services in Toronto & GTA",
    "Licensed excavation contractor serving Toronto and the GTA. Foundation, grading, trenching — done right.",
    """    <h2>Professional Excavation Services</h2>
    <p>aMaximum Construction provides residential and commercial excavation services throughout Toronto and the GTA. Our experienced team operates modern equipment and follows strict safety protocols for every dig.</p>
    <h2>Excavation Services We Offer</h2>
    <ul>
      <li><strong>Foundation Excavation</strong> — New home and addition foundations</li>
      <li><strong>Basement Underpinning</strong> — Lowering basement floors for added ceiling height</li>
      <li><strong>Site Grading</strong> — Proper drainage slope away from foundations</li>
      <li><strong>Trenching</strong> — Utilities, drainage, and waterproofing systems</li>
      <li><strong>Pool Excavation</strong> — In-ground pool preparation</li>
      <li><strong>Debris &amp; Fill Removal</strong> — Hauling and disposal of excavated material</li>
    </ul>
    <p>All excavation work includes locate services (Ontario One Call) before any digging begins. We operate safely around utilities and neighbouring structures.</p>"""
)))

# ── PAVING COMPANY ────────────────────────────────────────────────────────────
pages.append(("paving-company", gen_interlocking("Toronto & GTA", "paving-company")))

# ── PRIVACY SCREEN ────────────────────────────────────────────────────────────
pages.append(("privacy-screen-installation-in-north-york", gen_simple_page(
    "privacy-screen-installation-in-north-york",
    "Privacy Screen Installation in North York | aMaximum Construction",
    "Custom privacy screen installation in North York. Deck privacy walls, lattice, slatted screens. Licensed contractor. Free quotes.",
    "Privacy Screen Installation in North York",
    "Custom privacy screens for decks and outdoor spaces in North York.",
    """    <h2>Privacy Screen Installation in North York</h2>
    <p>aMaximum Construction designs and installs custom privacy screens for decks, patios, and outdoor spaces throughout North York. Whether you want to block a neighbour's sightline, create a shaded area, or add a design feature, we build screens that are both functional and attractive.</p>
    <h2>Privacy Screen Options in North York</h2>
    <ul>
      <li><strong>Slatted Wood Screens</strong> — Cedar or pressure-treated with adjustable spacing</li>
      <li><strong>Lattice Panels</strong> — Classic look, ideal for climbing plants</li>
      <li><strong>Solid Privacy Walls</strong> — Full-height panels for maximum privacy</li>
      <li><strong>Aluminum Screens</strong> — Low-maintenance, durable, powder-coated</li>
      <li><strong>Frosted Glass Panels</strong> — Modern look with light diffusion</li>
    </ul>
    <p>All privacy screens are custom-built to your deck dimensions and designed to complement your home's exterior. aMaximum Construction serves North York, Toronto, and all GTA communities.</p>"""
)))

# ── LANDSCAPING ───────────────────────────────────────────────────────────────
pages.append(("landscaping-services-toronto", gen_simple_page(
    "landscaping-services-toronto",
    "Landscaping Services in Toronto | aMaximum Construction",
    "Professional landscaping services in Toronto. Interlocking, grading, garden design, retaining walls & more. Licensed contractor. Free quotes.",
    "Landscaping Services in Toronto",
    "Complete landscaping solutions for Toronto homeowners.",
    """    <h2>Professional Landscaping Services in Toronto</h2>
    <p>aMaximum Construction provides comprehensive landscaping services throughout Toronto and the GTA. From interlocking stone driveways to full backyard transformations, our team creates beautiful, low-maintenance outdoor spaces tailored to your lifestyle.</p>
    <h2>Landscaping Services We Offer in Toronto</h2>
    <ul>
      <li><strong>Interlocking Driveways &amp; Patios</strong> — Concrete pavers, natural stone, brick</li>
      <li><strong>Retaining Walls</strong> — Structural and decorative stone walls</li>
      <li><strong>Grading &amp; Drainage</strong> — Proper slope away from foundations</li>
      <li><strong>Garden Design</strong> — Planting beds, borders, mulching</li>
      <li><strong>Sod Installation</strong> — Fresh lawn installation and grading</li>
      <li><strong>Walkways &amp; Steps</strong> — Natural stone and concrete paver pathways</li>
    </ul>"""
)))

# ── CANOPY ────────────────────────────────────────────────────────────────────
pages.append(("canopy", gen_simple_page(
    "canopy",
    "Canopy Installation Toronto & GTA | aMaximum Construction",
    "Professional canopy and pergola installation in Toronto & GTA. Custom structures for decks, patios & commercial spaces. Free quotes.",
    "Canopy & Pergola Installation in Toronto & GTA",
    "Custom canopy and pergola installation serving Toronto and the GTA.",
    """    <h2>Professional Canopy Installation in Toronto</h2>
    <p>aMaximum Construction designs and installs custom canopies, pergolas, and shade structures for residential and commercial properties throughout Toronto and the GTA. Extend your outdoor season and add value to your home with a professionally built shade solution.</p>
    <h2>Canopy &amp; Shade Structures We Install</h2>
    <ul>
      <li><strong>Wood Pergolas</strong> — Cedar and pressure-treated timber, custom designs</li>
      <li><strong>Aluminum Pergolas</strong> — Low-maintenance, powder-coated, louvred options</li>
      <li><strong>Retractable Awnings</strong> — Manual and motorized patio awnings</li>
      <li><strong>Shade Sails</strong> — Architectural fabric shade solutions</li>
      <li><strong>Commercial Canopies</strong> — Storefront and entrance canopies</li>
    </ul>
    <p>All structures are engineered for Ontario weather conditions including snow load and wind. aMaximum Construction manages permits and inspections as required.</p>"""
)))

# ── COMPANY / INFO PAGES ──────────────────────────────────────────────────────
pages.append(("our-work-process", gen_simple_page(
    "our-work-process",
    "Our Work Process | aMaximum Construction",
    "Learn how aMaximum Construction manages your project from first call to final walkthrough. Transparent process, clear communication.",
    "Our Work Process",
    "How aMaximum Construction manages your renovation or construction project.",
    """    <h2>How We Work</h2>
    <p>aMaximum Construction follows a proven, client-focused process that ensures every project is completed to the highest standard — on time, on budget, and with clear communication throughout.</p>
    <h2>Step 1: Free Consultation</h2>
    <p>We visit your home or property to discuss your project goals, timeline, and budget. No pressure, no sales tactics — just an honest conversation about what you want to achieve.</p>
    <h2>Step 2: Detailed Written Quote</h2>
    <p>Within 48 hours, we provide a detailed, itemized written quote with no hidden costs. You'll know exactly what's included before signing anything.</p>
    <h2>Step 3: Permit Management</h2>
    <p>For projects requiring building permits, we manage the entire application and inspection process. You don't need to deal with the city — we handle it.</p>
    <h2>Step 4: Construction</h2>
    <p>Our licensed and insured crew completes the work using quality materials and proven techniques. We maintain a clean job site and provide regular progress updates.</p>
    <h2>Step 5: Final Walkthrough &amp; Warranty</h2>
    <p>We conduct a detailed final inspection with you. We don't consider the job done until you're completely satisfied. All work is backed by our workmanship warranty.</p>"""
)))

pages.append(("why-choose-us", gen_simple_page(
    "why-choose-us",
    "Why Choose aMaximum Construction | Toronto GTA Contractor",
    "Why Toronto homeowners choose aMaximum Construction for renovations, deck building, and general contracting. Licensed, insured, and committed to quality.",
    "Why Choose aMaximum Construction",
    "The reasons Toronto homeowners trust aMaximum Construction for their biggest projects.",
    """    <h2>Licensed &amp; Insured</h2>
    <p>aMaximum Construction is fully licensed and carries comprehensive liability insurance and WSIB coverage. You're protected on every project, no exceptions.</p>
    <h2>Transparent Pricing</h2>
    <p>We provide detailed, written quotes with no hidden costs. The price we quote is the price you pay — unless you request changes to the scope of work.</p>
    <h2>Permit Management Included</h2>
    <p>We handle all building permit applications and inspections on your behalf. No chasing city inspectors or navigating confusing application processes.</p>
    <h2>Quality Materials</h2>
    <p>We source materials from reputable suppliers and stand behind every product we install. No substitutions without client approval.</p>
    <h2>Clean Job Sites</h2>
    <p>We maintain a clean, organized job site throughout your project. At the end of each day, materials are secured and debris is managed.</p>
    <h2>Real Workmanship Warranty</h2>
    <p>Our work is backed by a written workmanship warranty. If something isn't right, we fix it — no arguments, no excuses.</p>
    <h2>Strong Client Reviews</h2>
    <p>Our reputation is built on satisfied clients across Toronto and the GTA. We are happy to provide references for projects similar to yours.</p>"""
)))

pages.append(("what-we-do", gen_simple_page(
    "what-we-do",
    "What We Do | aMaximum Construction Services",
    "aMaximum Construction provides deck building, basement renovation, bathroom renovation, general contracting, handyman services, and more across Toronto & GTA.",
    "What We Do",
    "aMaximum Construction — full-service construction and renovation contractor in Toronto & GTA.",
    """    <h2>Construction &amp; Renovation Services</h2>
    <p>aMaximum Construction is a licensed general contractor serving Toronto and the Greater Toronto Area. We provide a comprehensive range of residential construction and renovation services under one roof.</p>
    <h2>Our Services</h2>
    <ul>
      <li><a href="/general-contractor-in-toronto/"><strong>General Contracting</strong></a> — Full project management for any scope</li>
      <li><a href="/deck-builder/"><strong>Deck Building</strong></a> — Custom decks in wood, composite, and cedar</li>
      <li><a href="/basement-renovation-service-in-toronto/"><strong>Basement Renovation</strong></a> — Full finishing, in-law suites, waterproofing</li>
      <li><a href="/interior-bathroom-renovation-toronto/"><strong>Bathroom Renovation</strong></a> — Complete bathroom remodels and updates</li>
      <li><a href="/fence-contractor-in-toronto/"><strong>Fence Installation</strong></a> — Wood, vinyl, aluminum, and chain-link</li>
      <li><a href="/carpenter-services-toronto/"><strong>Carpentry</strong></a> — Custom cabinetry, trim, built-ins</li>
      <li><a href="/handyman-service-in-toronto/"><strong>Handyman Services</strong></a> — Repairs, installations, and maintenance</li>
      <li><a href="/demolition-services/"><strong>Demolition</strong></a> — Interior, exterior, and full structure removal</li>
      <li><a href="/interlocking-paver-services/"><strong>Interlocking &amp; Paving</strong></a> — Driveways, patios, walkways</li>
      <li><a href="/excavation-services/"><strong>Excavation</strong></a> — Foundation, grading, and site preparation</li>
    </ul>"""
)))

pages.append(("client-testimonials", gen_simple_page(
    "client-testimonials",
    "Client Testimonials | aMaximum Construction Reviews",
    "Read what Toronto and GTA homeowners say about aMaximum Construction. Real reviews from real clients on decks, basement renovations, and more.",
    "Client Testimonials",
    "What Toronto & GTA homeowners say about working with aMaximum Construction.",
    """    <h2>What Our Clients Say</h2>
    <p>aMaximum Construction has completed hundreds of projects across Toronto and the GTA. Here's what some of our clients have shared about their experience.</p>
    <div style="margin:24px 0;padding:20px;background:#f8f9fa;border-left:4px solid #ff6b35;border-radius:4px">
      <p><em>"aMaximum built our new deck in Markham last summer. The team was professional, the timeline was exactly as promised, and the result is beautiful. We've already recommended them to our neighbours."</em></p>
      <p><strong>— Markham homeowner, Deck Build Project</strong></p>
    </div>
    <div style="margin:24px 0;padding:20px;background:#f8f9fa;border-left:4px solid #ff6b35;border-radius:4px">
      <p><em>"We hired aMaximum for our basement renovation in North York. They managed all the permits, kept us updated throughout, and delivered a beautiful family room and bathroom. Great experience."</em></p>
      <p><strong>— North York homeowner, Basement Renovation</strong></p>
    </div>
    <div style="margin:24px 0;padding:20px;background:#f8f9fa;border-left:4px solid #ff6b35;border-radius:4px">
      <p><em>"Quick, clean, and professional. They installed a new fence and privacy screen for our backyard in Richmond Hill. Exactly what we wanted."</em></p>
      <p><strong>— Richmond Hill homeowner, Fence &amp; Privacy Screen</strong></p>
    </div>
    <p>To read more reviews, visit our Google Business profile or contact us for client references for projects similar to yours.</p>"""
)))

pages.append(("company-policy-of-amaximum-construction", gen_simple_page(
    "company-policy-of-amaximum-construction",
    "Company Policy | aMaximum Construction",
    "aMaximum Construction company policies — licensing, insurance, payment terms, warranty, and dispute resolution.",
    "Company Policy",
    "aMaximum Construction policies on licensing, insurance, warranty, and client relations.",
    """    <h2>Licensing &amp; Insurance</h2>
    <p>aMaximum Construction is a licensed general contractor operating in Ontario. We carry comprehensive general liability insurance and WSIB coverage on all projects. Certificate of insurance available upon request.</p>
    <h2>Quotes &amp; Contracts</h2>
    <p>All projects begin with a detailed written quote. Work commences only after a signed contract is in place. Change orders require written authorization before work proceeds.</p>
    <h2>Payment Terms</h2>
    <p>Payment schedules are outlined in the project contract. We accept cash, credit card, and e-Transfer. A deposit is required before work begins; balance due upon project completion and client sign-off.</p>
    <h2>Permits &amp; Inspections</h2>
    <p>aMaximum Construction manages permit applications for all projects requiring building permits. Permit costs are passed through at cost — no markup. Inspections are scheduled and managed by our team.</p>
    <h2>Workmanship Warranty</h2>
    <p>All labour performed by aMaximum Construction is warranted against defects for a period of one year from project completion. Material warranties are passed through from manufacturers.</p>
    <h2>Dispute Resolution</h2>
    <p>We are committed to client satisfaction. Any concerns are addressed promptly and professionally. In the unlikely event of a dispute, we seek resolution through direct communication before any formal process.</p>"""
)))

pages.append(("amaximum-deck-builder-blog", gen_simple_page(
    "amaximum-deck-builder-blog",
    "aMaximum Deck Builder Blog | Construction Tips & Guides",
    "Expert articles on deck building, renovation, carpentry, and home improvement from the aMaximum Construction team in Toronto & GTA.",
    "aMaximum Construction Blog",
    "Expert tips, guides, and insights from Toronto's trusted construction contractors.",
    """    <h2>Expert Construction &amp; Renovation Articles</h2>
    <p>The aMaximum Construction blog covers everything from deck building and basement renovation to handyman tips and contractor advice. Our team shares practical, expert knowledge to help Toronto homeowners make informed decisions.</p>
    <h2>Popular Articles</h2>
    <ul>
      <li><a href="/find-perfect-deck-contractor/">How to Find the Perfect Deck Contractor</a></li>
      <li><a href="/choosing-right-decking-material-landscape/">Choosing the Right Decking Material</a></li>
      <li><a href="/deck-maintenance-in-markhams-variable-climate/">Deck Maintenance in Markham's Variable Climate</a></li>
      <li><a href="/how-to-repair-wood-decks/">How to Repair Wood Decks</a></li>
      <li><a href="/reasons-to-hire-professional-deck-contractors/">Reasons to Hire Professional Deck Contractors</a></li>
      <li><a href="/is-it-cheaper-to-build-your-own-deck-aurora/">Is It Cheaper to Build Your Own Deck?</a></li>
    </ul>
    <p><a href="/blog/" class="btn">View All Blog Posts</a></p>"""
)))

# ─────────────────────────────────────────────────────────────────────────────
#  WRITE ALL PAGES
# ─────────────────────────────────────────────────────────────────────────────

print(f"Generating {len(pages)} missing pages...")
for slug, html in pages:
    write_page(slug, html)

print(f"\nDone. {len(pages)} pages created.")
