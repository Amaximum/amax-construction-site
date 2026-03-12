#!/usr/bin/env python3
"""
generate_service_pages.py
Generates SEO-optimized service+location pages for aMaximum Construction.
SEO 2026: E-E-A-T, AI-overview friendly, schema.org (LocalBusiness + Service + FAQPage + BreadcrumbList),
          proper H1/H2/H3 hierarchy, canonical, OG tags, Core Web Vitals (lightweight HTML).
Run: python generate_service_pages.py
"""

import os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL  = "https://amaximumconstruction.com"
EMAIL     = "amaximumconstructioncorp@gmail.com"
PHONE     = "+1-647-XXX-XXXX"

LOCATIONS = [
    {"name": "Toronto",       "slug": "toronto",       "nearby": "North York, Etobicoke, Scarborough, East York"},
    {"name": "North York",    "slug": "north-york",    "nearby": "Toronto, Willowdale, Newtonbrook, Don Mills"},
    {"name": "East York",     "slug": "east-york",     "nearby": "Toronto, Scarborough, Leaside, Danforth"},
    {"name": "Scarborough",   "slug": "scarborough",   "nearby": "Toronto, Markham, Pickering, East York"},
    {"name": "Etobicoke",     "slug": "etobicoke",     "nearby": "Toronto, Mississauga, Woodbridge, Rexdale"},
    {"name": "Markham",       "slug": "markham",       "nearby": "Richmond Hill, Scarborough, Unionville, Stouffville"},
    {"name": "Richmond Hill", "slug": "richmond-hill", "nearby": "Markham, Vaughan, Aurora, North York"},
    {"name": "Vaughan",       "slug": "vaughan",       "nearby": "Woodbridge, Richmond Hill, Maple, Kleinburg"},
    {"name": "Woodbridge",    "slug": "woodbridge",    "nearby": "Vaughan, Etobicoke, Maple, Kleinburg"},
    {"name": "Aurora",        "slug": "aurora",        "nearby": "Newmarket, Richmond Hill, King City, Oak Ridges"},
    {"name": "Newmarket",     "slug": "newmarket",     "nearby": "Aurora, Bradford, Sharon, East Gwillimbury"},
]

# ── Nav ──────────────────────────────────────────────────────────────────────
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

# ── Footer ───────────────────────────────────────────────────────────────────
FOOTER = """\
<footer class="site-footer">
  <div class="shell">
    <div class="footer-cols">
      <div class="footer-col footer-brand">
        <a href="/" class="footer-logo-link">
          <img src="/img/logo.png" alt="aMaximum Construction" class="footer-logo">
        </a>
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
          <li><a href="/demolition-services/">Demolition</a></li>
          <li><a href="/handyman-service-in-toronto/">Handyman</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Service Areas</h4>
        <ul>
          <li><a href="/general-contractor-in-toronto/">Toronto</a></li>
          <li><a href="/general-contractor-in-markham/">Markham</a></li>
          <li><a href="/general-contractor-in-richmond-hill/">Richmond Hill</a></li>
          <li><a href="/general-contractor-in-vaughan/">Vaughan</a></li>
          <li><a href="/general-contractor-in-newmarket/">Newmarket</a></li>
          <li><a href="/locations/">All Locations &rarr;</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/portfolio/">Portfolio</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/#faq">FAQ</a></li>
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

SCRIPTS = """\
<script>
const menuBtn = document.getElementById('menuBtn');
const siteNav = document.getElementById('siteNav');
if (menuBtn && siteNav) {
  menuBtn.addEventListener('click', () => {
    const exp = menuBtn.getAttribute('aria-expanded') === 'true';
    menuBtn.setAttribute('aria-expanded', !exp);
    siteNav.classList.toggle('open');
  });
}
const m  = document.getElementById('bookingModal');
const b  = document.getElementById('bookingBtn');
const x  = document.getElementById('modalClose');
const ov = document.getElementById('modalOverlay');
const cc = document.getElementById('cancelBtn');
const f  = document.getElementById('bookingForm');
const bd = document.getElementById('bookDate');
if (bd) bd.min = new Date().toISOString().split('T')[0];
const openModal  = () => { m.classList.add('active');    document.body.style.overflow = 'hidden'; };
const closeModal = () => { m.classList.remove('active'); document.body.style.overflow = '';       };
if (b)  b.addEventListener('click', openModal);
if (x)  x.addEventListener('click', closeModal);
if (ov) ov.addEventListener('click', closeModal);
if (cc) cc.addEventListener('click', closeModal);
if (f) f.addEventListener('submit', e => {
  e.preventDefault();
  const d = Object.fromEntries(new FormData(f));
  const subj = encodeURIComponent(d.service || document.title);
  const body = encodeURIComponent(
    `Name: ${d.name}\\nPhone: ${d.phone}\\nEmail: ${d.email}\\nAddress: ${d.address}\\nDate: ${d.date}\\nTime: ${d.time}\\n\\n${d.details || 'N/A'}`
  );
  window.location.href = `mailto:${EMAIL_JS}?subject=${subj}&body=${body}`;
  f.reset();
  setTimeout(closeModal, 500);
});
</script>""".replace("${EMAIL_JS}", EMAIL)


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
                {"@type": "ListItem", "position": 1, "name": "Home",         "item": BASE_URL + "/"},
                {"@type": "ListItem", "position": 2, "name": location_name,  "item": canonical},
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
    schema    = build_schema(slug, service_type, location_name, faqs)
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
#  SERVICE GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def gen_general_contractor(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"general-contractor-in-{s}"
    faqs = [
        (f"What does a general contractor in {n} do?",
         f"A general contractor in {n} manages every aspect of your construction or renovation project — hiring subcontractors, sourcing materials, pulling permits, and ensuring the work meets Ontario Building Code. aMaximum Construction handles residential and commercial projects of all sizes across {n}."),
        (f"How much does a general contractor cost in {n}?",
         f"General contractor fees in {n} typically range from 10–20% of total project cost for full management, or a flat hourly/project rate for smaller jobs. aMaximum Construction offers transparent quotes with no hidden fees — contact us for a free estimate."),
        (f"Do I need a permit for my renovation in {n}?",
         f"Most structural, electrical, plumbing, and HVAC work in {n} requires a building permit from the City of Toronto or York Region. aMaximum Construction manages the permit process on your behalf, ensuring full compliance with Ontario Building Code."),
        (f"How long does a typical renovation take in {n}?",
         f"Project timelines in {n} vary by scope: a bathroom renovation may take 2–4 weeks, a basement finish 6–10 weeks, and a full home renovation 3–6 months. We provide a detailed schedule before work begins."),
    ]
    content = f"""\
    <h2>Trusted General Contractor in {n}</h2>
    <p>aMaximum Construction is a licensed and insured general contractor serving {n} and the Greater Toronto Area. We manage residential renovations, commercial build-outs, and custom construction projects from start to finish — on time and on budget.</p>
    <p>With over a decade of experience in {n}, our team coordinates every trade, handles building permits, and delivers results that meet Ontario Building Code standards and exceed client expectations.</p>

    <h2>General Contracting Services in {n}</h2>
    <ul>
      <li><strong>Full Project Management</strong> — Single point of contact from planning to final walkthrough</li>
      <li><strong>Residential Renovations</strong> — Kitchens, bathrooms, basements, additions, and whole-home remodels</li>
      <li><strong>Commercial Construction</strong> — Office fit-outs, retail renovations, and light industrial builds</li>
      <li><strong>Permits &amp; Inspections</strong> — We handle all permit applications and city inspections in {n}</li>
      <li><strong>Subcontractor Coordination</strong> — Vetted electricians, plumbers, HVAC, and drywall crews</li>
      <li><strong>Custom Builds &amp; Additions</strong> — Home additions, sunrooms, garages, and new construction</li>
    </ul>

    <h2>Why {n} Homeowners Choose aMaximum Construction</h2>
    <ul>
      <li>&#10003; Licensed contractor — Ontario contractor registration in good standing</li>
      <li>&#10003; Fully insured — $2M liability coverage for every project</li>
      <li>&#10003; Free detailed quotes — transparent pricing, no surprises</li>
      <li>&#10003; Permit-ready — we file and manage all {n} building permits</li>
      <li>&#10003; Warranty on workmanship — we stand behind every job</li>
      <li>&#10003; Local expertise — knowledge of {n} bylaws, HOA rules, and inspectors</li>
    </ul>

    <h2>Our Construction Process in {n}</h2>
    <p>Every project follows our proven 5-step process: <strong>1) Free Consultation</strong> → <strong>2) Detailed Quote</strong> → <strong>3) Permit Filing</strong> → <strong>4) Construction</strong> → <strong>5) Final Inspection &amp; Warranty</strong>. We keep you informed at every stage.</p>

    <h2>Areas We Serve Near {n}</h2>
    <p>In addition to {n}, aMaximum Construction serves {nb} and all surrounding GTA communities. Contact us for service availability in your area.</p>

    <h2>Frequently Asked Questions — General Contractor {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"General Contractor in {n} | aMaximum Construction",
        meta_desc   = f"Looking for a trusted general contractor in {n}? aMaximum Construction delivers expert residential and commercial construction services. Licensed, insured, free quotes.",
        h1          = f"General Contractor in {n}",
        hero_sub    = f"Licensed, insured general contracting for residential &amp; commercial projects in {n}",
        content_html= content,
        cta_h2      = f"Get a Free Quote — General Contractor {n}",
        cta_p       = f"Contact aMaximum Construction for a no-obligation estimate on your {n} project.",
        location_name = n,
        service_type  = "General Contracting",
        service_label = "General Contractor",
        faqs          = faqs,
    )


def gen_carpenter(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"carpenter-services-{s}"
    faqs = [
        (f"What carpenter services do you offer in {n}?",
         f"aMaximum Construction provides a full range of carpentry services in {n}: custom cabinetry, trim and moulding installation, stair construction, built-in shelving, deck framing, fence framing, door and window installation, and interior finishing work."),
        (f"How much do carpenter services cost in {n}?",
         f"Carpentry rates in {n} vary by project complexity. Simple trim and moulding work starts around $50–$80/hr, while custom cabinetry or built-ins are typically quoted as a fixed project price. Contact us for a free, itemized estimate."),
        (f"Do you build custom cabinets in {n}?",
         f"Yes — aMaximum Construction builds custom kitchen and bathroom cabinets in {n} to exact specifications. We use premium materials including solid wood, plywood carcasses, and quality hardware for long-lasting results."),
    ]
    content = f"""\
    <h2>Expert Carpenter Services in {n}</h2>
    <p>aMaximum Construction offers professional carpenter services throughout {n}. From custom cabinetry and built-ins to structural framing and finish carpentry, our skilled craftsmen deliver precise, durable results that enhance both the function and value of your property.</p>

    <h2>Carpentry Services We Offer in {n}</h2>
    <ul>
      <li><strong>Custom Cabinetry</strong> — Kitchen, bathroom, laundry, and garage cabinets built to specification</li>
      <li><strong>Trim &amp; Moulding</strong> — Baseboards, crown moulding, window casing, door casing, and wainscoting</li>
      <li><strong>Built-in Shelving &amp; Storage</strong> — Custom closets, home office built-ins, entertainment units</li>
      <li><strong>Stair Construction &amp; Repair</strong> — New staircases, treads, risers, stringers, and railings</li>
      <li><strong>Deck &amp; Fence Framing</strong> — Structural framing for decks, fences, pergolas, and gazebos</li>
      <li><strong>Door &amp; Window Installation</strong> — Interior and exterior door hanging, window trim, and sill replacement</li>
    </ul>

    <h2>Why Choose Our Carpenters in {n}</h2>
    <ul>
      <li>&#10003; Red Seal and apprentice-certified carpenters</li>
      <li>&#10003; Premium materials — solid wood, plywood, and quality composites</li>
      <li>&#10003; Precise measurements and tight tolerances</li>
      <li>&#10003; Clean jobsites — we protect your flooring and surfaces</li>
      <li>&#10003; Fixed-price quotes — no hourly surprises on defined projects</li>
      <li>&#10003; Serving {n} and {nb}</li>
    </ul>

    <h2>Finish Carpentry vs. Rough Carpentry in {n}</h2>
    <p><strong>Rough carpentry</strong> includes structural framing — walls, floors, roof structure, deck framing. <strong>Finish carpentry</strong> covers trim, cabinets, stairs, and anything visible in the final result. aMaximum Construction handles both, making us a one-stop shop for {n} homeowners and contractors.</p>

    <h2>Frequently Asked Questions — Carpenter Services {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"Carpenter Services in {n} | Custom Carpentry | aMaximum Construction",
        meta_desc   = f"Expert carpenter services in {n} — custom cabinetry, trim, built-ins, stairs, and framing. Licensed carpenters, free quotes. aMaximum Construction.",
        h1          = f"Carpenter Services in {n}",
        hero_sub    = f"Custom cabinetry, trim, built-ins, and finish carpentry in {n}",
        content_html= content,
        cta_h2      = f"Book a Carpenter in {n} Today",
        cta_p       = f"Get a free, itemized quote for your {n} carpentry project.",
        location_name = n,
        service_type  = "Carpentry Services",
        service_label = "Carpenter Services",
        faqs          = faqs,
    )


def gen_demolition(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"demolition-service-in-{s}"
    faqs = [
        (f"Do I need a permit for demolition work in {n}?",
         f"In most cases, yes. Structural demolition and full building removals require a demolition permit from the city. Interior selective demolition for renovation purposes may not require a separate permit. aMaximum Construction assesses your project and handles all permit requirements in {n}."),
        (f"How long does demolition take in {n}?",
         f"Interior demolition for a single room typically takes 1–2 days. Full structure demolition in {n} can take 1–5 days depending on size. We provide a detailed timeline in your quote."),
        (f"Do you handle debris removal after demolition in {n}?",
         f"Yes — all our demolition services in {n} include full debris removal and site cleanup. We haul away all materials and leave a clean, broom-swept site ready for the next phase of work."),
    ]
    content = f"""\
    <h2>Professional Demolition Services in {n}</h2>
    <p>aMaximum Construction provides safe, efficient demolition services for residential and commercial properties in {n}. Whether you need interior selective demolition for a renovation or complete structure removal, our team handles the job with full compliance to Ontario safety regulations and city permits.</p>

    <h2>Demolition Services Available in {n}</h2>
    <ul>
      <li><strong>Interior Demolition</strong> — Kitchen, bathroom, basement gut-outs; wall, ceiling, and floor removal</li>
      <li><strong>Selective Demolition</strong> — Precise removal of specific elements while protecting surrounding structures</li>
      <li><strong>Exterior &amp; Structure Demolition</strong> — Garages, sheds, decks, fences, and outbuildings</li>
      <li><strong>Full Building Demolition</strong> — Complete residential and light commercial structure removal</li>
      <li><strong>Debris Removal &amp; Haul-Away</strong> — Full cleanup and responsible disposal of all demolition waste</li>
      <li><strong>Asbestos &amp; Hazmat Protocol</strong> — Safe procedures for pre-1990 buildings; referral to certified abatement when required</li>
    </ul>

    <h2>Why Hire aMaximum Construction for Demolition in {n}</h2>
    <ul>
      <li>&#10003; Permit management — we file all required {n} demolition permits</li>
      <li>&#10003; Full $2M liability insurance coverage</li>
      <li>&#10003; Utility disconnection coordination (gas, hydro, water)</li>
      <li>&#10003; Dust and debris containment — protecting adjacent areas</li>
      <li>&#10003; Same-day and next-day availability for urgent projects</li>
      <li>&#10003; Serving {n}, {nb}, and surrounding GTA communities</li>
    </ul>

    <h2>Demolition Safety Standards in {n}</h2>
    <p>All demolition work in {n} is performed in compliance with the <strong>Ontario Occupational Health and Safety Act</strong>, Ontario Building Code, and City of Toronto / York Region demolition permit requirements. We conduct pre-demolition surveys to identify hazardous materials, locate utilities, and plan safe work procedures before a single wall comes down.</p>

    <h2>Frequently Asked Questions — Demolition in {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"Demolition Service in {n} | Licensed Demo Contractors | aMaximum Construction",
        meta_desc   = f"Professional demolition services in {n} — interior demo, structure removal, debris haul-away. Licensed, insured, permit-managed. Free quotes from aMaximum Construction.",
        h1          = f"Demolition Service in {n}",
        hero_sub    = f"Safe, permitted demolition for residential and commercial properties in {n}",
        content_html= content,
        cta_h2      = f"Request a Demolition Quote in {n}",
        cta_p       = f"Contact us for a fast, free estimate on your {n} demolition project.",
        location_name = n,
        service_type  = "Demolition Services",
        service_label = "Demolition Service",
        faqs          = faqs,
    )


def gen_handyman(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"handyman-service-in-{s}"
    faqs = [
        (f"What handyman services do you offer in {n}?",
         f"Our handyman team in {n} handles drywall repair, door and window installation, minor plumbing (fixture replacement, shut-off valves), tile repair, painting, caulking, fixture mounting, shelving installation, weatherstripping, and general home repairs."),
        (f"How do you charge for handyman work in {n}?",
         f"aMaximum Construction offers both hourly handyman rates and fixed-price project quotes in {n}. Hourly rates apply to small varied tasks; for defined projects we provide a flat price. Minimum 2-hour booking. Contact us for current rates."),
        (f"Are your handymen licensed and insured in {n}?",
         f"Yes — all our handyman technicians in {n} are covered under aMaximum Construction's $2M liability insurance policy. For trades-specific work (electrical, plumbing rough-in) we bring in licensed subcontractors."),
    ]
    content = f"""\
    <h2>Reliable Handyman Services in {n}</h2>
    <p>Need something fixed, installed, or repaired around your {n} home or business? aMaximum Construction's handyman team tackles a wide range of maintenance and repair tasks quickly and professionally. No job is too small — we show up on time and get it done right.</p>

    <h2>Handyman Services We Provide in {n}</h2>
    <ul>
      <li><strong>Drywall Repair &amp; Patching</strong> — Holes, cracks, water damage, and full panel replacement</li>
      <li><strong>Door &amp; Window Installation</strong> — Interior doors, exterior doors, storm doors, window repairs</li>
      <li><strong>Plumbing Fixtures</strong> — Faucet replacement, toilet installation, shut-off valves, minor leak repairs</li>
      <li><strong>Painting &amp; Caulking</strong> — Touch-ups, accent walls, bathroom and kitchen re-caulking</li>
      <li><strong>Fixture &amp; TV Mounting</strong> — Light fixtures, ceiling fans, TV wall mounts, shelving</li>
      <li><strong>General Repairs</strong> — Weatherstripping, tile replacement, cabinet hardware, deck board replacement</li>
    </ul>

    <h2>Why {n} Residents Trust Our Handyman Team</h2>
    <ul>
      <li>&#10003; Background-checked, uniformed technicians</li>
      <li>&#10003; Fully insured — $2M liability coverage</li>
      <li>&#10003; Prompt arrival — we respect your schedule</li>
      <li>&#10003; Transparent pricing — no surprise charges</li>
      <li>&#10003; Clean work — all debris removed when we leave</li>
      <li>&#10003; Serving {n} and nearby {nb}</li>
    </ul>

    <h2>Home Maintenance vs. Renovation in {n}</h2>
    <p>Our handyman service covers maintenance and repair tasks. For larger renovation projects (full kitchen, bathroom, or basement renovation) in {n}, our <a href="/general-contractor-in-{s}/">general contracting team</a> takes over. One call covers everything.</p>

    <h2>Frequently Asked Questions — Handyman {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"Handyman Service in {n} | Repairs & Installations | aMaximum Construction",
        meta_desc   = f"Trusted handyman services in {n} — drywall, doors, plumbing fixtures, painting, mounting, and more. Licensed, insured. Free quotes from aMaximum Construction.",
        h1          = f"Handyman Service in {n}",
        hero_sub    = f"Fast, reliable repairs and installations for homes and businesses in {n}",
        content_html= content,
        cta_h2      = f"Book a Handyman in {n} Today",
        cta_p       = f"Schedule your {n} handyman appointment — same-week availability.",
        location_name = n,
        service_type  = "Handyman Services",
        service_label = "Handyman Service",
        faqs          = faqs,
    )


def gen_deck_contractor(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"deck-contractor-{s}"
    faqs = [
        (f"How much does a deck cost in {n}?",
         f"Deck costs in {n} range from $8,000–$15,000 for a basic pressure-treated deck to $25,000–$50,000+ for large composite or hardwood multi-level decks. Exact pricing depends on size, materials, and complexity. We offer free, itemized quotes."),
        (f"What deck materials do you use in {n}?",
         f"aMaximum Construction builds decks in {n} using pressure-treated lumber, cedar, tropical hardwood (Ipe, Cumaru), Trex composite, TimberTech, and Fiberon. We help you choose the best material for your budget, aesthetic, and {n}'s climate."),
        (f"Do I need a permit for a deck in {n}?",
         f"In Ontario, decks over 24\" above grade or attached to the house typically require a building permit. aMaximum Construction handles all permit applications for {n} deck projects as part of our service."),
    ]
    content = f"""\
    <h2>Expert Deck Contractor in {n}</h2>
    <p>aMaximum Construction is a trusted deck contractor serving {n} and the surrounding GTA. We design and build custom decks — from simple ground-level platforms to multi-level entertainment spaces — using premium materials built to withstand Ontario's climate and meet all local building codes.</p>

    <h2>Deck Services in {n}</h2>
    <ul>
      <li><strong>Custom Deck Design &amp; Build</strong> — Ground-level, elevated, and multi-level decks</li>
      <li><strong>Deck Renovation &amp; Rebuild</strong> — Updating old decks with new materials and designs</li>
      <li><strong>Composite Decking</strong> — Trex, TimberTech, Fiberon — low maintenance, 25-year warranty</li>
      <li><strong>Wood Decking</strong> — Pressure-treated, cedar, redwood, and tropical hardwoods</li>
      <li><strong>Deck Railings &amp; Stairs</strong> — Cable, glass, aluminum, and wood railing systems</li>
      <li><strong>Pergolas &amp; Shade Structures</strong> — Attached and freestanding pergolas for {n} backyards</li>
    </ul>

    <h2>Why {n} Homeowners Choose aMaximum Construction</h2>
    <ul>
      <li>&#10003; Licensed and insured deck contractor — Ontario registered</li>
      <li>&#10003; Building permit management for {n} and York Region</li>
      <li>&#10003; Premium materials from trusted Canadian suppliers</li>
      <li>&#10003; Structural warranty on all framing and connections</li>
      <li>&#10003; Free 3D design consultation</li>
      <li>&#10003; Serving {n}, {nb}, and surrounding areas</li>
    </ul>

    <h2>Best Decking Materials for {n}'s Climate</h2>
    <p><strong>Composite decking</strong> is the most popular choice in {n} — it resists freeze-thaw cycles, requires no staining, and lasts 25+ years. <strong>Pressure-treated lumber</strong> remains the budget-friendly option with regular sealing. <strong>Cedar</strong> offers natural beauty with good rot resistance. We guide every {n} homeowner through the selection process.</p>

    <h2>Frequently Asked Questions — Deck Contractor {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"Deck Contractor {n} | Custom Deck Builder | aMaximum Construction",
        meta_desc   = f"Expert deck contractor in {n}. Custom deck design and build, composite and wood decking, railings, and pergolas. Licensed, insured. Free quotes.",
        h1          = f"Deck Contractor in {n}",
        hero_sub    = f"Custom deck design, build, and renovation services in {n}",
        content_html= content,
        cta_h2      = f"Start Your {n} Deck Project",
        cta_p       = f"Get a free consultation and 3D design quote for your {n} deck.",
        location_name = n,
        service_type  = "Deck Construction",
        service_label = "Deck Contractor",
        faqs          = faqs,
    )


def gen_deck_railing(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"deck-railing-installer-in-{s}"
    faqs = [
        (f"What deck railing styles are available in {n}?",
         f"aMaximum Construction installs cable railings, tempered glass railings, aluminum railings, wood railings, and composite railings in {n}. We help you choose the style that complements your deck and meets Ontario building code requirements."),
        (f"What are the building code requirements for deck railings in {n}?",
         f"Ontario Building Code requires guards (railings) on decks 600mm (24\") or more above grade. Guards must be at least 900mm high for decks up to 1.8m above grade, and 1070mm for decks higher than 1.8m. Openings must not allow a 100mm sphere to pass through. aMaximum Construction ensures all {n} installations are fully code-compliant."),
        (f"How long does railing installation take in {n}?",
         f"A typical deck railing installation in {n} takes 1–2 days depending on linear footage and material type. Glass railing systems may take an additional day for templating and custom panel fabrication."),
    ]
    content = f"""\
    <h2>Professional Deck Railing Installer in {n}</h2>
    <p>aMaximum Construction installs deck railings and guards throughout {n} that combine safety, style, and full Ontario Building Code compliance. Whether you're upgrading existing railings or adding them to a new deck, we offer a full range of materials and styles to match your home's aesthetic.</p>

    <h2>Deck Railing Systems We Install in {n}</h2>
    <ul>
      <li><strong>Cable Railings</strong> — Sleek, modern stainless steel cable systems with unobstructed views</li>
      <li><strong>Tempered Glass Railings</strong> — Frameless and semi-frameless glass panels for maximum sight lines</li>
      <li><strong>Aluminum Railings</strong> — Low-maintenance, powder-coated, available in multiple colours</li>
      <li><strong>Wood Railings</strong> — Classic cedar or pressure-treated posts, rails, and balusters</li>
      <li><strong>Composite Railings</strong> — Weather-resistant composite in a variety of finishes</li>
      <li><strong>Post &amp; Baluster Systems</strong> — Traditional and contemporary baluster designs</li>
    </ul>

    <h2>Ontario Building Code — Railing Requirements in {n}</h2>
    <p>All railings installed by aMaximum Construction in {n} meet or exceed Ontario Building Code Section 9.8.8 (Guards): minimum 900mm height for decks up to 1.8m above grade; 1070mm for higher decks; no openings larger than 100mm. We handle the permit process and inspections.</p>

    <h2>Why Choose aMaximum for Railing Installation in {n}</h2>
    <ul>
      <li>&#10003; Code-compliant installations — permit filing included</li>
      <li>&#10003; Wide material selection — cable, glass, aluminum, wood, composite</li>
      <li>&#10003; Experienced installers with precision post-setting</li>
      <li>&#10003; Competitive pricing with written quotes</li>
      <li>&#10003; Also serving {nb}</li>
    </ul>

    <h2>Frequently Asked Questions — Deck Railings {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"Deck Railing Installer in {n} | Cable, Glass & Aluminum | aMaximum Construction",
        meta_desc   = f"Professional deck railing installation in {n} — cable, glass, aluminum, and wood railings. Code-compliant, licensed, free quotes. aMaximum Construction.",
        h1          = f"Deck Railing Installer in {n}",
        hero_sub    = f"Cable, glass, aluminum, and wood railing systems for {n} decks",
        content_html= content,
        cta_h2      = f"Get a Railing Quote for Your {n} Deck",
        cta_p       = f"Free measurement and quote — we come to your {n} property.",
        location_name = n,
        service_type  = "Deck Railing Installation",
        service_label = "Deck Railing Installer",
        faqs          = faqs,
    )


def gen_basement_renovation(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"basement-renovation-service-in-{s}"
    faqs = [
        (f"How much does a basement renovation cost in {n}?",
         f"Basement renovation costs in {n} typically range from $30,000–$60,000 for a full finish with standard materials, and $60,000–$120,000+ for premium finishes or an in-law suite with a second kitchen and bathroom. Contact us for a free, itemized quote specific to your {n} basement."),
        (f"How long does a basement renovation take in {n}?",
         f"A typical basement renovation in {n} takes 8–14 weeks from permit approval to final inspection. Projects involving waterproofing, underpinning, or complex plumbing may take longer. We provide a detailed timeline before work begins."),
        (f"Do I need a permit to finish my basement in {n}?",
         f"Yes — finishing an unfinished basement in {n} requires a building permit covering framing, electrical, plumbing (if adding a bathroom), and HVAC. aMaximum Construction files all permits and manages city inspections on your behalf."),
        (f"Can you add a second unit or in-law suite to my {n} basement?",
         f"Yes — aMaximum Construction designs and builds legal secondary suites and in-law apartments in {n} basements, including egress windows, separate entrance, kitchen, bathroom, and all required permits for an Additional Dwelling Unit (ADU)."),
    ]
    content = f"""\
    <h2>Professional Basement Renovation in {n}</h2>
    <p>aMaximum Construction transforms unfinished and outdated basements into beautiful, functional living spaces across {n}. From cozy family rooms and home offices to full in-law suites, our team manages every aspect of your basement renovation — design, permits, construction, and final inspection.</p>

    <h2>Basement Renovation Services in {n}</h2>
    <ul>
      <li><strong>Full Basement Finishing</strong> — Framing, insulation, drywall, electrical, flooring, and ceiling</li>
      <li><strong>Basement Bathroom Addition</strong> — 2-piece, 3-piece, or full bathroom with rough-in plumbing</li>
      <li><strong>In-Law Suite &amp; ADU</strong> — Legal secondary unit with kitchen, bathroom, and separate entrance</li>
      <li><strong>Basement Waterproofing</strong> — Interior drain tile, sump pump, exterior membrane systems</li>
      <li><strong>Egress Window Installation</strong> — Larger windows for natural light and code-compliant emergency egress</li>
      <li><strong>Home Theater, Gym &amp; Bar</strong> — Custom entertainment and recreation spaces</li>
    </ul>

    <h2>Why {n} Homeowners Choose aMaximum for Basement Renovation</h2>
    <ul>
      <li>&#10003; Complete project management — one contractor for everything</li>
      <li>&#10003; Permit-managed — we handle all {n} building permits and inspections</li>
      <li>&#10003; Waterproofing expertise — wet basements resolved before finishing</li>
      <li>&#10003; In-law suite specialists — ADU design and compliance</li>
      <li>&#10003; Detailed written quote — no hidden costs</li>
      <li>&#10003; Serving {n} and {nb}</li>
    </ul>

    <h2>Basement Renovation Process in {n}</h2>
    <p>Our process: <strong>1) Free In-Home Consultation</strong> → <strong>2) Design &amp; Layout Planning</strong> → <strong>3) Permit Application</strong> → <strong>4) Waterproofing &amp; Structural Work</strong> → <strong>5) Rough-Ins (electrical, plumbing, HVAC)</strong> → <strong>6) Insulation, Drywall &amp; Finishing</strong> → <strong>7) Final Inspection &amp; Handover</strong>.</p>

    <h2>Frequently Asked Questions — Basement Renovation {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"Basement Renovation in {n} | Licensed Contractors | aMaximum Construction",
        meta_desc   = f"Expert basement renovation services in {n} — full finishing, in-law suites, waterproofing, and bathroom additions. Licensed, permit-managed. Free quotes.",
        h1          = f"Basement Renovation Service in {n}",
        hero_sub    = f"Full basement finishing, in-law suites, and waterproofing in {n}",
        content_html= content,
        cta_h2      = f"Free Basement Renovation Consultation in {n}",
        cta_p       = f"Book your free in-home consultation — we assess your {n} basement and provide a detailed quote.",
        location_name = n,
        service_type  = "Basement Renovation",
        service_label = "Basement Renovation",
        faqs          = faqs,
    )


def gen_home_renovation(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"home-renovation-{s}"
    faqs = [
        (f"Where do I start with a home renovation in {n}?",
         f"Start with a clear budget and priority list. Then consult a general contractor in {n} — aMaximum Construction offers free consultations to help you plan scope, timeline, and budget. We handle design coordination, permits, and construction from a single point of contact."),
        (f"How much does a home renovation cost in {n}?",
         f"Home renovation costs in {n} vary widely: kitchen renovations average $25,000–$75,000; bathroom renovations $15,000–$40,000; full home renovations $100,000–$300,000+. We provide a detailed, itemized quote after assessing your {n} property."),
        (f"How do I avoid renovation scams in {n}?",
         f"Always hire a registered Ontario contractor, get everything in writing, never pay more than 10% upfront, and verify insurance. aMaximum Construction is fully licensed, insured, and provides a detailed written contract before any work begins in {n}."),
    ]
    content = f"""\
    <h2>Home Renovation Services in {n}</h2>
    <p>aMaximum Construction is {n}'s trusted home renovation contractor for complete residential transformations. Whether you're updating a single room or planning a whole-home renovation, our experienced team manages every trade, every permit, and every detail — delivering results that increase your home's value and livability.</p>

    <h2>Types of Home Renovations We Do in {n}</h2>
    <ul>
      <li><strong>Kitchen Renovation</strong> — Custom cabinets, countertops, islands, and complete kitchen redesigns</li>
      <li><strong>Bathroom Renovation</strong> — Walk-in showers, freestanding tubs, vanities, tile, and fixture upgrades</li>
      <li><strong>Basement Renovation</strong> — Full finishing, in-law suites, home theaters, and gyms</li>
      <li><strong>Home Additions</strong> — Second-storey additions, rear extensions, and garage conversions</li>
      <li><strong>Interior Remodeling</strong> — Open-concept conversions, flooring, painting, and trim upgrades</li>
      <li><strong>Exterior Renovation</strong> — Siding, windows, roofing, and curb appeal improvements</li>
    </ul>

    <h2>Why {n} Homeowners Renovate With aMaximum Construction</h2>
    <ul>
      <li>&#10003; Single contractor for all trades — no coordination headaches</li>
      <li>&#10003; Full permit management — we handle all {n} building permits</li>
      <li>&#10003; Transparent pricing — detailed written quotes before work starts</li>
      <li>&#10003; Realistic timelines — we meet our schedules</li>
      <li>&#10003; Post-renovation warranty on workmanship</li>
      <li>&#10003; Serving {n} and {nb}</li>
    </ul>

    <h2>Renovation ROI in {n}</h2>
    <p>Kitchen and bathroom renovations consistently deliver the best ROI in {n}'s real estate market — typically 60–80% return on investment at resale. Basement finishing adds livable square footage with strong returns. aMaximum Construction helps you prioritize renovations that maximize your {n} home's value.</p>

    <h2>Frequently Asked Questions — Home Renovation {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"Home Renovation in {n} | Licensed Renovation Contractor | aMaximum Construction",
        meta_desc   = f"Complete home renovation services in {n} — kitchens, bathrooms, basements, additions, and whole-home remodels. Licensed contractor, free quotes.",
        h1          = f"Home Renovation in {n}",
        hero_sub    = f"Complete residential renovation services for {n} homes — kitchens, bathrooms, basements, and more",
        content_html= content,
        cta_h2      = f"Start Your {n} Home Renovation",
        cta_p       = f"Book a free in-home consultation and get a detailed renovation quote for your {n} property.",
        location_name = n,
        service_type  = "Home Renovation",
        service_label = "Home Renovation",
        faqs          = faqs,
    )


def gen_fence_contractor(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"fence-contractor-in-{s}"
    faqs = [
        (f"What types of fences do you install in {n}?",
         f"aMaximum Construction installs wood privacy fences, vinyl fences, aluminum ornamental fences, chain-link fences, cedar split-rail fences, and composite fences in {n}. We also build custom gates and arbors."),
        (f"Do I need a permit to build a fence in {n}?",
         f"In most Toronto and GTA municipalities, fences under 2 metres (6.5 feet) do not require a permit, but must comply with local fence bylaws regarding height, placement, and materials. aMaximum Construction reviews local {n} bylaws and handles any required permits."),
        (f"How long does fence installation take in {n}?",
         f"A standard residential fence in {n} is typically installed in 1–3 days depending on linear footage, terrain, and material. Concrete post footings require 24–48 hours to cure before panel installation."),
    ]
    content = f"""\
    <h2>Professional Fence Contractor in {n}</h2>
    <p>aMaximum Construction is a trusted fence contractor serving {n} and the Greater Toronto Area. From classic wood privacy fences to modern aluminum and vinyl systems, we install durable, attractive fences that enhance your property's security, privacy, and curb appeal.</p>

    <h2>Fence Installation Services in {n}</h2>
    <ul>
      <li><strong>Wood Privacy Fence</strong> — Cedar, pressure-treated, and board-on-board privacy fencing</li>
      <li><strong>Vinyl Fence</strong> — Low-maintenance PVC panels in privacy, picket, and rail styles</li>
      <li><strong>Aluminum Ornamental Fence</strong> — Elegant powder-coated aluminum for decorative and security applications</li>
      <li><strong>Chain-Link Fence</strong> — Economical galvanized or vinyl-coated chain-link for residential and commercial</li>
      <li><strong>Composite Fence</strong> — Wood-look composite that resists rot, insects, and UV fading</li>
      <li><strong>Custom Gates &amp; Arbors</strong> — Matching gates with manual and automatic opener options</li>
    </ul>

    <h2>Why Choose aMaximum Construction for Fence Installation in {n}</h2>
    <ul>
      <li>&#10003; Bylaw-compliant — we review {n} fence bylaws before installation</li>
      <li>&#10003; Concrete post footings — proper depth for frost resistance</li>
      <li>&#10003; Precision levelling on all terrains including slopes</li>
      <li>&#10003; Clean installs — all debris removed</li>
      <li>&#10003; Competitive pricing with written quotes</li>
      <li>&#10003; Serving {n}, {nb}</li>
    </ul>

    <h2>Fence Maintenance Tips for {n}'s Climate</h2>
    <p>Wood fences in {n} should be sealed or stained every 2–3 years to resist moisture and UV damage. Vinyl and aluminum require only occasional washing. Composite fencing is the lowest-maintenance option. aMaximum Construction offers annual maintenance packages for {n} homeowners.</p>

    <h2>Frequently Asked Questions — Fence Installation {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"Fence Contractor in {n} | Wood, Vinyl & Aluminum Fencing | aMaximum Construction",
        meta_desc   = f"Professional fence installation in {n} — wood, vinyl, aluminum, and chain-link fencing. Licensed, insured fence contractors. Free quotes from aMaximum Construction.",
        h1          = f"Fence Contractor in {n}",
        hero_sub    = f"Wood, vinyl, aluminum, and chain-link fence installation in {n}",
        content_html= content,
        cta_h2      = f"Get a Free Fence Quote in {n}",
        cta_p       = f"Contact aMaximum Construction for a free on-site measurement and quote in {n}.",
        location_name = n,
        service_type  = "Fence Installation",
        service_label = "Fence Contractor",
        faqs          = faqs,
    )


def gen_interlocking(loc):
    n, s, nb = loc["name"], loc["slug"], loc["nearby"]
    slug = f"interlocking-stone-services-in-{s}"
    faqs = [
        (f"What interlocking stone services do you offer in {n}?",
         f"aMaximum Construction installs interlocking driveways, patios, walkways, pool surrounds, steps, retaining walls, and border accents in {n} using concrete pavers, natural stone, and porcelain tiles."),
        (f"How much does interlocking cost in {n}?",
         f"Interlocking paver installation in {n} typically costs $15–$30 per sq ft installed, depending on paver material, pattern complexity, and site preparation required. Driveways average $8,000–$25,000 for standard sizes. Contact us for a free measurement and quote."),
        (f"How long does interlocking last in {n}'s climate?",
         f"Quality interlocking pavers in {n} last 25–40 years when properly installed with adequate base preparation. Ontario's freeze-thaw cycles require a minimum 12\" compacted granular base and proper drainage to prevent heaving and settling."),
    ]
    content = f"""\
    <h2>Interlocking Stone Services in {n}</h2>
    <p>aMaximum Construction designs and installs beautiful interlocking stone driveways, patios, and walkways throughout {n}. Using premium concrete pavers, natural stone, and porcelain, we create durable outdoor surfaces that enhance your property's curb appeal and stand up to Ontario's demanding climate.</p>

    <h2>Interlocking Services We Provide in {n}</h2>
    <ul>
      <li><strong>Interlocking Driveway</strong> — Concrete paver driveways with proper base and drainage for {n}'s winters</li>
      <li><strong>Patio Installation</strong> — Natural stone, concrete, and porcelain patio designs</li>
      <li><strong>Walkways &amp; Paths</strong> — Front entry walkways, garden paths, and side-yard passages</li>
      <li><strong>Pool Surrounds</strong> — Slip-resistant paver surfaces around in-ground pools</li>
      <li><strong>Steps &amp; Risers</strong> — Natural stone and paver steps for front entries and terraced gardens</li>
      <li><strong>Retaining Walls &amp; Borders</strong> — Segmental retaining walls and decorative border accents</li>
    </ul>

    <h2>Why {n} Homeowners Choose Our Interlocking Services</h2>
    <ul>
      <li>&#10003; Proper base preparation — minimum 12" compacted granular base</li>
      <li>&#10003; Polymeric sand jointing — locks pavers and prevents weed growth</li>
      <li>&#10003; Sealed finish available — enhances colour and resists staining</li>
      <li>&#10003; Wide material selection — Cambridge, Unilock, Belgard, natural stone</li>
      <li>&#10003; Lifetime substrate warranty on our installations</li>
      <li>&#10003; Serving {n} and {nb}</li>
    </ul>

    <h2>Interlocking vs. Concrete &amp; Asphalt in {n}</h2>
    <p>Interlocking pavers outperform poured concrete and asphalt in {n}'s freeze-thaw climate. Individual pavers flex with ground movement — eliminating the cracking common in poured slabs. Damaged pavers can be replaced individually without replacing the entire surface. The result is a longer-lasting, better-looking driveway or patio.</p>

    <h2>Frequently Asked Questions — Interlocking Stone {n}</h2>
    {"".join(f"    <h3>{q}</h3>\n    <p>{a}</p>\n" for q, a in faqs)}"""

    return build_page(
        slug        = slug,
        meta_title  = f"Interlocking Stone Services in {n} | Driveways & Patios | aMaximum Construction",
        meta_desc   = f"Expert interlocking stone installation in {n} — driveways, patios, walkways, steps, and retaining walls. Premium pavers, proper base, free quotes.",
        h1          = f"Interlocking Stone Services in {n}",
        hero_sub    = f"Driveways, patios, walkways, and retaining walls in {n}",
        content_html= content,
        cta_h2      = f"Get a Free Interlocking Quote in {n}",
        cta_p       = f"Free on-site measurement and design consultation for your {n} interlocking project.",
        location_name = n,
        service_type  = "Interlocking Stone Installation",
        service_label = "Interlocking Stone Services",
        faqs          = faqs,
    )


# ── Pages already covered by existing files (skip to avoid overwriting) ───────
SKIP_EXISTING = {
    "deck-contractor-markham", "deck-contractor-north-york", "deck-contractor-scarborough",
    "deck-contractor-king-city", "deck-contractor-woodbridge",
    "deck-builder", "deck-builder-in-richmond-hill", "deck-builder-newmarket",
    "deck-builder-toronto", "deck-builder-gta", "deck-builder-schomberg",
    "deck-railing-builder-richmond-hill", "deck-railing-installer-east-york",
    "privacy-screen-deck", "trex-rainescape-system-toronto",
    "best-decking-materials-outdoor-decks", "building-a-small-deck-in-toronto",
    "expert-deck-building-in-aurora", "deck-maintenance-in-markhams-variable-climate",
    "how-to-repair-wood-decks-2", "starting-deck-boards-installation",
    "what-is-a-good-price-for-a-deck-in-toronto",
}

# ── Run ───────────────────────────────────────────────────────────────────────
GENERATORS = [
    gen_general_contractor,
    gen_carpenter,
    gen_demolition,
    gen_handyman,
    gen_deck_contractor,
    gen_deck_railing,
    gen_basement_renovation,
    gen_home_renovation,
    gen_fence_contractor,
    gen_interlocking,
]

SERVICE_NAMES = [
    "General Contractor", "Carpenter Services", "Demolition Service",
    "Handyman Service",   "Deck Contractor",    "Deck Railing Installer",
    "Basement Renovation","Home Renovation",    "Fence Contractor",
    "Interlocking Stone",
]

if __name__ == "__main__":
    total = 0
    skipped = 0
    for gen, sname in zip(GENERATORS, SERVICE_NAMES):
        print(f"\n-- {sname} --")
        for loc in LOCATIONS:
            # Determine slug for skip check
            test_html = gen(loc)
            # Extract slug from canonical in html
            import re
            m = re.search(r'<link rel="canonical" href="https://amaximumconstruction\.com/([^/]+)/', test_html)
            slug = m.group(1) if m else ""
            if slug in SKIP_EXISTING:
                print(f"  –  /{slug}/  (skipped — existing file)")
                skipped += 1
                continue
            write_page(slug, test_html)
            total += 1

    print(f"\n{'='*50}")
    print(f"Done. Created: {total} pages | Skipped: {skipped}")
