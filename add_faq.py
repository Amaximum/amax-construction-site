import os, re

ROOT = r'c:\Users\maxim\Desktop\amax-Construction-site'
SKIP = {'index-seo-2026.html','service-template.html','update_all_pages.py','add_faq.py','find_broken_links.py'}
SKIP_DIRS = {'.venv','.git','img','css','node_modules'}

RE_FAQ_SECTION = re.compile(
    r'<section[^>]*id="faq"[^>]*>[\s\S]*?</section>',
    re.DOTALL
)

LOCATIONS = {
    'toronto': 'Toronto', 'north-york': 'North York', 'east-york': 'East York',
    'scarborough': 'Scarborough', 'etobicoke': 'Etobicoke', 'markham': 'Markham',
    'richmond-hill': 'Richmond Hill', 'vaughan': 'Vaughan', 'woodbridge': 'Woodbridge',
    'aurora': 'Aurora', 'newmarket': 'Newmarket', 'thornhill': 'Thornhill',
    'king-city': 'King City', 'kleinburg': 'Kleinburg', 'concord': 'Concord',
    'hamilton': 'Hamilton', 'burlington': 'Burlington', 'brampton': 'Brampton',
    'mississauga': 'Mississauga', 'schomberg': 'Schomberg', 'bradford': 'Bradford',
    'east-gwillimbury': 'East Gwillimbury', 'bayview-glen': 'Bayview Glen',
    'glenville': 'Glenville', 'maple': 'Maple', 'forest-hill': 'Forest Hill',
    'whitchurch': 'Whitchurch-Stouffville', 'gta': 'the GTA', 'oakville': 'Oakville',
}

def detect_service(path):
    p = path.lower()
    if any(x in p for x in ['deck-builder','deck-contractor','deck-railing','deck-maintenance','deck-boards','decking-material','building-a-deck','best-deck','custom-deck','amazing-deck','expert-deck']): return 'deck'
    if any(x in p for x in ['fence-contractor','fence-install','fence-option','finding-best-fence']): return 'fence'
    if any(x in p for x in ['bathroom-renovation','bathroom-reno']): return 'bathroom'
    if any(x in p for x in ['basement-renovation','basement-bathroom','best-basement','basement-costs','low-ceiling','remodel-your-basement']): return 'basement'
    if any(x in p for x in ['handyman']): return 'handyman'
    if any(x in p for x in ['general-contractor','renovation-service','home-renovation','trusted-small-contractor','renovation-permit','legal-consideration','first-steps-renovation']): return 'general'
    if any(x in p for x in ['carpenter','carpentry']): return 'carpentry'
    if any(x in p for x in ['interlocking','paving','paver','benefits-of-interlocking']): return 'interlocking'
    if any(x in p for x in ['landscaping','your-guide-to-choose-landscaping']): return 'landscaping'
    if any(x in p for x in ['canopy','awning']): return 'canopy'
    if any(x in p for x in ['demolition']): return 'demolition'
    if any(x in p for x in ['christmas-light']): return 'christmas'
    if any(x in p for x in ['plumbing','handyman-plumbing']): return 'plumbing'
    if any(x in p for x in ['blog/','find-perfect-deck','choosing-right','choosing-perfect','reasons-to-hire','effective-communication','understanding-cost','exploring-the-benefits','construction-project-in-the-winter','expensive-parts','installation-timelines','avoid','trusted','expert-tips','benefits-of','ultimate-guide','your-guide']): return 'blog'
    if '/locations/' in p: return 'location'
    if 'portfolio' in p: return 'portfolio'
    return 'general'

def detect_location(path):
    p = path.lower()
    for slug, name in LOCATIONS.items():
        if slug in p:
            return name
    return 'Toronto & GTA'

FAQS = {
'deck': [
  ("How much does it cost to build a deck in {loc}?", "Deck building costs in {loc} typically range from $8,000 to $35,000+, depending on size, materials, and design complexity. Pressure-treated wood is the most affordable option, while composite decking costs more upfront but requires less maintenance. We provide detailed written quotes so you know exactly what you're paying for."),
  ("Do I need a building permit for a deck in {loc}?", "In most municipalities including {loc}, a building permit is required for decks higher than 24 inches (60 cm) from the ground, or attached to the house. Our team handles the permit process and ensures your deck is code-compliant from start to finish."),
  ("What is the best decking material for {loc}'s climate?", "For {loc}'s freeze-thaw climate, composite decking (Trex, TimberTech) performs best — it won't warp, crack, or splinter. Pressure-treated cedar is a great natural wood option with good rot resistance. We'll recommend the right material based on your budget, usage, and aesthetic goals."),
  ("How long does it take to build a deck?", "A standard deck in {loc} takes 1–2 weeks from permit approval to final inspection. Larger, multi-level decks or those with custom railings and stairs may take 2–4 weeks. We provide a clear timeline before work begins."),
  ("What is the difference between composite and pressure-treated wood decking?", "Composite decking is made from wood fibres and recycled plastic — it's low-maintenance, doesn't splinter, and carries long warranties (25+ years). Pressure-treated wood costs less upfront but requires sealing, staining, and regular maintenance. Both are strong choices depending on your priorities."),
  ("How long does a deck last?", "A well-built deck in {loc} can last 15–30+ years depending on materials and maintenance. Composite decks with proper installation typically last 25–30 years. Pressure-treated wood lasts 15–20 years with regular maintenance. Our workmanship warranty covers the structural build."),
  ("Can you build a deck attached to the house?", "Yes. Attached decks are ledger-mounted to the house structure using flashing and hardware designed for {loc}'s climate conditions. Proper ledger attachment is critical — it must meet Ontario Building Code requirements to ensure safety and prevent moisture infiltration."),
  ("What railing options are available for my deck?", "We offer aluminum, glass, composite, cable, and wood railing systems. Glass and cable railings maximize views, aluminum is low-maintenance, and wood matches traditional deck aesthetics. All railings are installed to OBC height and load requirements."),
  ("Do you handle deck repairs and replacements?", "Yes. We assess existing decks in {loc} for structural integrity, rotted boards, loose connections, and safety issues. We can repair specific sections or do a full replacement — whichever makes more financial sense for your situation."),
  ("How do I maintain my new deck?", "Composite decks need only occasional cleaning with soap and water. Wood decks should be cleaned, inspected, and re-sealed or stained every 2–3 years. Keep leaves and debris off the surface, ensure drainage isn't blocked, and check fasteners annually."),
],
'fence': [
  ("How much does fence installation cost in {loc}?", "Fence installation in {loc} ranges from $30 to $100+ per linear foot depending on material and style. Wood (cedar) runs $35–$55/ft, vinyl $45–$75/ft, and aluminum $50–$100/ft. We provide detailed written quotes including materials, labour, and post installation."),
  ("Do I need a permit to install a fence in {loc}?", "In {loc} and most GTA municipalities, fences over 2 metres (6.5 ft) require a building permit. Corner lot fences have additional sightline restrictions. We handle permit applications and ensure your fence meets all local bylaws."),
  ("What fence height is allowed in {loc}?", "Standard residential fences in {loc} can be up to 2 metres (6.5 ft) in side and rear yards without a permit. Front yard fences are typically limited to 1 metre. Corner lots have additional restrictions. We'll advise on the maximum allowable height for your property."),
  ("What type of fence gives the most privacy?", "Solid board-on-board cedar or vinyl privacy fences with no gaps provide maximum privacy. A standard 6-foot privacy fence is the most common choice in {loc}. We can add lattice toppers or increase height (with permit) for additional screening."),
  ("Wood vs vinyl fence — which is better for {loc}?", "Cedar is the most popular wood choice in {loc} — naturally rot-resistant and holds stain well. Vinyl (PVC) requires no painting or staining and lasts longer, but costs 30–50% more upfront. We recommend cedar for budget-conscious clients and vinyl for those wanting minimal maintenance."),
  ("How long does fence installation take?", "A standard residential fence in {loc} typically takes 1–3 days to install. Longer runs, custom gates, or complex terrain may take 4–5 days. We provide a complete timeline before starting and minimize disruption to your property."),
  ("Who owns a boundary fence between neighbours?", "In Ontario, boundary fences are generally considered the shared responsibility of both property owners under the Line Fences Act. We can help you document the project properly if cost-sharing with a neighbour is involved."),
  ("Can you install gates and custom fence sections?", "Yes. We install single and double swing gates, sliding gates, and arched gate tops. Custom fence sections for uneven terrain, slopes, and corners are all part of our standard installation service in {loc}."),
  ("How long will my fence last?", "A well-installed cedar fence in {loc} lasts 15–20 years with regular maintenance (staining every 2–3 years). Vinyl fences last 25–40 years with minimal upkeep. Aluminum fences can last 50+ years. All our fences come with a workmanship warranty."),
  ("What is the best fence for a pool enclosure in {loc}?", "Ontario Building Code requires pool enclosures to be at least 1.2 metres (4 feet) high with self-closing, self-latching gates. Aluminum picket fencing is the most common pool fence choice in {loc} — it's durable, low-maintenance, and meets code requirements."),
],
'bathroom': [
  ("How much does a bathroom renovation cost in {loc}?", "Bathroom renovations in {loc} range from $8,000–$15,000 for a cosmetic refresh to $20,000–$45,000 for a full gut-and-rebuild. High-end projects with custom tile, steam showers, and heated floors can exceed $60,000. We provide detailed written quotes broken down by scope."),
  ("How long does a bathroom renovation take in {loc}?", "A cosmetic bathroom update in {loc} takes 1–2 weeks. A full renovation with plumbing and tile work takes 3–5 weeks. Projects involving moving walls or relocating plumbing can take 6–8 weeks. We provide a clear timeline before work begins."),
  ("Do I need a permit for my bathroom renovation in {loc}?", "In {loc}, permits are required when you're moving plumbing, adding electrical circuits, or removing walls. Replacing fixtures in the same location, new tile, or a vanity swap typically don't require permits. We pull all required permits and coordinate inspections."),
  ("Can you move the toilet or shower to a different location?", "Yes, but relocating plumbing is the biggest cost driver in bathroom renovations. Moving a toilet or shower requires breaking the concrete floor (in basements) or rerouting drain lines — adding $3,000–$10,000 to the project. We advise on cost-effective alternatives where possible."),
  ("What tile is best for bathroom floors and shower walls?", "Porcelain tile is the most durable and water-resistant choice for both floors and shower walls in {loc} homes. Large-format tiles (24×24\") make small bathrooms look bigger. Natural stone is beautiful but requires sealing and more maintenance."),
  ("Do you handle electrical and plumbing in bathroom renovations?", "Yes. We coordinate all trades including licensed electricians and plumbers as part of our full-service renovation approach in {loc}. You deal with one contractor — we handle the entire scope and scheduling."),
  ("What is the best ventilation solution for a bathroom?", "Ontario Building Code requires mechanical ventilation in all bathrooms without operable windows. We install Energy Star–rated exhaust fans sized to the room's CFM requirements. Proper ventilation prevents mould, protects drywall, and extends the life of your finishes."),
  ("Can you add a bathroom to my basement?", "Yes. Basement bathroom additions in {loc} typically require breaking the concrete floor to tie into the drain system (or installing a sewage ejector pump). Costs range from $8,000–$20,000 depending on complexity. We handle permits, rough-in plumbing, and all finishes."),
  ("What's included in a full bathroom renovation?", "Our full bathroom renovations in {loc} include: demolition, waterproofing, plumbing rough-in, electrical, tile installation, vanity and fixture installation, glass shower enclosures, accessories, painting, and final inspection. We handle everything from start to finish."),
  ("How do I choose between a walk-in shower and a bathtub?", "If you have only one bathroom, keep the tub — it helps with resale value and is needed for bathing children. If you have a second bathroom, converting the tub to a walk-in shower is a popular upgrade in {loc} that adds usable space and a modern look."),
],
'basement': [
  ("How much does a basement renovation cost in {loc}?", "Basement renovations in {loc} range from $30,000–$55,000 for a standard finish to $60,000–$100,000+ for a legal apartment with separate entrance. Key cost drivers include: bathroom addition, ceiling height, waterproofing requirements, and egress windows."),
  ("Do I need a permit to finish my basement in {loc}?", "Yes. In {loc} and across the GTA, finishing a basement requires a building permit. The permit process covers framing, electrical, plumbing, and insulation — all subject to inspection. We manage the permit process and schedule all required inspections."),
  ("What ceiling height is needed for a finished basement in {loc}?", "Ontario Building Code requires a minimum ceiling height of 1.95 metres (6'5\") for habitable basement space in {loc}. If your existing ceiling is lower, options include lowering the floor (underpinning) or creative design around beams and ductwork."),
  ("Do I need egress windows for a bedroom in the basement?", "Yes. Ontario Building Code requires egress windows for any basement bedroom — minimum 0.35 m² openable area and no dimension smaller than 380mm. Egress windows are required for legal occupancy and for insurance coverage. We handle the installation as part of our basement renovation service."),
  ("Can I legally rent out my finished basement in {loc}?", "To legally rent a basement apartment in {loc}, it must meet Ontario Building Code requirements: separate entrance, proper ceiling height, egress windows, interconnected smoke and CO detectors, and a second means of egress. We build legal secondary suites that meet all requirements."),
  ("How do I deal with moisture in my basement before renovating?", "Moisture must be addressed before any finishing work begins. We assess the source — whether exterior drainage, foundation cracks, or condensation — and recommend waterproofing solutions. Finishing over a wet basement leads to mould and material failure."),
  ("What insulation should I use in my basement in {loc}?", "In {loc}'s climate, basement walls should have a minimum of R-20 insulation. We typically use rigid foam board (XPS) against the foundation wall, then batt insulation in the stud wall. This approach prevents thermal bridging and moisture accumulation."),
  ("How long does a basement renovation take?", "A standard basement finish in {loc} takes 6–10 weeks from permit approval to final inspection. A legal basement apartment with plumbing, separate entrance, and multiple rooms takes 10–16 weeks. We provide a detailed schedule at the start of every project."),
  ("What's the best use for a finished basement in {loc}?", "The most popular uses in {loc} are: legal rental apartment (best ROI), family recreation room, home office, home gym, and guest suite. The right choice depends on your family's needs, budget, and long-term plans for the property."),
  ("How much value does a finished basement add to my home in {loc}?", "A well-finished basement in {loc} typically adds 70–80% of renovation cost in home value, with legal apartments often returning more. In the current {loc} market, a legal secondary suite can add $80,000–$150,000 to your home's appraised value."),
],
'handyman': [
  ("What handyman services do you offer in {loc}?", "We offer a full range of handyman services in {loc} including: drywall repair, painting, furniture assembly, door/window adjustments, caulking, minor plumbing fixes, light fixture installation, shelving, flooring repairs, weatherstripping, and general home maintenance."),
  ("How do you charge for handyman work in {loc}?", "We charge by the job (flat rate for clearly defined tasks) or by the hour for open-ended maintenance lists. We provide a written estimate before starting any work. There are no surprise charges — you approve the scope and price in advance."),
  ("Can you do multiple small jobs in one visit?", "Yes — that's actually our most efficient service in {loc}. A handyman day-rate visit lets us tackle your entire to-do list: hang pictures, patch walls, fix squeaky doors, caulk windows, replace hardware, and more. One visit, many tasks."),
  ("Do you do drywall repair in {loc}?", "Yes. We repair drywall holes of all sizes — from small nail holes to large damage from plumbing or electrical work. Repairs are properly taped, mudded, sanded, and primed so they're ready for painting. We match existing textures where required."),
  ("Can a handyman do plumbing and electrical work?", "Our handyman team handles minor plumbing (faucet replacement, shut-off valve, toilet parts) and minor electrical (light fixture, switch, outlet replacement) that don't require permits in {loc}. For full plumbing or electrical installations, we bring in licensed tradespeople."),
  ("Do you assemble furniture in {loc}?", "Yes. We assemble all types of furniture — IKEA, flat-pack, office furniture, gym equipment, and more. We have experience with complex multi-piece assemblies and follow manufacturer instructions to ensure proper, safe completion."),
  ("Can you help with TV wall mounting in {loc}?", "Yes. We mount flat-screen TVs of all sizes on drywall, concrete, and brick walls in {loc} homes. We locate studs, use proper mounting hardware, and can conceal cables through the wall for a clean finish."),
  ("How quickly can you respond to handyman requests in {loc}?", "We typically book handyman visits in {loc} within 3–7 business days. For urgent situations (water leak, broken lock), contact us directly and we'll do our best to accommodate a faster timeline."),
  ("Do you do exterior handyman work?", "Yes. Our handyman services in {loc} include: deck board replacement, fence repairs, caulking around windows and doors, gutter cleaning, weatherstripping, exterior painting touch-ups, and minor concrete crack repairs."),
  ("Are your handymen licensed and insured in {loc}?", "Yes. Our team is fully insured with liability coverage and WSIB clearance. All work in {loc} is done to a professional standard. We stand behind our work — if something isn't right, we come back and fix it."),
],
'general': [
  ("What does a general contractor do in {loc}?", "A general contractor in {loc} manages the full scope of a construction or renovation project: coordinating trades (framing, electrical, plumbing, HVAC, finishing), obtaining permits, scheduling inspections, and ensuring the project is delivered on time, on budget, and to code."),
  ("How much does a general contractor charge in {loc}?", "General contractors in {loc} typically charge 15–25% of total project cost as a management fee, or provide a fixed-price contract. For full renovations, our all-in pricing includes labour, materials, permits, and coordination — no hidden fees."),
  ("Do I need a permit for my renovation in {loc}?", "In {loc}, permits are required for: structural changes, additions, basement apartments, new plumbing or electrical circuits, HVAC modifications, and most significant alterations. We manage the entire permit process and coordinate all required inspections."),
  ("How do I find a reliable contractor in {loc}?", "Verify: WSIB clearance certificate, liability insurance ($2M minimum), references from similar projects, written contract with detailed scope, and a payment schedule tied to milestones. Avoid contractors who ask for large upfront cash payments or won't provide written quotes."),
  ("How long does a typical home renovation take in {loc}?", "Kitchen renovations: 4–8 weeks. Bathroom: 3–6 weeks. Basement: 8–16 weeks. Full home renovation: 3–6 months. Timelines depend on scope, permit approvals, and material lead times. We provide a detailed schedule before work begins."),
  ("What should be included in a renovation contract in {loc}?", "A proper renovation contract in {loc} must include: detailed scope of work, materials specified by brand/grade, start and completion dates, payment schedule tied to milestones, change order process, warranty terms, and dispute resolution. Never sign a vague contract."),
  ("Can you manage multi-trade projects in {loc}?", "Yes. We coordinate all trades under one contract — framing, electrical, plumbing, HVAC, tile, flooring, painting, and exterior work. You deal with one point of contact for the entire project. This reduces scheduling conflicts and ensures consistent quality control."),
  ("How does the payment schedule work for renovations in {loc}?", "We use milestone-based payment schedules: typically 10–15% deposit, progress payments at defined milestones (rough-in complete, drywall complete, etc.), and a final payment after your sign-off. We never ask for large upfront payments before work begins."),
  ("Do you handle permits and inspections in {loc}?", "Yes. We manage the full permit process for your project in {loc}: application, drawings (where required), permit fees, booking inspections, and obtaining the final occupancy certificate. You don't need to deal with the city directly."),
  ("What warranty do you provide on renovation work in {loc}?", "We provide a written workmanship warranty on all our renovation work in {loc}. Structural work carries a longer warranty period. Material warranties from manufacturers are passed through to you. All warranty terms are specified in your contract before work begins."),
],
'carpentry': [
  ("What carpentry services do you offer in {loc}?", "We provide full carpentry services in {loc} including: custom trim and molding, framing, built-in shelving and cabinetry, stair construction and repair, door installation, window casing, wainscoting, coffered ceilings, and interior/exterior wood finishing."),
  ("How much does custom carpentry cost in {loc}?", "Custom carpentry in {loc} varies widely by project: basic trim installation starts at $500–$2,000; built-in shelving units run $1,500–$5,000+; full custom cabinetry $5,000–$20,000+. We provide detailed written estimates for every project."),
  ("Can you match existing trim and molding in my home?", "Yes. We can source matching profiles for most standard and custom trim styles in {loc}. For older homes with unique profiles, we use a combination of stacking standard profiles or custom-milling to achieve an exact match."),
  ("Do you build custom built-in shelving and storage?", "Yes. Built-ins are one of our specialties in {loc}. We design and build custom shelving, entertainment units, home office built-ins, and closet systems that maximize space and add significant value to your home."),
  ("Can you repair or replace my staircase?", "Yes. We repair and replace staircases in {loc} including: treads and risers replacement, newel posts, balusters, handrails, and full stair redesigns. We ensure all stair work meets Ontario Building Code requirements for rise, run, and railing height."),
  ("Do you install doors and windows?", "Yes. We install interior and exterior doors, including prehung doors, pocket doors, barn doors, and bifold doors in {loc} homes. Exterior door installation includes proper flashing, weatherstripping, and hardware for Ontario's climate conditions."),
  ("What wood species do you recommend for interior trim in {loc}?", "Finger-jointed pine is the most cost-effective choice for painted trim. For stained wood, we recommend clear pine, poplar, or oak depending on the grain character you prefer. Hardwoods like maple and walnut are ideal for high-end applications."),
  ("Can you add crown molding to my existing rooms?", "Yes. Crown molding installation is one of the highest-value cosmetic upgrades in {loc} homes. We handle ceiling prep, corner mitering (including compound angles), and finishing for paint-ready results."),
  ("Do you do outdoor/exterior carpentry work?", "Yes. Our exterior carpentry in {loc} includes: fascia and soffit, pergolas, garden structures, exterior trim, wood fence construction, and custom gate builds. We use weather-resistant materials appropriate for {loc}'s climate."),
  ("How long does carpentry work take?", "Simple trim installation in one room: 1–2 days. Full-home trim package: 1–2 weeks. Custom built-ins: 3–7 days per unit. We provide a clear timeline for every carpentry project in {loc} and coordinate with other trades to avoid delays."),
],
'interlocking': [
  ("How much does interlocking stone installation cost in {loc}?", "Interlocking paver installation in {loc} ranges from $15–$35+ per square foot installed, depending on stone type, pattern complexity, and site preparation needed. A standard 400 sq ft driveway runs $8,000–$14,000. We provide detailed written quotes."),
  ("How long does interlocking installation last in {loc}?", "Properly installed interlocking pavers in {loc} last 25–50+ years. The freeze-thaw cycles in {loc} require a minimum 6–8 inch compacted granular base to prevent heaving and shifting. Our installations are built to handle Ontario's climate."),
  ("Do I need a permit for interlocking pavers in {loc}?", "Most residential interlocking projects in {loc} don't require a permit. However, projects near the road allowance, affecting drainage, or in flood-plain areas may have restrictions. We advise on any permit requirements during the quote process."),
  ("What's the difference between concrete pavers and natural stone?", "Concrete pavers (Unilock, Permacon) are manufactured to consistent sizes and colours — more affordable and highly durable. Natural stone (slate, granite, limestone) has unique character but varies in thickness and costs more. Both perform well in {loc}'s climate."),
  ("Can interlocking be installed over existing concrete?", "In most cases, no — existing concrete must be removed to allow proper base preparation. The granular base thickness needed for {loc}'s frost depth cannot be achieved over an existing slab. Removing old concrete is included in our interlocking quotes."),
  ("How do I maintain my interlocking driveway or patio?", "Annual maintenance for {loc} interlocking: re-sand joints with polymeric sand every 3–5 years, apply sealer every 2–4 years, remove weeds promptly, and avoid salt (use sand for winter traction). Avoid metal snow blower blades that can chip paver edges."),
  ("Can you do interlocking steps and retaining walls?", "Yes. We build interlocking steps, raised patios, and retaining walls in {loc} using Allan Block, Unilock Umbriano, and other certified systems. All retaining walls over 1 metre require engineering in Ontario."),
  ("What patterns are available for interlocking pavers?", "Popular patterns in {loc} include: herringbone (most stable for driveways), running bond, basketweave, 45-degree herringbone, and random/tumbled patterns. We'll recommend the right pattern based on your application and aesthetic preference."),
  ("Can you integrate drainage into my interlocking project?", "Yes. Proper drainage design is critical in {loc}. We ensure minimum 2% slope away from structures, install French drains or channel drains where needed, and use edge restraints to prevent spreading. Drainage planning is part of every quote."),
  ("How long does interlocking installation take?", "A standard driveway or patio in {loc} takes 3–7 days depending on size and complexity. This includes demolition, base preparation, paver installation, and polymeric sand application. We keep the site clean and minimize disruption throughout."),
],
'landscaping': [
  ("What landscaping services do you offer in {loc}?", "Our landscaping services in {loc} include: lawn installation (sod and seed), garden bed design and planting, tree and shrub installation, grading and drainage, interlocking patios and walkways, retaining walls, mulching, and seasonal cleanup."),
  ("How much does landscaping cost in {loc}?", "Landscaping costs in {loc} vary widely by scope. Sod installation runs $1.50–$3.00/sq ft installed. Garden design and planting starts at $2,000–$5,000. Full backyard transformations with patio, planting, and lighting run $15,000–$50,000+."),
  ("What plants grow best in {loc}'s climate?", "For {loc}'s hardiness zone (Zone 5–6), top performers include: hostas, ornamental grasses, black-eyed Susans, coneflowers, spireas, burning bush, lilacs, and hydrangeas. We select plants rated for {loc}'s winters and maintenance preferences."),
  ("When is the best time to install sod in {loc}?", "The best time to lay sod in {loc} is spring (April–June) or early fall (August–September) when temperatures are mild and rainfall is adequate for establishment. Avoid midsummer sod installation as heat stress affects root establishment."),
  ("Do you handle grading and drainage problems?", "Yes. Poor grading that directs water toward your foundation is one of the most common problems in {loc} homes. We re-grade yards to direct water away from the house, install French drains, and correct low spots that collect standing water."),
  ("Can you design and install a backyard patio with landscaping?", "Yes. We design and install complete outdoor living spaces in {loc} including: interlocking patios, planting beds, lawn areas, privacy screening, and exterior lighting. We provide design concepts and a single contract for the full scope."),
  ("Do you offer seasonal maintenance in {loc}?", "Yes. Our seasonal services in {loc} include: spring cleanup (leaf removal, bed edging, pruning), lawn fertilization programs, mulch installation, fall cleanup, and snow management. We offer package pricing for ongoing maintenance contracts."),
  ("How do I prevent weeds in my garden beds?", "The most effective weed control in {loc} gardens: install landscape fabric under 3–4 inches of mulch, apply pre-emergent herbicide in spring, edge beds regularly to prevent grass intrusion, and maintain healthy plant density that shades out weeds."),
  ("What is the cost of building a retaining wall in {loc}?", "Retaining walls in {loc} cost $25–$60+ per square foot of face area, depending on material and height. Walls over 1 metre require engineering. We use Allan Block, Unilock, natural stone, or timber depending on your design and budget."),
  ("Do you need a permit for landscaping work in {loc}?", "Most landscaping in {loc} doesn't require permits. However: retaining walls over 1 metre, works near regulated watercourses, removal of significant trees (check local bylaws), and grading that affects adjacent properties may require approvals. We advise on requirements during the quote."),
],
'canopy': [
  ("What types of canopies and awnings do you install in {loc}?", "We install retractable awnings, fixed canopies, pergola covers, polycarbonate patio roofs, fabric shade sails, and motorized awning systems in {loc}. Each solution is designed for your space, sun exposure, and budget."),
  ("How much does a canopy or awning installation cost in {loc}?", "Awning installation in {loc} ranges from $1,500–$5,000 for a standard motorized retractable awning. Fixed canopies and pergola covers with polycarbonate roofing run $3,000–$12,000. Full outdoor structure canopies start at $8,000+."),
  ("Do canopies hold up to {loc}'s winter weather?", "Retractable awnings should be retracted during heavy snow or high winds in {loc}. Fixed canopies and polycarbonate roofing systems are designed to handle Ontario's snow load requirements. We specify structures and materials rated for {loc}'s climate."),
  ("Do I need a permit for a canopy or awning in {loc}?", "Smaller awnings and retractable systems typically don't require permits in {loc}. Larger attached structures (pergolas, patio enclosures) may require a building permit if they're attached to the house or exceed certain size thresholds. We advise on permit requirements during the quote."),
  ("Can you install a motorized retractable awning?", "Yes. We install motorized retractable awnings with remote control or smartphone app control in {loc}. Options include wind sensors that automatically retract when wind exceeds safe limits — ideal for {loc}'s variable weather."),
  ("What materials are best for outdoor canopies in {loc}?", "For {loc}'s climate: polycarbonate and tempered glass panels for permanent structures, Sunbrella or similar solution-dyed acrylic fabrics for awnings and shade sails. These materials handle UV exposure, snow load, and rain without degrading."),
  ("Can you build a covered deck or pergola with a canopy roof?", "Yes. We build complete covered outdoor structures in {loc}: pergolas with retractable shade fabric, louvered roof systems, polycarbonate-covered structures, and aluminum pergolas with integrated rain management. All structures meet Ontario Building Code."),
  ("How long do awning fabrics last?", "Quality awning fabrics (Sunbrella, Dickson Orchestra) in {loc} last 8–12 years with proper maintenance. Store retractable awnings during winter months or severe weather. Clean fabric annually with mild soap and water to prevent mould and extend life."),
  ("Can you install shade over an existing patio or deck in {loc}?", "Yes. We assess your existing structure and design a shade solution that works with your space — whether a freestanding pergola, wall-mounted awning, or overhead tensioned fabric system. Most installations in {loc} can be completed in 1–3 days."),
  ("Do you do commercial canopy installations in {loc}?", "Yes. We install commercial-grade canopies and entrance awnings for storefronts, restaurants, and office buildings in {loc}. Commercial installations include proper signage integration, code-compliant anchoring, and weather-resistant materials."),
],
'demolition': [
  ("What demolition services do you offer in {loc}?", "We provide interior and exterior demolition services in {loc}: room gutting, wall removal, bathroom and kitchen demo, basement demolition, deck and fence removal, shed and garage demolition, concrete breaking, and full residential teardowns."),
  ("Do I need a permit for demolition in {loc}?", "In {loc}, permits are required for: structural wall removal, full building demolition, and projects affecting load-bearing elements. Interior soft demolition (gutting finishes, removing non-structural walls) typically doesn't require a permit. We advise on requirements for your project."),
  ("How much does demolition cost in {loc}?", "Interior room demolition in {loc} runs $1,500–$5,000 depending on size and disposal requirements. Full kitchen demo: $2,000–$4,000. Deck removal: $1,000–$3,000. Full residential demolition: $15,000–$40,000+. We provide detailed quotes including disposal fees."),
  ("How do you handle asbestos and hazardous materials?", "For homes built before 1990 in {loc}, we recommend asbestos testing before demolition begins. If hazardous materials are found, we bring in certified abatement contractors. We do not disturb suspected asbestos materials without proper testing and clearance."),
  ("How long does demolition take in {loc}?", "Interior room demo in {loc}: 1–2 days. Full kitchen or bathroom gutting: 2–3 days. Basement demolition: 3–5 days. Full house demolition: 3–7 days. Timeline includes debris removal and site cleanup. We provide a schedule at the start of every project."),
  ("Do you remove the debris and dispose of it?", "Yes. Our demolition service in {loc} includes all debris removal and disposal at approved facilities. We separate materials for recycling where possible (concrete, metal, wood). Disposal fees are included in our written quotes — no surprise charges."),
  ("Can you remove just one wall or a partial structure?", "Yes. Selective demolition is one of our specialties in {loc}. We can remove a specific wall (load-bearing or non-load-bearing), a section of deck, old bathroom finishes, or any targeted area while protecting the rest of your home."),
  ("How do you protect the rest of my home during demolition?", "We use heavy-duty plastic sheeting, dust barriers, and floor protection in {loc} homes to contain dust and debris. For exterior demolitions, we protect landscaping and neighbouring properties. Cleanup is part of every job."),
  ("Can you demolish a load-bearing wall?", "Yes, but load-bearing wall removal in {loc} requires a permit and engineering review. We coordinate with structural engineers, obtain the permit, install temporary shoring during the work, and install the required beam to carry the load safely."),
  ("Do you offer same-week demolition services in {loc}?", "For smaller jobs in {loc} (single room demo, deck removal), we can often schedule within 1–2 weeks. For larger projects, scheduling depends on permit timelines and crew availability. Contact us for current availability and fast quotes."),
],
'christmas': [
  ("How much does professional Christmas light installation cost in {loc}?", "Christmas light installation in {loc} ranges from $500–$3,000+ depending on the size of your home and complexity of the display. This includes installation, professional lighting, and removal service. We provide written quotes based on your property."),
  ("Do you supply the lights or do I provide them?", "We provide professional-grade LED commercial lights in {loc} that are brighter, more energy-efficient, and longer-lasting than retail options. Using our lights means we handle warranty replacements for any bulbs that fail during the season at no extra charge."),
  ("When do you start installing Christmas lights in {loc}?", "We begin installations in {loc} in early to mid-November. Early booking is strongly recommended — our schedule fills up quickly. Contact us in September or October to secure your preferred installation date."),
  ("Do you take the lights down after the holidays?", "Yes. Takedown and storage are included in our Christmas light packages in {loc}. We remove lights after the holiday season, store them, and bring the same installation back next year — making the process completely hands-off for you."),
  ("Are your Christmas lights energy efficient?", "Yes. We use LED commercial-grade Christmas lights in {loc} that use up to 80% less energy than traditional incandescent bulbs. They're brighter, run cooler (safer), and last much longer. LED lights also perform better in {loc}'s cold winter temperatures."),
  ("Can you create custom Christmas light displays?", "Yes. We design custom Christmas light displays for homes and businesses in {loc} — including roofline lighting, tree wrapping, pathway lights, garlands, and architectural accents. We work from your ideas or suggest designs based on your home's features."),
  ("Is Christmas light installation safe on my roof and gutters?", "We use professional installation clips and techniques designed to avoid damaging gutters, shingles, and fascia in {loc} homes. Our team is trained for safe roof-level work and carries full liability insurance."),
  ("Do you install Christmas lights for commercial properties in {loc}?", "Yes. We install commercial Christmas light displays for storefronts, office buildings, restaurants, and shopping centres in {loc}. Commercial installations include programmable LED systems, timer controls, and multi-year contracts with guaranteed maintenance."),
  ("What happens if a section of lights stops working?", "We guarantee our installations in {loc} throughout the entire display season. If any section fails due to product defect or installation issue, we return and fix it at no charge. This is why using our professional-grade lights matters."),
  ("Can you install Christmas lights on trees and not just the roofline?", "Yes. We wrap trees, shrubs, columns, railings, and architectural features in {loc} in addition to roofline lighting. Tree wrapping with warm white or colour-changing LEDs creates dramatic displays that stand out in your neighbourhood."),
],
'plumbing': [
  ("What plumbing services do you offer in {loc}?", "Our plumbing services in {loc} include: faucet and fixture replacement, toilet repair and replacement, shut-off valve replacement, pipe repairs, drain cleaning, kitchen and bathroom rough-in, water heater installation, and emergency leak response."),
  ("How much does plumbing work cost in {loc}?", "Plumbing costs in {loc} vary by job: faucet installation $150–$350; toilet replacement $200–$450; shut-off valve $100–$250; bathroom rough-in (new bathroom) $2,500–$6,000+. We provide written quotes before starting any work."),
  ("Do you handle emergency plumbing in {loc}?", "Yes. For urgent situations in {loc} — active leaks, burst pipes, sewage backups — contact us directly. We prioritize emergency calls and respond as quickly as possible to minimize water damage."),
  ("Do I need a permit for plumbing work in {loc}?", "In {loc}, permits are required for new plumbing rough-ins, drain relocations, and water line extensions. Simple fixture replacements in the same location (toilet, faucet, shut-off valve) typically don't require permits. We advise on requirements for your project."),
  ("Can you replace old galvanized or lead pipes in {loc}?", "Yes. We replace old galvanized steel and copper pipe systems in {loc} homes with modern PEX or copper piping. Lead pipe replacement (common in older {loc} homes) improves water quality and is eligible for city rebate programs."),
  ("What should I do in a plumbing emergency before the plumber arrives?", "Locate and close the nearest shut-off valve: under sinks and toilets for fixture issues, or the main shut-off (usually near the water meter in your basement) for whole-house issues. Turn off the water heater if you've shut the main. Then call us immediately."),
  ("Can you install a new bathroom or kitchen in my home?", "Yes. We handle complete plumbing rough-ins for new bathrooms and kitchens in {loc}. This includes: drain and vent stack installation, supply line rough-in, fixture installation, and permit coordination. We coordinate with other trades for full project delivery."),
  ("How do I know if I have a hidden water leak?", "Signs of hidden leaks in {loc} homes: unexplained increase in water bills, damp spots on walls or ceilings, musty odours, sounds of running water with no fixtures on, and reduced water pressure. We use pressure testing and visual inspection to locate leaks."),
  ("Can you fix low water pressure in my {loc} home?", "Yes. Low water pressure in {loc} homes is typically caused by: partially closed main valve, mineral buildup in aerators or pipes, corroded galvanized pipes, or pressure regulator failure. We diagnose and fix the root cause rather than just the symptom."),
  ("Do you install water heaters and tankless systems in {loc}?", "Yes. We install traditional tank water heaters and tankless (on-demand) hot water systems in {loc}. Tankless systems are more energy-efficient for most households and eliminate the risk of tank flooding. We advise on the right system for your hot water usage pattern."),
],
'blog': [
  ("What construction services are available in Toronto and the GTA?", "aMaximum Construction offers a full range of services across Toronto and the GTA: deck building, fence installation, bathroom renovation, basement renovation, general contracting, carpentry, handyman services, landscaping, interlocking, canopy installation, demolition, and plumbing."),
  ("How do I get a free quote from aMaximum Construction?", "Getting a quote is simple — contact us by email at amaximumconstructioncorp@gmail.com or use the contact form on our website. We respond within 24 hours and schedule a site visit to provide a detailed written estimate at no obligation."),
  ("Is aMaximum Construction licensed and insured?", "Yes. aMaximum Construction is a licensed and fully insured contractor serving Toronto and the GTA. We carry liability insurance and maintain WSIB clearance. All required permits are pulled for applicable projects."),
  ("What areas does aMaximum Construction serve?", "We serve all of Toronto and the Greater Toronto Area including: North York, Scarborough, Etobicoke, East York, Markham, Richmond Hill, Vaughan, Woodbridge, Aurora, Newmarket, and surrounding communities."),
  ("How long has aMaximum Construction been in business?", "aMaximum Construction has been serving Toronto and GTA homeowners since 2021. Our team has decades of combined experience in construction and renovation across all residential and light commercial project types."),
  ("Do you offer free estimates?", "Yes. We provide free, no-obligation written estimates for all projects. Our estimates include a full scope of work, materials specification, labour breakdown, and timeline. We never charge for estimates or site visits."),
  ("What is your payment policy?", "We use milestone-based payment schedules: a modest deposit to begin, progress payments at defined project milestones, and a final payment after your sign-off. We never ask for large upfront payments before work begins."),
  ("Do you guarantee your work?", "Yes. All our work comes with a written workmanship warranty. We stand behind the quality of every project — if something isn't right after completion, we come back and fix it. Material warranties from manufacturers are also passed through to our clients."),
  ("How do I prepare for a construction project at my home?", "Before work begins: clear the work area of furniture and valuables, ensure tradespeople have access to the space, discuss any pets or schedule sensitivities with us, and make sure water/electrical shutoffs are accessible. We'll provide a pre-start checklist."),
  ("What makes aMaximum Construction different from other contractors?", "We focus on clear communication, transparent pricing, and tidy job sites. Every project gets a written scope, timeline, and payment schedule before work starts. We coordinate all trades under one contract so you have one point of contact throughout the entire project."),
],
'location': [
  ("What construction services are available in {loc}?", "aMaximum Construction serves {loc} with a full range of services: deck building, fence installation, bathroom renovation, basement renovation, general contracting, carpentry, handyman services, landscaping, interlocking, canopy installation, and plumbing."),
  ("How do I get a quote for construction work in {loc}?", "Contact us at amaximumconstructioncorp@gmail.com or use the form on our website. We schedule a site visit in {loc} and provide a detailed written estimate within 24 hours of the visit — at no obligation."),
  ("Do you serve {loc} for deck building?", "Yes. We build custom decks throughout {loc} including pressure-treated wood, composite, and cedar decks. We handle permits, materials, and installation — providing a turnkey deck building service from design to final inspection."),
  ("Is aMaximum Construction licensed to work in {loc}?", "Yes. We are a licensed and fully insured contractor with WSIB clearance, serving {loc} and all of the Greater Toronto Area. All permits are obtained where required by {loc}'s building department."),
  ("What basement renovation services do you offer in {loc}?", "We provide full basement renovation services in {loc}: framing, insulation, drywall, flooring, electrical, plumbing rough-in, bathroom addition, legal apartment conversion, and permit management. We handle everything from design to final inspection."),
  ("How long do renovation projects take in {loc}?", "Timelines vary by project: bathroom renovation 3–6 weeks, basement 8–16 weeks, deck 1–2 weeks, fence 1–3 days. We provide a detailed project schedule before work begins and keep you updated throughout construction in {loc}."),
  ("Do you handle permits for renovation projects in {loc}?", "Yes. We manage the full permit process for applicable projects in {loc}: application, drawings, fees, scheduling inspections, and obtaining the final permit sign-off. You don't need to deal with the municipality directly."),
  ("Can you renovate a bathroom and basement at the same time in {loc}?", "Yes. Multi-trade projects are our specialty in {loc}. Running bathroom and basement renovations concurrently — or sequencing them efficiently — reduces total project time and disruption. We coordinate all trades under one contract."),
  ("What fence types do you install in {loc}?", "We install wood (cedar), vinyl (PVC), aluminum, and chain-link fencing in {loc}. Privacy fences, decorative fences, pool enclosures, and custom gates are all available. We ensure all installations comply with {loc}'s fence height bylaws."),
  ("How do I verify a contractor is legitimate in {loc}?", "Always verify: WSIB clearance certificate, liability insurance certificate, business registration, references from {loc} area projects, and request a detailed written contract with scope and payment milestones. Never pay in full upfront."),
],
'portfolio': [
  ("What types of projects has aMaximum Construction completed?", "Our portfolio includes deck building, fence installation, bathroom renovations, basement renovations, general contracting, carpentry, interlocking, landscaping, canopy installation, and handyman projects across Toronto and the GTA."),
  ("Where can I see photos of completed projects?", "Browse our portfolio on this page to see photos of completed construction and renovation projects across Toronto and the GTA. For more examples or to discuss a specific project type, contact us at amaximumconstructioncorp@gmail.com."),
  ("Do you take on custom and unique projects?", "Yes. Every project we take on in Toronto and the GTA is unique to the client's property, budget, and goals. We've completed projects ranging from small handyman visits to full multi-trade home renovations. Contact us to discuss your specific vision."),
  ("Can I visit a recently completed project site?", "With homeowner permission, we can arrange site visits to recently completed projects similar to yours. This is the best way to evaluate the quality of our work firsthand. Ask us when requesting a quote."),
  ("How long has aMaximum Construction been building in Toronto?", "aMaximum Construction has been serving Toronto and GTA homeowners since 2021. Our team brings decades of combined construction experience to every project — from small repairs to complete renovations."),
  ("Do you do both residential and commercial projects?", "Our primary focus is residential construction and renovation across Toronto and the GTA. We also take on light commercial projects — storefronts, office renovations, and commercial exterior work."),
  ("What is your approach to project quality control?", "Every project includes a pre-start scope review, milestone inspections by our site supervisor, and a final walkthrough with the homeowner before closing out the job. We don't consider a project complete until you're satisfied."),
  ("Can I get a reference from a past client?", "Yes. We provide references from past clients on request. We're proud of our work and happy to connect you with homeowners in Toronto and the GTA who can speak to their experience with aMaximum Construction."),
  ("Do you work with interior designers and architects?", "Yes. We work with interior designers, architects, and design-build teams across the GTA. We're experienced in executing design specifications and coordinating with other professionals on larger projects."),
  ("What warranty do you provide on completed projects?", "All completed projects come with a written workmanship warranty. Structural work carries a longer warranty period. Manufacturer warranties on materials are passed through to the homeowner. Full warranty terms are specified in your contract."),
],
}


def build_faq_html(service, location):
    questions = FAQS.get(service, FAQS['general'])
    loc = location
    items_html = ''
    for q, a in questions:
        q2 = q.replace('{loc}', loc)
        a2 = a.replace('{loc}', loc)
        items_html += f'''    <details class="faq-item">
      <summary>{q2}</summary>
      <p>{a2}</p>
    </details>\n'''

    # Subtitle
    if service in ('blog', 'portfolio'):
        subtitle = 'Common questions about our services and process.'
    elif location == 'Toronto & GTA':
        subtitle = f'Common questions about {service.replace("-"," ").title()} services in Toronto and the GTA.'
    else:
        subtitle = f'Common questions about {service.replace("-"," ").title()} services in {location}.'

    return f'''<section class="island reveal" id="faq" aria-label="Frequently asked questions">
  <span class="shine" aria-hidden="true"></span>
  <div class="section-head">
    <h2>Frequently Asked Questions</h2>
    <p>{subtitle}</p>
  </div>
  <div class="faq-list">
{items_html}  </div>
</section>'''


def process_file(filepath):
    try:
        content = open(filepath, encoding='utf-8').read()
    except Exception:
        return False

    # Skip redirect pages (very short)
    if len(content) < 500:
        return False

    rel = filepath.replace(ROOT, '').replace('\\', '/').lstrip('/')
    service = detect_service(rel)
    location = detect_location(rel)
    faq_html = build_faq_html(service, location)

    # Try to replace existing FAQ section
    if RE_FAQ_SECTION.search(content):
        new_content = RE_FAQ_SECTION.sub(faq_html, content, count=1)
    elif '<section class="shell" style="margin:40px auto;">' in content:
        # Insert before the reviews section
        new_content = content.replace(
            '<section class="shell" style="margin:40px auto;">',
            faq_html + '\n\n<section class="shell" style="margin:40px auto;">',
            1
        )
    elif '<footer class="site-footer">' in content:
        # Insert before footer
        new_content = content.replace(
            '<footer class="site-footer">',
            faq_html + '\n\n<footer class="site-footer">',
            1
        )
    else:
        return False

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


updated = []
skipped = 0
for dirpath, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for fname in files:
        if fname in SKIP or not fname.endswith('.html'):
            continue
        fp = os.path.join(dirpath, fname)
        if process_file(fp):
            rel = fp.replace(ROOT, '')
            updated.append(rel)
        else:
            skipped += 1

print(f'Updated {len(updated)} files, skipped {skipped}')
for u in updated[:20]:
    print(' ', u)
if len(updated) > 20:
    print(f'  ... and {len(updated)-20} more')
