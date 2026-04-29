"""
Optimize all 18 service hub pages following top competitor patterns:
1. Title: 50-65 chars, city in title
2. Meta desc: 140-160 chars with CTA
3. Schema: LocalBusiness + Service (proper)
4. Remove old div.container/content
5. Add rich intro section (process, types, pricing range)
6. Fix H1 to be specific + city
"""
import re
from pathlib import Path

root = Path('.')

PHONE = "(647) 967-8555"
EMAIL = "info@amaximumconstruction.com"
DOMAIN = "https://amaximumconstruction.com"

# ─── Per-service data ─────────────────────────────────────────────────────────
SERVICES = {
    'deck-builder': {
        'title': 'Custom Deck Builder in Toronto & GTA | aMaximum',
        'desc': 'Licensed deck builders serving Toronto & GTA. Custom decks, composite & pressure-treated. Fixed quotes, permit-managed. Call (647) 967-8555.',
        'h1': 'Custom Deck Builder in Toronto & GTA',
        'hero_p': 'aMaximum Construction designs and builds beautiful, durable decks across Toronto, Markham, Richmond Hill, Vaughan & all of the GTA. Licensed, insured, and permit-managed.',
        'book': '/book-deck.html',
        'schema_service': 'Deck Building',
        'price_range': '$8,000 – $45,000',
        'icon': '🏗️',
        'process': [
            ('Free Consultation', 'We visit your property, discuss your vision and measure the space — no obligation.'),
            ('Custom Design & Quote', 'Detailed drawing and fixed written quote. No hidden costs.'),
            ('Permits & Materials', 'We pull all required permits and source quality materials — composite or wood.'),
            ('Build & Cleanup', 'Professional installation on schedule. Clean site daily, final walk-through with you.'),
        ],
        'service_types': [
            ('🪵', 'Pressure-Treated Decks', 'Durable and budget-friendly. Ideal for ground-level and elevated builds.'),
            ('♻️', 'Composite Decking', 'Trex, TimberTech — low maintenance, fade-resistant, 25-year warranty.'),
            ('🏠', 'Multi-Level Decks', 'Complex split-level designs that maximize your outdoor space.'),
            ('🔧', 'Deck Repairs & Restoration', 'Board replacement, structural repairs, staining and sealing.'),
            ('🌿', 'Rooftop & Balcony Decks', 'Urban outdoor spaces with proper waterproofing and drainage.'),
            ('🎨', 'Custom Design & Railings', 'Glass, aluminum or wood railings integrated into the deck design.'),
        ],
        'faq': [
            ('How much does a deck cost in Toronto?', 'A basic pressure-treated deck starts around $8,000–$12,000. Composite decks range from $15,000–$45,000 depending on size, material, and complexity. We provide free detailed quotes.'),
            ('Do I need a permit for a deck in Toronto?', 'Yes — most decks over 24 inches above grade require a building permit. aMaximum handles all permit applications and inspections on your behalf.'),
            ('How long does it take to build a deck?', 'A standard deck takes 3–7 business days once permits are approved. Permit approval in Toronto typically takes 2–6 weeks.'),
            ('What decking material is best for Toronto weather?', 'Composite decking (Trex, TimberTech) handles Toronto\'s freeze-thaw cycles best — no warping, cracking, or splinting. Pressure-treated cedar is a great natural option with proper maintenance.'),
            ('Do you offer a warranty on deck building?', 'Yes — we provide a written workmanship warranty on all our builds. Composite materials carry manufacturer warranties of 25–50 years.'),
        ],
    },
    'deck-railings': {
        'title': 'Deck Railings Toronto & GTA | Glass, Aluminum, Wood',
        'desc': 'Deck railing installation in Toronto & GTA. Glass, aluminum, cable & wood railings. Licensed contractors, free quotes. Call (647) 967-8555.',
        'h1': 'Deck Railing Installation in Toronto & GTA',
        'hero_p': 'aMaximum Construction installs safe, beautiful deck railings across Toronto and the GTA. Glass, aluminum, cable, and wood — code-compliant and built to last.',
        'book': '/book-railing.html',
        'schema_service': 'Deck Railing Installation',
        'price_range': '$2,500 – $15,000',
        'icon': '🔩',
        'process': [
            ('Free Measurement', 'We measure your deck perimeter and assess existing structure.'),
            ('Design & Material Selection', 'Choose from glass, aluminum, cable or wood — we show samples.'),
            ('Code Check & Quote', 'Fixed written quote, building-code compliant design confirmed.'),
            ('Install & Inspect', 'Professional installation, load-tested, cleaned up same day.'),
        ],
        'service_types': [
            ('🔮', 'Glass Railings', 'Frameless or semi-frameless tempered glass — open views, modern look.'),
            ('🔩', 'Aluminum Railings', 'Powder-coated, rust-proof, low maintenance. Most popular choice in GTA.'),
            ('🪵', 'Wood Railings', 'Cedar or pressure-treated. Classic look, paintable, budget-friendly.'),
            ('🔗', 'Cable Railings', 'Stainless steel cable — sleek, coastal aesthetic, strong.'),
            ('⚫', 'Iron & Metal Railings', 'Wrought iron or steel — ornamental and extremely durable.'),
            ('🎨', 'Custom Designs', 'Mixed materials, custom patterns, decorative post caps.'),
        ],
        'faq': [
            ('What height must deck railings be in Toronto?', 'Ontario Building Code requires railings on decks over 600mm (24") above grade. For decks above 1.8m, railings must be at least 1,070mm (42") high.'),
            ('How much do deck railings cost?', 'Aluminum railings start around $90–$130 per linear foot installed. Glass railings range from $150–$250/ft. We provide free quotes.'),
            ('How long does railing installation take?', 'Most residential railing projects are completed in 1–2 days.'),
            ('Can you replace just part of my railing?', 'Yes — we do partial repairs and full replacements. We match existing styles where possible.'),
            ('Do railings need a permit?', 'Railing replacement on an existing permitted deck usually doesn\'t require a new permit. New deck + railing builds do. We handle all permits.'),
        ],
    },
    'fence-contractor-in-toronto': {
        'title': 'Fence Contractor Toronto & GTA | Wood, Vinyl, Chain Link',
        'desc': 'Licensed fence contractor in Toronto & GTA. Wood, vinyl, aluminum & chain link fences. Free quotes, permit-managed. Call (647) 967-8555.',
        'h1': 'Fence Installation in Toronto & GTA',
        'hero_p': 'aMaximum Construction installs privacy fences, picket fences, vinyl, and chain link across Toronto and the GTA. Licensed, insured, and permit-managed.',
        'book': '/book-fence.html',
        'schema_service': 'Fence Installation',
        'price_range': '$4,000 – $18,000',
        'icon': '🏡',
        'process': [
            ('Free Site Visit', 'We assess your property lines, survey stakes, and discuss your needs.'),
            ('Design & Quote', 'Fixed price quote with materials and style confirmed in writing.'),
            ('Permit if Required', 'We handle fence permit applications with the City of Toronto.'),
            ('Install & Cleanup', 'Professional crew installs on schedule. Full cleanup after completion.'),
        ],
        'service_types': [
            ('🪵', 'Wood Privacy Fences', 'Cedar or pressure-treated. 6ft privacy fences are our most popular.'),
            ('🤍', 'Vinyl / PVC Fences', 'Never rot, no painting needed. 20+ year lifespan.'),
            ('🔩', 'Aluminum Fences', 'Ornamental aluminum — decorative and maintenance-free.'),
            ('⛓️', 'Chain Link Fences', 'Durable and budget-friendly. Good for large yards and commercial.'),
            ('🚪', 'Gate Installation', 'Single, double, or sliding gates with hardware and latches.'),
            ('🌿', 'Lattice & Decorative', 'Trellis, lattice-top privacy fences and decorative styles.'),
        ],
        'faq': [
            ('Do I need a permit for a fence in Toronto?', 'Fences under 2m (6.5ft) on residential properties generally don\'t need a permit in Toronto. Taller fences or fences near laneways may require one. We check this for you.'),
            ('How much does fence installation cost in Toronto?', 'A standard 6ft cedar privacy fence costs $40–$65 per linear foot installed. Vinyl is $50–$80/ft. We provide free detailed quotes.'),
            ('How long does fence installation take?', 'Most residential fences are installed in 1–3 days depending on length.'),
            ('Who is responsible for the fence between neighbours?', 'In Ontario, the Line Fences Act governs boundary fences. Costs are typically shared. We can advise you on your specific situation.'),
            ('Can you remove and replace my old fence?', 'Yes — we offer full demolition and disposal of old fencing as part of our installation service.'),
        ],
    },
    'bathroom-renovation': {
        'title': 'Bathroom Renovation Toronto & GTA | Licensed Contractors',
        'desc': 'Licensed bathroom renovation contractors in Toronto & GTA. Full renos, tile, plumbing & vanity. Fixed quotes, 5-star rated. Call (647) 967-8555.',
        'h1': 'Bathroom Renovation in Toronto & GTA',
        'hero_p': 'aMaximum Construction delivers full bathroom renovations across Toronto and the GTA — on time, on budget, and with a written workmanship warranty.',
        'book': '/book-bathroom.html',
        'schema_service': 'Bathroom Renovation',
        'price_range': '$12,000 – $45,000',
        'icon': '🚿',
        'process': [
            ('Design Consultation', 'We visit, measure, and help you choose fixtures, tile, and layout.'),
            ('Fixed Written Quote', 'Detailed scope, timeline, and fixed price — no surprises.'),
            ('Demo & Rough-In', 'Demo, waterproofing, plumbing and electrical rough-in.'),
            ('Finishing & Handover', 'Tile, fixtures, vanity, accessories — final walk-through with you.'),
        ],
        'service_types': [
            ('🚿', 'Full Bathroom Renovation', 'Complete gut and rebuild — layout changes, new plumbing, tile, fixtures.'),
            ('🛁', 'Shower & Tub Replacement', 'Walk-in showers, freestanding tubs, tub-to-shower conversions.'),
            ('🔲', 'Tile Installation', 'Floor and wall tile, heated floors, large format porcelain.'),
            ('🪞', 'Vanity & Storage', 'Custom and semi-custom vanities, medicine cabinets, built-in storage.'),
            ('🔧', 'Plumbing Updates', 'Fixture relocation, new supply lines, drain rough-in.'),
            ('💡', 'Lighting & Ventilation', 'Pot lights, vanity lighting, exhaust fans with timers.'),
        ],
        'faq': [
            ('How much does a bathroom renovation cost in Toronto?', 'A mid-range bathroom renovation in Toronto typically costs $15,000–$30,000. High-end renovations with custom tile and fixtures range $30,000–$50,000+. We provide free detailed quotes.'),
            ('How long does a bathroom renovation take?', 'A standard full bathroom renovation takes 2–4 weeks. Timeline depends on scope, permit requirements, and material lead times.'),
            ('Do I need a permit for a bathroom renovation in Toronto?', 'Moving or adding plumbing requires a plumbing permit. Structural changes need a building permit. We manage all required permits.'),
            ('Can you renovate a small bathroom?', 'Absolutely — we specialize in maximizing small bathroom spaces with smart layout choices and space-saving fixtures.'),
            ('What is the best tile for a bathroom?', 'Porcelain is the most durable and water-resistant. Large format tiles (24"x24") make small bathrooms look bigger. We help you choose during the design consultation.'),
        ],
    },
    'basement-renovation-service-in-toronto': {
        'title': 'Basement Renovation Toronto & GTA | Licensed Contractors',
        'desc': 'Licensed basement renovation contractors in Toronto & GTA. Finishing, waterproofing, in-law suites. Fixed quotes, permit-managed. Call (647) 967-8555.',
        'h1': 'Basement Renovation in Toronto & GTA',
        'hero_p': 'aMaximum Construction transforms unfinished basements into living spaces, in-law suites, and rental units across Toronto and the GTA. Licensed, insured, permit-managed.',
        'book': '/book-basement.html',
        'schema_service': 'Basement Renovation',
        'price_range': '$35,000 – $120,000',
        'icon': '🏠',
        'process': [
            ('Free Site Assessment', 'We inspect your basement, check ceiling height, plumbing rough-ins, and discuss your goals.'),
            ('Design & Permit', 'Floor plan, scope of work, fixed quote. We apply for all permits.'),
            ('Construction', 'Framing, insulation, electrical, plumbing, drywall — all trades coordinated by us.'),
            ('Finishing & Handover', 'Flooring, paint, trim, fixtures — final inspection and walk-through.'),
        ],
        'service_types': [
            ('🏠', 'Full Basement Finishing', 'Framing to flooring — turn raw concrete into beautiful living space.'),
            ('👪', 'In-Law Suite / Apartment', 'Second kitchen, separate entrance, full bathroom — legal rental unit.'),
            ('💧', 'Waterproofing', 'Interior and exterior waterproofing, sump pump installation, drainage.'),
            ('🎬', 'Home Theater / Rec Room', 'Custom media room with acoustic treatment, projector, wet bar.'),
            ('🏋️', 'Gym / Office', 'Rubber flooring, mirrors, proper ventilation for home gym or office.'),
            ('🔧', 'Underpinning', 'Basement lowering to increase ceiling height — we handle all engineering.'),
        ],
        'faq': [
            ('How much does a basement renovation cost in Toronto?', 'A basic basement finish (open concept, bathroom, flooring) starts around $35,000–$55,000. A full in-law suite with kitchen runs $75,000–$120,000+. We provide free quotes.'),
            ('Do I need a permit for a basement renovation?', 'Yes — any basement renovation involving framing, electrical, or plumbing requires a building permit in Toronto. We handle all permit applications.'),
            ('How long does a basement renovation take?', 'A standard basement finish takes 8–14 weeks. In-law suites with kitchens may take 16–20 weeks depending on permit timelines.'),
            ('Can I rent out my finished basement legally?', 'Yes — with a proper permit and second-suite registration. We build to Ontario Building Code standards required for legal rental units.'),
            ('What basement ceiling height is required for a legal apartment?', 'Ontario requires a minimum 1,950mm (6\'5") ceiling height in living areas for a legal basement apartment. We can lower the floor (underpin) if needed.'),
        ],
    },
    'handyman-plumbing-services': {
        'title': 'Plumbing Services Toronto & GTA | Licensed Plumbers',
        'desc': 'Licensed plumbers in Toronto & GTA. Drain cleaning, pipe repair, fixture install & leak detection. Fast response. Call (647) 967-8555.',
        'h1': 'Plumbing Services in Toronto & GTA',
        'hero_p': 'aMaximum Construction provides licensed plumbing services across Toronto and the GTA — from drain cleaning to full pipe replacement. Fast, reliable, and guaranteed.',
        'book': '/book-plumbing.html',
        'schema_service': 'Plumbing Services',
        'price_range': '$150 – $4,500',
        'icon': '🔧',
        'process': [
            ('Call or Book Online', 'Contact us for same-day or scheduled service. We confirm arrival window.'),
            ('Diagnosis & Quote', 'We diagnose the issue and provide a fixed price before any work starts.'),
            ('Repair or Install', 'Licensed plumber completes the work to Ontario code standards.'),
            ('Test & Guarantee', 'We test the system before leaving. Written warranty on all work.'),
        ],
        'service_types': [
            ('🚰', 'Drain Cleaning', 'Camera inspection, hydro-jetting, snake clearing for blocked drains.'),
            ('🔧', 'Pipe Repair & Replacement', 'Burst pipes, corroded lines, repiping — copper and PEX.'),
            ('🚿', 'Fixture Installation', 'Faucets, toilets, sinks, showers — supply and install.'),
            ('🌡️', 'Water Heater', 'Tank and tankless water heater installation and replacement.'),
            ('🔍', 'Leak Detection', 'Non-invasive leak detection, slab leaks, hidden pipe leaks.'),
            ('🏗️', 'Rough-In Plumbing', 'New bathroom, kitchen, basement — plumbing rough-in for renovations.'),
        ],
        'faq': [
            ('How much does a plumber cost in Toronto?', 'Plumbing service calls start around $150–$300 for diagnostics. Drain cleaning runs $250–$600. Pipe repairs vary by scope. We provide upfront quotes before any work.'),
            ('Do you offer emergency plumbing?', 'Yes — we offer priority service for urgent plumbing issues. Call (647) 967-8555 for urgent requests.'),
            ('Are your plumbers licensed in Ontario?', 'Yes — all our plumbers hold a valid Ontario Certificate of Qualification (306A) and are fully insured.'),
            ('How do I know if I have a hidden leak?', 'Signs include unexplained high water bills, damp drywall, mold smell, or water stains on ceilings. We use moisture meters and camera inspection to locate leaks.'),
            ('Can you fix the plumbing during a renovation?', 'Absolutely — we coordinate plumbing rough-in and finishing with your renovation schedule. All work is permit-managed.'),
        ],
    },
    'canopy': {
        'title': 'Canopy & Awning Installation Toronto & GTA | aMaximum',
        'desc': 'Canopy, pergola & awning installation in Toronto & GTA. Custom patio covers, carports & shade structures. Free quotes. Call (647) 967-8555.',
        'h1': 'Canopy & Awning Installation in Toronto & GTA',
        'hero_p': 'aMaximum Construction designs and installs custom canopies, pergolas, and awnings across Toronto and the GTA. Protect your outdoor space from sun, rain, and weather year-round.',
        'book': '/book-canopy.html',
        'schema_service': 'Canopy Installation',
        'price_range': '$3,500 – $25,000',
        'icon': '⛺',
        'process': [
            ('Free Site Consultation', 'We assess your space, discuss style options, and take measurements.'),
            ('Design & Fixed Quote', 'Custom design with fixed price — materials, labour, and hardware included.'),
            ('Engineering if Required', 'Larger structures may require engineer-stamped drawings. We arrange this.'),
            ('Installation & Finish', 'Professional installation by our crew. Complete cleanup on completion.'),
        ],
        'service_types': [
            ('⛺', 'Patio Canopies', 'Freestanding or attached canopy structures for patios and decks.'),
            ('🚗', 'Carport Installation', 'Single and double carports — metal frame, polycarbonate or fabric roof.'),
            ('☂️', 'Retractable Awnings', 'Manual or motorized awnings for doors, windows, and patios.'),
            ('🏛️', 'Pergolas', 'Open or lattice-roof pergolas — cedar, aluminum, or vinyl.'),
            ('🏢', 'Commercial Canopies', 'Storefront awnings, entrance canopies, commercial shade structures.'),
            ('🌧️', 'Shade Sails', 'Tensioned fabric shade structures for pools, playgrounds, and patios.'),
        ],
        'faq': [
            ('How much does a canopy cost in Toronto?', 'A basic retractable awning starts around $1,500–$3,500. Custom patio canopies range from $5,000–$15,000. Larger pergolas and carports run $10,000–$25,000+. Free quotes available.'),
            ('Do canopies need a permit in Toronto?', 'Attached structures over a certain size require a permit. Freestanding shade sails and small awnings often don\'t. We confirm permit requirements for your specific project.'),
            ('What materials are used for canopies?', 'We use aluminum frames (rust-proof), cedar wood, polycarbonate panels, and weather-resistant fabric. All materials are chosen for Toronto\'s climate.'),
            ('Can a canopy withstand Toronto winters?', 'We recommend removing retractable fabric awnings in winter. Permanent aluminum and polycarbonate canopies are engineered for snow loads to Ontario standards.'),
            ('How long does canopy installation take?', 'Most canopy and awning installations are completed in 1–3 days.'),
        ],
    },
    'landscaping-services-toronto': {
        'title': 'Landscaping Services Toronto & GTA | aMaximum Construction',
        'desc': 'Professional landscaping in Toronto & GTA. Lawn design, sod, garden beds, trees & cleanup. Licensed contractors. Free quotes. Call (647) 967-8555.',
        'h1': 'Landscaping Services in Toronto & GTA',
        'hero_p': 'aMaximum Construction delivers complete landscaping services across Toronto and the GTA — from sod and garden design to full yard transformations. Licensed, insured, and guaranteed.',
        'book': '/book-landscaping.html',
        'schema_service': 'Landscaping Services',
        'price_range': '$3,000 – $35,000',
        'icon': '🌿',
        'process': [
            ('Free Site Visit', 'We visit your property, discuss your vision, soil type, and sun exposure.'),
            ('Design & Quote', 'Custom landscape plan with fixed written quote — no hidden costs.'),
            ('Materials & Scheduling', 'We source plants, sod, and materials and schedule your project.'),
            ('Installation & Cleanup', 'Professional crew installs on schedule. Full site cleanup on completion.'),
        ],
        'service_types': [
            ('🌱', 'Lawn & Sod Installation', 'New sod, overseeding, grading and lawn restoration.'),
            ('🌸', 'Garden Design & Planting', 'Annual and perennial beds, shrubs, trees, and seasonal colour.'),
            ('🪨', 'Mulching & Ground Cover', 'Mulch, gravel, and stone ground cover for low-maintenance beds.'),
            ('✂️', 'Yard Cleanup & Maintenance', 'Spring/fall cleanup, pruning, edging, and ongoing maintenance.'),
            ('💧', 'Irrigation Systems', 'Drip and sprinkler irrigation design and installation.'),
            ('🔆', 'Landscape Lighting', 'Solar and low-voltage landscape lighting for paths and features.'),
        ],
        'faq': [
            ('How much does landscaping cost in Toronto?', 'Basic yard cleanup starts around $500–$1,500. Full landscaping projects (design, sod, garden beds) range from $5,000–$35,000+ depending on scope. Free quotes available.'),
            ('What is the best time to install sod in Toronto?', 'Spring (April–June) and early fall (August–September) are ideal. We can install sod during summer with proper irrigation.'),
            ('Do you offer ongoing maintenance?', 'We focus on installation projects. For ongoing maintenance, we can recommend trusted partners.'),
            ('Can you remove existing landscaping?', 'Yes — we offer full demo and disposal of existing plants, sod, and garden beds before new installation.'),
            ('What plants work best in Toronto\'s climate?', 'We recommend native Ontario plants (coneflower, black-eyed Susan, ornamental grasses) for low maintenance. We also design for Zone 6b hardy annuals and perennials.'),
        ],
    },
    'general-contractor-in-toronto': {
        'title': 'General Contractor Toronto & GTA | Licensed & Insured',
        'desc': 'Licensed general contractor in Toronto & GTA. Full home renovations, additions, permit management. Fixed quotes. Call (647) 967-8555.',
        'h1': 'General Contractor in Toronto & GTA',
        'hero_p': 'aMaximum Construction is a licensed general contractor serving Toronto and the GTA since 2018. We manage full renovations, additions, and complex multi-trade projects — one contract, one point of contact.',
        'book': '/book-contractor.html',
        'schema_service': 'General Contracting',
        'price_range': '$25,000 – $300,000',
        'icon': '🏗️',
        'process': [
            ('Project Assessment', 'We meet on-site, review your goals, scope, and budget range.'),
            ('Design & Permits', 'We coordinate architects/designers and manage all permit applications.'),
            ('Construction Management', 'We schedule and supervise all trades — framing, electrical, plumbing, drywall.'),
            ('Finishing & Handover', 'Final finishes, inspections, and walk-through with occupancy confirmation.'),
        ],
        'service_types': [
            ('🏠', 'Full Home Renovation', 'Whole-home or multi-room gut-and-rebuild with all trades managed.'),
            ('➕', 'Home Additions', 'Second floor, rear addition, garage conversion — all permit-managed.'),
            ('📋', 'Project Management', 'We manage your existing trades as the general contractor.'),
            ('🏗️', 'Structural Work', 'Load-bearing wall removal, beam installation, structural modifications.'),
            ('🔑', 'Design-Build', 'From concept to keys — we handle design, permits, and construction.'),
            ('🏢', 'Commercial Renovation', 'Office fit-outs, retail, restaurants — commercial renovation experience.'),
        ],
        'faq': [
            ('What does a general contractor do?', 'A GC manages all trades (framing, electrical, plumbing, drywall, finishes), coordinates scheduling, pulls permits, and is your single point of contact for the entire project.'),
            ('How much does a general contractor charge in Toronto?', 'GC fees are typically 15–25% of total project cost, included in our fixed quote. We charge for the project — not by the hour.'),
            ('Do I need a general contractor for my renovation?', 'For projects involving multiple trades, permits, or structural changes — yes. A GC saves you time, stress, and money by preventing costly mistakes and delays.'),
            ('Are you licensed in Ontario?', 'Yes — aMaximum Construction is a licensed and insured contractor in Ontario with WSIB coverage and $2M liability insurance.'),
            ('How long does a full home renovation take?', 'A typical whole-home renovation takes 4–8 months depending on scope and permit timelines. We provide a detailed schedule at the quote stage.'),
        ],
    },
    'handyman-service-in-toronto': {
        'title': 'Handyman Service Toronto & GTA | Reliable & Licensed',
        'desc': 'Professional handyman services in Toronto & GTA. Drywall, assembly, repairs, painting & more. Fixed quotes. Call (647) 967-8555.',
        'h1': 'Handyman Services in Toronto & GTA',
        'hero_p': 'aMaximum Construction provides reliable handyman services across Toronto and the GTA. From minor repairs to multi-room updates — no job is too small.',
        'book': '/book-handy.html',
        'schema_service': 'Handyman Services',
        'price_range': '$150 – $3,500',
        'icon': '🔨',
        'process': [
            ('Book Online or Call', 'Schedule your service. We confirm a 2-hour arrival window.'),
            ('Assessment & Quote', 'We assess the job and provide a fixed price before starting.'),
            ('Efficient Repair', 'Our handyman completes the work promptly and professionally.'),
            ('Cleanup & Guarantee', 'We clean up after every job and back our work with a warranty.'),
        ],
        'service_types': [
            ('🧱', 'Drywall Repair', 'Holes, cracks, water damage — patch and texture match.'),
            ('🪑', 'Furniture Assembly', 'IKEA and flatpack assembly — quick and stress-free.'),
            ('🚪', 'Door & Window Repairs', 'Sticking doors, broken locks, window hardware, weather stripping.'),
            ('🎨', 'Painting & Touch-Ups', 'Room painting, trim, touch-ups, feature walls.'),
            ('💡', 'Minor Electrical', 'Switch/outlet replacement, light fixture installation, fan mounting.'),
            ('🔧', 'General Repairs', 'Caulking, grout, shelving, TV mounting, tile replacement.'),
        ],
        'faq': [
            ('How much does a handyman cost in Toronto?', 'Handyman services typically start at $150–$250 for a first hour. Most small jobs are completed in 2–4 hours. We provide fixed quotes before starting any work.'),
            ('Do you have a minimum charge?', 'We have a minimum service call of $150. Most jobs are quoted at a fixed price.'),
            ('Are your handymen licensed and insured?', 'Yes — all our handymen are insured and our company carries $2M liability insurance and WSIB coverage.'),
            ('Can you do multiple small jobs in one visit?', 'Absolutely — our handymen can tackle a list of small tasks in a single visit, making it efficient and cost-effective.'),
            ('How quickly can you come?', 'We typically schedule within 2–5 business days. For urgent requests, call us directly at (647) 967-8555.'),
        ],
    },
    'interlocking-paver-services': {
        'title': 'Interlocking & Paving Toronto & GTA | Licensed Contractors',
        'desc': 'Interlocking stone and paving services in Toronto & GTA. Driveways, patios, walkways & retaining walls. Fixed quotes. Call (647) 967-8555.',
        'h1': 'Interlocking & Paving Services in Toronto & GTA',
        'hero_p': 'aMaximum Construction installs interlocking stone driveways, patios, and walkways across Toronto and the GTA. Proper base preparation, clean edges, and long-lasting results.',
        'book': '/book-interlock.html',
        'schema_service': 'Interlocking Paving',
        'price_range': '$6,000 – $40,000',
        'icon': '🧱',
        'process': [
            ('Free Site Assessment', 'We assess grading, drainage, and existing surface condition.'),
            ('Design & Quote', 'Pattern, stone selection, fixed written quote.'),
            ('Excavation & Base', 'Proper excavation, granular base, and compaction — the critical step.'),
            ('Install & Edge Restraints', 'Stone laying, cuts, polymeric sand, and edge restraints.'),
        ],
        'service_types': [
            ('🚗', 'Driveway Paving', 'Interlocking stone or concrete driveway — engineered for vehicles.'),
            ('🏡', 'Patio Installation', 'Backyard patio in natural stone, concrete pavers, or tumbled brick.'),
            ('🚶', 'Walkway & Path', 'Front walkway, garden paths, stepping stones.'),
            ('🧱', 'Retaining Walls', 'Armour stone, concrete block, and interlocking retaining walls.'),
            ('🏊', 'Pool Deck Paving', 'Slip-resistant paving around pools with proper drainage.'),
            ('🔧', 'Re-Leveling & Repairs', 'Lifting and resetting sunken or heaved interlock pavers.'),
        ],
        'faq': [
            ('How much does interlocking cost in Toronto?', 'Interlocking driveways start around $15–$25 per sq ft installed. Patios and walkways run $12–$20/sq ft. Total project costs typically range $6,000–$40,000. Free quotes available.'),
            ('How long does interlocking last?', 'A properly installed interlocking driveway lasts 25–30 years with minimal maintenance. The key is proper base preparation — 8–12 inches of compacted granular.'),
            ('Do interlocking pavers need a permit?', 'Most residential interlocking projects don\'t need a permit. Projects involving drainage changes or retaining walls over 1m may require one.'),
            ('Why is my old interlock sinking?', 'Usually caused by improper base depth or compaction. We excavate to the proper depth and use compacted granular A base to prevent heaving.'),
            ('What is polymeric sand?', 'Polymeric sand is a joint-filling compound that hardens when wet, preventing weed growth and ant infiltration between pavers. We use it on all installs.'),
        ],
    },
    'carpenter-services': {
        'title': 'Carpentry Services Toronto & GTA | Custom & Finish Work',
        'desc': 'Licensed carpenters in Toronto & GTA. Custom cabinetry, trim, built-ins, doors & stairs. Quality craftsmanship. Free quotes. Call (647) 967-8555.',
        'h1': 'Carpentry Services in Toronto & GTA',
        'hero_p': 'aMaximum Construction provides finish and rough carpentry services across Toronto and the GTA. From custom built-ins to trim and staircase work — quality craftsmanship guaranteed.',
        'book': '/book-carpentry.html',
        'schema_service': 'Carpentry Services',
        'price_range': '$800 – $25,000',
        'icon': '🪵',
        'process': [
            ('Consultation & Measurement', 'We visit, measure, and discuss design, wood species, and finish.'),
            ('Design & Quote', 'Custom drawings and fixed price before any work begins.'),
            ('Shop or Site Build', 'Cabinetry built in our shop or on-site depending on scope.'),
            ('Install & Finishing', 'Professional installation, caulking, painting or staining.'),
        ],
        'service_types': [
            ('🗄️', 'Custom Cabinetry', 'Kitchen, bathroom, laundry, and built-in cabinetry — fully custom.'),
            ('📐', 'Trim & Molding', 'Crown molding, baseboards, casing, wainscoting, coffered ceilings.'),
            ('📚', 'Built-In Shelving', 'Home office built-ins, entertainment walls, mudroom built-ins.'),
            ('🚪', 'Door Installation', 'Interior and exterior door installation, barn doors, pocket doors.'),
            ('🪜', 'Staircase Building', 'New staircase construction, stringer repair, railing integration.'),
            ('🔧', 'Rough Carpentry', 'Framing, sheathing, structural carpentry for renovation projects.'),
        ],
        'faq': [
            ('How much does custom carpentry cost in Toronto?', 'Custom built-in shelving starts around $2,000–$5,000. Full kitchen cabinetry runs $8,000–$25,000+. Trim and molding projects vary by linear footage. Free quotes provided.'),
            ('How long do carpentry projects take?', 'Small trim projects take 1–2 days. Custom cabinetry and built-ins typically take 2–4 weeks including shop time.'),
            ('What wood species do you work with?', 'We work with MDF (for painted finishes), maple, oak, walnut, and pine. We recommend the best species for your application and budget.'),
            ('Can you match existing trim and molding in my home?', 'Yes — we can match existing profiles using custom router work or sourcing matching stock profiles.'),
            ('Do you paint or stain the carpentry?', 'We offer priming, painting, and staining as part of our full-service carpentry package.'),
        ],
    },
    'electrical-handyman-services': {
        'title': 'Electrical Handyman Toronto & GTA | Licensed Electricians',
        'desc': 'Licensed electrical services in Toronto & GTA. Panel upgrades, outlets, lighting, EV chargers. Fully insured. Free quotes. Call (647) 967-8555.',
        'h1': 'Electrical Services in Toronto & GTA',
        'hero_p': 'aMaximum Construction provides licensed electrical services across Toronto and the GTA. Panel upgrades, EV charger installation, lighting, and renovation rough-in — all to Ontario Electrical Safety Code.',
        'book': '/book-electrical.html',
        'schema_service': 'Electrical Services',
        'price_range': '$250 – $8,000',
        'icon': '⚡',
        'process': [
            ('Assessment & Quote', 'We assess your panel, wiring, and load requirements. Fixed quote before work.'),
            ('ESA Permit', 'We pull an Electrical Safety Authority (ESA) permit for all permitted work.'),
            ('Electrical Work', 'Licensed electrician completes work to Ontario Electrical Safety Code.'),
            ('Inspection & Certificate', 'ESA inspection and certificate of acceptance provided on completion.'),
        ],
        'service_types': [
            ('⚡', 'Panel Upgrades', '100A to 200A panel upgrade — required for EV chargers and major renovations.'),
            ('🔌', 'Outlet & Switch Installation', 'New outlets, USB outlets, GFCI, AFCI — code-compliant installation.'),
            ('💡', 'Lighting Installation', 'Pot lights, pendant lights, under-cabinet lighting, dimmer switches.'),
            ('🚗', 'EV Charger Installation', 'Level 2 EV charger (240V) installation — panel assessment included.'),
            ('🔧', 'Renovation Rough-In', 'Electrical rough-in for bathroom, kitchen, basement renovations.'),
            ('🔍', 'Electrical Inspection', 'Pre-purchase inspection, safety audit, knob-and-tube assessment.'),
        ],
        'faq': [
            ('How much does an electrician cost in Toronto?', 'Electrical service calls start at $250–$400. Panel upgrades run $2,500–$5,000. EV charger installation is $800–$1,800 depending on panel capacity. Free quotes available.'),
            ('Do you pull ESA permits?', 'Yes — we pull ESA permits for all work that requires them (panel upgrades, new circuits, EV chargers). This protects you and ensures insurance compliance.'),
            ('Can you install an EV charger in my condo?', 'Condo EV charger installation requires strata/condo board approval and often a dedicated circuit from your panel. We assess feasibility and guide you through the process.'),
            ('What is a panel upgrade and do I need one?', 'If your home has a 60A or 100A panel, you may need a 200A upgrade for EV chargers, hot tubs, or major renovations. We assess your load requirements.'),
            ('Is electrical work dangerous to DIY?', 'Electrical work without a permit and proper licensing violates Ontario law, voids homeowner insurance, and creates fire hazards. Always use a licensed electrician.'),
        ],
    },
    'handyman-painting-services': {
        'title': 'Painting Services Toronto & GTA | Interior & Exterior',
        'desc': 'Professional painting services in Toronto & GTA. Interior, exterior, cabinet painting & deck staining. Fixed quotes. Call (647) 967-8555.',
        'h1': 'Painting Services in Toronto & GTA',
        'hero_p': 'aMaximum Construction delivers professional painting services across Toronto and the GTA. Interior, exterior, cabinet painting, and deck staining — clean work, crisp lines, and lasting results.',
        'book': '/book-painting.html',
        'schema_service': 'Painting Services',
        'price_range': '$800 – $15,000',
        'icon': '🎨',
        'process': [
            ('Colour Consultation', 'We help you choose colours, sheens, and finishes for your space.'),
            ('Prep & Protection', 'Proper surface prep — filling, sanding, priming — and full furniture protection.'),
            ('Paint Application', 'Two coats minimum with professional tools for even, streak-free finish.'),
            ('Cleanup & Touch-Up', 'Full cleanup, touch-ups, and final walk-through with you.'),
        ],
        'service_types': [
            ('🏠', 'Interior Painting', 'Rooms, hallways, ceilings, trim — full interior painting packages.'),
            ('🏡', 'Exterior Painting', 'Siding, trim, doors, fences — weather-resistant exterior paints.'),
            ('🗄️', 'Cabinet Painting', 'Kitchen and bathroom cabinet refinishing — spray finish available.'),
            ('🪵', 'Deck Staining & Sealing', 'Cleaning, sanding, stain, and sealer application for wood decks.'),
            ('🧱', 'Wallpaper Removal', 'Wallpaper stripping and surface prep before painting.'),
            ('🖌️', 'Feature Walls', 'Accent walls, geometric patterns, textured finishes.'),
        ],
        'faq': [
            ('How much does interior painting cost in Toronto?', 'A standard bedroom costs $300–$500 to paint. A full home interior (1,500 sq ft) runs $3,000–$6,000. We provide room-by-room quotes so you know exactly what you are paying.'),
            ('How many coats of paint do you apply?', 'We apply primer (on bare or stained surfaces) plus two finish coats minimum. This gives the best coverage and durability.'),
            ('What paint brands do you use?', 'We use Benjamin Moore and Sherwin-Williams — premium paints with excellent coverage and durability. You can also supply your own paint.'),
            ('How long does interior painting take?', 'A single room takes 1 day. A full home interior typically takes 3–7 business days depending on square footage and complexity.'),
            ('Do you move furniture?', 'We move light furniture and protect everything with drop cloths. We recommend you remove fragile or valuable items before we start.'),
        ],
    },
    'demolition-services': {
        'title': 'Demolition Services Toronto & GTA | Licensed & Insured',
        'desc': 'Licensed demolition services in Toronto & GTA. Interior demo, deck removal, structure demo & debris removal. Free quotes. Call (647) 967-8555.',
        'h1': 'Demolition Services in Toronto & GTA',
        'hero_p': 'aMaximum Construction provides safe, licensed demolition services across Toronto and the GTA. Interior strip-outs, deck removal, shed demolition, and full structure removal — permit-managed and fully insured.',
        'book': '/book-demolition.html',
        'schema_service': 'Demolition Services',
        'price_range': '$1,500 – $30,000',
        'icon': '🏚️',
        'process': [
            ('Site Assessment', 'We assess the structure, identify utilities, asbestos/hazmat concerns.'),
            ('Permit if Required', 'We pull demolition permits and notify utilities as required.'),
            ('Safe Demolition', 'Systematic, safe demo with dust control and neighbour protection.'),
            ('Debris Removal', 'Full site cleanup — debris hauled away, site left broom-clean.'),
        ],
        'service_types': [
            ('🧱', 'Interior Demolition', 'Wall removal, floor strip-out, ceiling demo — full gut or selective.'),
            ('🏗️', 'Deck & Structure Removal', 'Old deck, pergola, fence, shed — fully removed and hauled away.'),
            ('🏠', 'Garage Demolition', 'Detached garage removal including foundation if required.'),
            ('🏚️', 'Shed Removal', 'Any size shed — dismantled and removed, site graded.'),
            ('🪨', 'Concrete Breaking', 'Driveway, sidewalk, patio slab breaking and removal.'),
            ('⚠️', 'Selective Demo', 'Targeted removal while protecting surrounding finishes.'),
        ],
        'faq': [
            ('How much does demolition cost in Toronto?', 'Interior room demo starts around $1,500–$4,000. Deck removal runs $1,000–$3,000. Full garage demolition ranges $5,000–$15,000 including disposal. Free quotes provided.'),
            ('Do you test for asbestos before demolition?', 'We recommend asbestos testing (through a certified lab) for homes built before 1990. We can arrange testing and, if positive, coordinate licensed asbestos abatement before demo.'),
            ('Do you need a permit for demolition?', 'Full structure demolition requires a demolition permit. Interior strip-outs typically do not. We confirm permit requirements for your specific project.'),
            ('Do you remove and haul away debris?', 'Yes — we handle full debris removal and haul-away. We sort materials for recycling where possible.'),
            ('Can you remove a load-bearing wall?', 'Yes — load-bearing wall removal requires a structural engineer\'s approval and a building permit. We manage both.'),
        ],
    },
    'excavation-services': {
        'title': 'Excavation Services Toronto & GTA | Licensed Contractors',
        'desc': 'Licensed excavation services in Toronto & GTA. Foundation dig, grading, trenching & pool excavation. Free quotes. Call (647) 967-8555.',
        'h1': 'Excavation Services in Toronto & GTA',
        'hero_p': 'aMaximum Construction provides licensed excavation services across Toronto and the GTA. Foundation excavation, grading, trenching, and pool digs — precise, safe, and fully insured.',
        'book': '/book-excavation.html',
        'schema_service': 'Excavation Services',
        'price_range': '$3,000 – $50,000',
        'icon': '⛏️',
        'process': [
            ('Site Assessment', 'We assess site access, soil conditions, underground utility locations (Ontario One Call).'),
            ('Plan & Quote', 'Excavation plan and fixed quote — depth, volume, disposal.'),
            ('Utility Locates', 'We request Ontario One Call locates before any digging begins.'),
            ('Excavation & Grading', 'Precise excavation with proper shoring, drainage, and final grading.'),
        ],
        'service_types': [
            ('🏗️', 'Foundation Excavation', 'New home, addition, or garage foundation dig to engineer specs.'),
            ('📐', 'Grading & Leveling', 'Yard grading for proper drainage away from foundations.'),
            ('🔧', 'Trenching', 'Utility, weeping tile, irrigation, and drainage trenching.'),
            ('🏊', 'Pool Excavation', 'Inground pool digs — precise depth and shape per pool specs.'),
            ('🏠', 'Basement Lowering', 'Underpinning and bench-footing to increase basement ceiling height.'),
            ('💧', 'Drainage Solutions', 'French drains, catch basins, swales — proper site drainage.'),
        ],
        'faq': [
            ('How much does excavation cost in Toronto?', 'Small excavation projects start around $3,000–$8,000. Foundation digs for additions run $15,000–$35,000. Pool excavation ranges $5,000–$15,000. Free quotes available.'),
            ('Do you call Ontario One Call before digging?', 'Always — we request utility locates through Ontario One Call (1-800-400-2255) before any excavation. This is required by law and protects against hitting gas, hydro, or water lines.'),
            ('How long does excavation take?', 'A standard foundation dig takes 1–3 days. Pool excavation takes 1–2 days. Timeline depends on site access and soil conditions.'),
            ('What happens to the excavated soil?', 'Clean fill can be repurposed on-site for grading or hauled away. Contaminated soil requires special disposal. We assess and advise.'),
            ('Do you do underpinning?', 'Yes — we provide basement lowering through underpinning and bench-footing. This requires a structural engineer\'s drawings, which we arrange.'),
        ],
    },
    'home-renovation': {
        'title': 'Home Renovation Toronto & GTA | Licensed Contractors',
        'desc': 'Licensed home renovation contractors in Toronto & GTA. Kitchen, full-home, additions. Fixed quotes, permit-managed, 5-star rated. Call (647) 967-8555.',
        'h1': 'Home Renovation in Toronto & GTA',
        'hero_p': 'aMaximum Construction delivers full-scale home renovations across Toronto and the GTA. Kitchen remodels, open-concept conversions, full-home renovations — one contractor, one contract.',
        'book': '/book-renovation.html',
        'schema_service': 'Home Renovation',
        'price_range': '$20,000 – $250,000',
        'icon': '🏠',
        'process': [
            ('Consultation & Vision', 'We meet, review your ideas, lifestyle needs, and realistic budget.'),
            ('Design & Permits', 'Floor plans, permit applications, and detailed fixed quote.'),
            ('Construction', 'All trades managed under one contract — no coordination headaches.'),
            ('Finishing & Handover', 'Final finishes, cleaning, and a complete walk-through with you.'),
        ],
        'service_types': [
            ('🍳', 'Kitchen Renovation', 'Full kitchen gut and rebuild — layout changes, cabinets, countertops, appliances.'),
            ('🏠', 'Full Home Renovation', 'Multi-room or whole-home transformation — all trades, one contractor.'),
            ('🏗️', 'Open Concept Conversion', 'Load-bearing wall removal, beam installation, new layout.'),
            ('➕', 'Home Additions', 'Rear, side, or second-floor additions to expand your living space.'),
            ('🪟', 'Window & Door Replacement', 'Energy-efficient window and door replacement — permit-managed.'),
            ('🎨', 'Interior Finishing', 'Paint, trim, flooring, lighting — renovation finishing package.'),
        ],
        'faq': [
            ('How much does a home renovation cost in Toronto?', 'Kitchen renovations run $25,000–$80,000. Full home renovations are $80,000–$250,000+. We provide detailed fixed quotes so you know exactly what you are spending.'),
            ('How do I plan a home renovation?', 'Start with a clear scope and realistic budget. Get 2–3 quotes from licensed contractors. Ensure permits are pulled. We guide you through the full planning process.'),
            ('How long does a home renovation take?', 'A kitchen takes 4–8 weeks. A full home renovation takes 3–8 months depending on scope and permit timelines.'),
            ('Do I need to move out during renovation?', 'For major full-home renovations, we recommend it for safety and to speed up the timeline. For smaller room-by-room projects, you can often stay.'),
            ('What permits are needed for a home renovation?', 'Structural, plumbing, and electrical work all require permits. We manage all permit applications and inspections as part of our service.'),
        ],
    },
    'christmas-lights-installation-toronto-gta': {
        'title': 'Christmas Lights Installation Toronto & GTA | aMaximum',
        'desc': 'Professional Christmas lights installation in Toronto & GTA. Rooflines, trees, commercial displays. Takedown included. Free quotes. Call (647) 967-8555.',
        'h1': 'Christmas Lights Installation in Toronto & GTA',
        'hero_p': 'aMaximum Construction installs professional Christmas and holiday lighting across Toronto and the GTA. Rooflines, trees, pathways, and commercial displays — installed safely and removed after the season.',
        'book': '/book-christmas.html',
        'schema_service': 'Christmas Lights Installation',
        'price_range': '$500 – $8,000',
        'icon': '🎄',
        'process': [
            ('Free Estimate Visit', 'We visit, measure your roofline and trees, and discuss your lighting style.'),
            ('Design & Quote', 'Lighting plan and fixed price — installation, materials, and takedown.'),
            ('Professional Installation', 'Our crew installs safely with proper ladders and equipment.'),
            ('Season-End Takedown', 'We remove, bundle, and store your lights after the season.'),
        ],
        'service_types': [
            ('🏠', 'Roofline & Eave Lighting', 'Classic C9 or LED lights along rooflines, peaks, and eaves.'),
            ('🌲', 'Tree & Shrub Wrapping', 'Warm white or multicolour wrap for trees and shrubs.'),
            ('🛤️', 'Pathway & Garden Lighting', 'Ground-level lights for driveways, paths, and garden features.'),
            ('🏢', 'Commercial Displays', 'Full commercial holiday displays for businesses, plazas, and offices.'),
            ('📦', 'Install & Takedown Package', 'Supply, install, and end-of-season takedown in one package.'),
            ('🎨', 'Custom Displays', 'Themed displays, animated lighting, and custom colour schemes.'),
        ],
        'faq': [
            ('How much does Christmas light installation cost in Toronto?', 'Residential roofline installation starts around $500–$1,500. Full property displays with trees run $1,500–$4,000. Commercial displays start at $3,000+. Free quotes available.'),
            ('Do you supply the lights or do I?', 'We offer a full-supply package (commercial-grade LED lights included) or a labour-only option where you supply your own lights.'),
            ('When should I book Christmas light installation?', 'Book in September or October — our calendar fills up quickly. We install from late October through December.'),
            ('Do you take down the lights after Christmas?', 'Yes — takedown is included in our install-and-takedown packages. We remove, bundle, and can store lights for next season.'),
            ('Are your installers insured?', 'Yes — all installers are fully insured and use proper safety equipment. We are covered by $2M liability insurance and WSIB.'),
        ],
    },
}

# ─── Build schema JSON ────────────────────────────────────────────────────────
def build_schema(slug, info):
    url = f"{DOMAIN}/{slug}/"
    return f'''{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "LocalBusiness",
      "name": "aMaximum Construction",
      "url": "{url}",
      "telephone": "+16479678555",
      "email": "{EMAIL}",
      "address": {{
        "@type": "PostalAddress",
        "addressLocality": "Toronto",
        "addressRegion": "ON",
        "addressCountry": "CA"
      }},
      "areaServed": {{"@type": "City", "name": "Toronto"}},
      "priceRange": "{info['price_range']}"
    }},
    {{
      "@type": "Service",
      "name": "{info['schema_service']} in Toronto & GTA",
      "provider": {{"@type": "LocalBusiness", "name": "aMaximum Construction"}},
      "areaServed": "Toronto, GTA",
      "description": "{info['desc']}"
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{DOMAIN}/"}},
        {{"@type": "ListItem", "position": 2, "name": "Services", "item": "{DOMAIN}/#services"}},
        {{"@type": "ListItem", "position": 3, "name": "{info['schema_service']}", "item": "{url}"}}
      ]
    }}
  ]
}}'''


def build_faq_schema(faq):
    items = []
    for q, a in faq:
        items.append(f'''    {{
      "@type": "Question",
      "name": "{q}",
      "acceptedAnswer": {{"@type": "Answer", "text": "{a.replace('"', "'")}"}}
    }}''')
    return '{\n  "@context": "https://schema.org",\n  "@type": "FAQPage",\n  "mainEntity": [\n' + ',\n'.join(items) + '\n  ]\n}'


def build_process_section(process):
    steps = ''
    for i, (title, desc) in enumerate(process, 1):
        steps += f'''    <div class="card">
      <div class="icon">0{i}</div>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>\n'''
    return f'''<section class="island reveal" id="how-it-works" aria-label="How it works">
  <span class="shine" aria-hidden="true"></span>
  <div class="section-head">
    <h2>How It Works</h2>
    <p>Our simple 4-step process — from first call to finished project.</p>
  </div>
  <div class="cards">
{steps}  </div>
</section>'''


def build_services_section(service_types, label):
    cards = ''
    for icon, title, desc in service_types:
        cards += f'''    <div class="card">
      <div class="icon">{icon}</div>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>\n'''
    return f'''<section class="island reveal" id="service-types" aria-label="Service types">
  <span class="shine" aria-hidden="true"></span>
  <div class="section-head">
    <h2>{label} Services We Offer</h2>
    <p>Professional services tailored to your needs and budget.</p>
  </div>
  <div class="cards">
{cards}  </div>
</section>'''


def build_faq_section(faq):
    items = ''
    for q, a in faq:
        items += f'''  <details class="faq-item">
    <summary><h3>{q}</h3></summary>
    <p>{a}</p>
  </details>\n'''
    return f'''<section class="island reveal" id="faq" aria-label="Frequently asked questions">
  <span class="shine" aria-hidden="true"></span>
  <div class="section-head">
    <h2>Frequently Asked Questions</h2>
  </div>
{items}</section>'''


def build_cta_mid(h1, book_url):
    return f'''<section class="island reveal" style="text-align:center;background:linear-gradient(135deg,#ff6b00 0%,#ff8c00 100%);color:#fff;" aria-label="Call to action">
  <span class="shine" aria-hidden="true"></span>
  <h2 style="color:#fff;margin-bottom:.5rem;">Ready to Get Started?</h2>
  <p style="color:rgba(255,255,255,.9);margin-bottom:1.5rem;">Get a free consultation and fixed quote — no obligation.</p>
  <a href="{book_url}" class="btn" style="background:#fff;color:#ff6b00;font-weight:700;">Book Free Consultation →</a>
</section>'''


# ─── Process each service page ────────────────────────────────────────────────
import re

updated = []

for slug, info in SERVICES.items():
    idx = root / slug / 'index.html'
    if not idx.exists():
        print(f'  SKIP (not found): {slug}')
        continue

    html = idx.read_text(encoding='utf-8', errors='ignore')

    # 1. Fix title
    html = re.sub(r'<title>[^<]+</title>',
                  f'<title>{info["title"]}</title>', html)

    # 2. Fix meta description
    html = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{info["desc"]}">', html)

    # 3. Fix OG tags
    html = re.sub(r'<meta property="og:title" content="[^"]*">',
                  f'<meta property="og:title" content="{info["title"]}">', html)
    html = re.sub(r'<meta property="og:description" content="[^"]*">',
                  f'<meta property="og:description" content="{info["desc"]}">', html)

    # 4. Fix schema
    old_schema = re.search(r'<script type="application/ld\+json">.*?</script>', html, re.DOTALL)
    new_schema = f'<script type="application/ld+json">\n{build_schema(slug, info)}\n</script>\n<script type="application/ld+json">\n{build_faq_schema(info["faq"])}\n</script>'
    if old_schema:
        html = html[:old_schema.start()] + new_schema + html[old_schema.end():]
    else:
        html = html.replace('</head>', new_schema + '\n</head>', 1)

    # 5. Remove old div.container block (depth-aware)
    def remove_container_div(text):
        """Remove <div class="container"> ... </div> (top-level, depth-tracked)."""
        result = []
        i = 0
        while i < len(text):
            # Look for the opening tag
            m = re.search(r'<div\s+class="container">', text[i:])
            if not m:
                result.append(text[i:])
                break
            result.append(text[i:i + m.start()])
            i += m.start() + len(m.group())
            # Track depth to find matching close
            depth = 1
            j = i
            while j < len(text) and depth > 0:
                open_m = re.search(r'<div\b', text[j:])
                close_m = re.search(r'</div>', text[j:])
                if not close_m:
                    break
                if open_m and open_m.start() < close_m.start():
                    depth += 1
                    j += open_m.start() + 4
                else:
                    depth -= 1
                    j += close_m.start() + 6
            i = j  # skip the entire container block
        return ''.join(result)

    html = remove_container_div(html)
    # Also remove standalone old cta divs that may remain
    html = re.sub(r'<div class="cta">.*?</div>', '', html, flags=re.DOTALL)

    # 6. Fix H1 and hero paragraph (page-hero or blog-hero)
    html = re.sub(r'(<div class="page-hero"[^>]*>.*?<h1>)[^<]+(</h1>)',
                  r'\g<1>' + info['h1'] + r'\2', html, flags=re.DOTALL)
    html = re.sub(r'(<section class="page-hero"[^>]*>.*?<h1>)[^<]+(</h1>)',
                  r'\g<1>' + info['h1'] + r'\2', html, flags=re.DOTALL)
    # If hero has a paragraph after h1
    html = re.sub(
        r'(<div class="page-hero"[^>]*>.*?<h1>[^<]+</h1>\s*)<p>[^<]*</p>',
        r'\g<1><p>' + info['hero_p'] + '</p>',
        html, flags=re.DOTALL
    )

    # 7. Inject process + service types + mid-CTA after reviews section (or before FAQ)
    new_sections = (
        '\n' + build_process_section(info['process']) +
        '\n' + build_services_section(info['service_types'], info['schema_service']) +
        '\n' + build_cta_mid(info['h1'], info['book']) +
        '\n'
    )

    # Insert before existing FAQ section or before locations section
    if 'id="faq"' in html:
        html = html.replace('<section class="island reveal" id="faq"', new_sections + '<section class="island reveal" id="faq"', 1)
    elif 'id="locations"' in html:
        html = html.replace('<section class="island reveal service-locations" id="locations"', new_sections + '<section class="island reveal service-locations" id="locations"', 1)
    else:
        # Before footer
        html = html.replace('<footer class="site-footer">', new_sections + '<footer class="site-footer">', 1)

    # 8. Replace old FAQ section with new rich one (if it's a bare one)
    # Remove existing plain FAQ and inject new
    old_faq = re.search(r'<section class="island reveal" id="faq".*?</section>', html, re.DOTALL)
    if old_faq:
        html = html[:old_faq.start()] + build_faq_section(info['faq']) + html[old_faq.end():]

    idx.write_text(html, encoding='utf-8')
    updated.append(slug)
    print(f'  UPDATED: {slug}')

print(f'\nTotal updated: {len(updated)}/{len(SERVICES)}')
