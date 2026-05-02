#!/usr/bin/env python3
"""
Fix hub page structure: update location-grid and related-blogs sections
on all service hub pages. Does NOT change URLs.
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).parent

# ── SERVICE → LOCATION PAGES mapping ──────────────────────────────
# Each entry: hub_slug → list of (url, display_name)
# Only REAL location pages (not blog posts)

SERVICE_LOCATIONS = {
    "basement-renovation": [
        ("/basement-renovation-service-in-toronto/", "Toronto"),
        ("/basement-renovation-service-in-north-york/", "North York"),
        ("/basement-renovation-service-in-east-york/", "East York"),
        ("/basement-renovation-service-in-scarborough/", "Scarborough"),
        ("/basement-renovation-service-in-etobicoke/", "Etobicoke"),
        ("/basement-renovation-service-in-markham/", "Markham"),
        ("/basement-renovation-service-in-vaughan/", "Vaughan"),
        ("/basement-renovation-service-in-woodbridge/", "Woodbridge"),
        ("/basement-renovation-service-in-richmond-hill/", "Richmond Hill"),
        ("/basement-renovation-service-in-aurora/", "Aurora"),
        ("/basement-renovation-service-in-newmarket/", "Newmarket"),
        ("/basement-renovation-in-toronto/", "Basement Renovation in Toronto"),
        ("/basement-and-bathroom-renovation-in-north-york/", "Basement & Bathroom in North York"),
        ("/basement-bathroom-renovation-richmond-hill/", "Basement & Bathroom in Richmond Hill"),
    ],
    "bathroom-renovation": [
        ("/bathroom-renovation-aurora/", "Aurora"),
        ("/bathroom-renovation-mississauga/", "Mississauga"),
        ("/bathroom-renovation-richmond-hill/", "Richmond Hill"),
        ("/bathrooms-renovation-in-north-york/", "North York"),
    ],
    "deck-builder": [
        ("/deck-contractor-toronto/", "Toronto"),
        ("/deck-contractor-north-york/", "North York"),
        ("/deck-contractor-east-york/", "East York"),
        ("/deck-contractor-scarborough/", "Scarborough"),
        ("/deck-contractor-etobicoke/", "Etobicoke"),
        ("/deck-contractor-markham/", "Markham"),
        ("/deck-contractor-vaughan/", "Vaughan"),
        ("/deck-contractor-woodbridge/", "Woodbridge"),
        ("/deck-builder-in-richmond-hill/", "Richmond Hill"),
        ("/deck-contractor-aurora/", "Aurora"),
        ("/deck-contractor-newmarket/", "Newmarket"),
        ("/deck-contractor-bradford/", "Bradford"),
        ("/deck-contractor-burlington/", "Burlington"),
        ("/deck-contractor-concord/", "Concord"),
        ("/deck-contractor-east-gwillimbury/", "East Gwillimbury"),
        ("/deck-contractor-hamilton/", "Hamilton"),
        ("/deck-contractor-in-thornhill/", "Thornhill"),
        ("/deck-contractor-king-city/", "King City"),
        ("/deck-contractor-kleinburg/", "Kleinburg"),
        ("/deck-builder-toronto/", "Deck Builder Toronto"),
        ("/deck-builder-newmarket/", "Deck Builder Newmarket"),
        ("/deck-builder-schomberg/", "Schomberg"),
        ("/deck-builder-gta/", "GTA"),
        ("/deck-builder-in-richmond-hill/", "Deck Builder Richmond Hill"),
    ],
    "deck-railings": [
        ("/deck-railing-installer-in-toronto/", "Toronto"),
        ("/deck-railing-installer-in-north-york/", "North York"),
        ("/deck-railing-installer-in-east-york/", "East York"),
        ("/deck-railing-installer-in-scarborough/", "Scarborough"),
        ("/deck-railing-installer-in-etobicoke/", "Etobicoke"),
        ("/deck-railing-installer-in-markham/", "Markham"),
        ("/deck-railing-installer-in-vaughan/", "Vaughan"),
        ("/deck-railing-installer-in-woodbridge/", "Woodbridge"),
        ("/deck-railing-installer-in-richmond-hill/", "Richmond Hill"),
        ("/deck-railing-installer-in-aurora/", "Aurora"),
        ("/deck-railing-installer-in-newmarket/", "Newmarket"),
        ("/deck-railing-builder-markham/", "Railing Builder Markham"),
        ("/deck-railing-builder-richmond-hill/", "Railing Builder Richmond Hill"),
        ("/deck-railing-installation-in-king-city/", "King City"),
        ("/deck-railing-installer-east-york/", "Railing Installer East York"),
        ("/deck-railings-toronto/", "Deck Railings Toronto"),
        ("/deck-railing-vaughan/", "Railing Vaughan"),
    ],
    "fence-installation": [
        ("/fence-contractor-in-toronto/", "Toronto"),
        ("/fence-contractor-in-north-york/", "North York"),
        ("/fence-contractor-in-east-york/", "East York"),
        ("/fence-contractor-in-scarborough/", "Scarborough"),
        ("/fence-contractor-in-etobicoke/", "Etobicoke"),
        ("/fence-contractor-in-markham/", "Markham"),
        ("/fence-contractor-in-vaughan/", "Vaughan"),
        ("/fence-contractor-in-woodbridge/", "Woodbridge"),
        ("/fence-contractor-in-richmond-hill/", "Richmond Hill"),
        ("/fence-contractor-in-aurora/", "Aurora"),
        ("/fence-contractor-in-newmarket/", "Newmarket"),
        ("/fence-installer-aurora/", "Fence Installer Aurora"),
    ],
    "general-contractor": [
        ("/general-contractor-in-toronto/", "Toronto"),
        ("/general-contractor-in-north-york/", "North York"),
        ("/general-contractor-in-east-york/", "East York"),
        ("/general-contractor-in-scarborough/", "Scarborough"),
        ("/general-contractor-in-etobicoke/", "Etobicoke"),
        ("/general-contractor-in-markham/", "Markham"),
        ("/general-contractor-in-vaughan/", "Vaughan"),
        ("/general-contractor-in-woodbridge/", "Woodbridge"),
        ("/general-contractor-in-richmond-hill/", "Richmond Hill"),
        ("/general-contractor-in-aurora/", "Aurora"),
        ("/general-contractor-in-newmarket/", "Newmarket"),
        ("/general-contractor-in-king-city/", "King City"),
        ("/general-contractor-in-nobleton/", "Nobleton"),
        ("/general-contractor-in-whitchurch-stouffville/", "Whitchurch-Stouffville"),
        ("/general-contractor-services/", "General Contractor Services"),
        ("/general-contractor-services-2/", "General Contractor Services 2"),
        ("/general-contractor-services-near-me/", "General Contractor Near Me"),
    ],
    "handyman-services": [
        ("/handyman-service-in-toronto/", "Toronto"),
        ("/handyman-service-in-north-york/", "North York"),
        ("/handyman-service-in-east-york/", "East York"),
        ("/handyman-service-in-scarborough/", "Scarborough"),
        ("/handyman-service-in-etobicoke/", "Etobicoke"),
        ("/handyman-service-in-markham/", "Markham"),
        ("/handyman-service-in-vaughan/", "Vaughan"),
        ("/handyman-service-in-woodbridge/", "Woodbridge"),
        ("/handyman-service-in-richmond-hill/", "Richmond Hill"),
        ("/handyman-service-in-aurora/", "Aurora"),
        ("/handyman-service-in-newmarket/", "Newmarket"),
        ("/handyman-services-bayview-glen/", "Bayview Glen"),
        ("/handyman-services-in-glenville/", "Glenville"),
        ("/handyman-services-in-maple/", "Maple"),
        ("/handyman-services-in-markham/", "Markham (Alt)"),
        ("/handyman-services-in-thornhill-woods/", "Thornhill Woods"),
        ("/handyman-services-king-creek/", "King Creek"),
        ("/handyman-services-unionville/", "Unionville"),
    ],
    "demolition-services": [
        ("/demolition-service-in-toronto/", "Toronto"),
        ("/demolition-service-in-north-york/", "North York"),
        ("/demolition-service-in-east-york/", "East York"),
        ("/demolition-service-in-scarborough/", "Scarborough"),
        ("/demolition-service-in-etobicoke/", "Etobicoke"),
        ("/demolition-service-in-markham/", "Markham"),
        ("/demolition-service-in-vaughan/", "Vaughan"),
        ("/demolition-service-in-woodbridge/", "Woodbridge"),
        ("/demolition-service-in-richmond-hill/", "Richmond Hill"),
        ("/demolition-service-in-aurora/", "Aurora"),
        ("/demolition-service-in-newmarket/", "Newmarket"),
        ("/demolition-service-in-king-city/", "King City"),
        ("/demolition-service-in-whitchurch-stouffville/", "Whitchurch-Stouffville"),
        ("/demolition-service-brampton/", "Brampton"),
        ("/demolition-services-etobicoke/", "Etobicoke (Alt)"),
        ("/demolition-services-mississauga/", "Mississauga"),
        ("/demolition-services-nobleton/", "Nobleton"),
        ("/demolition-services-oakville/", "Oakville"),
        ("/demolition-services-scarborough/", "Scarborough (Alt)"),
    ],
    "interlocking-paver-services": [
        ("/interlocking-stone-services-in-toronto/", "Toronto"),
        ("/interlocking-stone-services-in-north-york/", "North York"),
        ("/interlocking-stone-services-in-east-york/", "East York"),
        ("/interlocking-stone-services-in-scarborough/", "Scarborough"),
        ("/interlocking-stone-services-in-etobicoke/", "Etobicoke"),
        ("/interlocking-stone-services-in-markham/", "Markham"),
        ("/interlocking-stone-services-in-vaughan/", "Vaughan"),
        ("/interlocking-stone-services-in-woodbridge/", "Woodbridge"),
        ("/interlocking-stone-services-in-richmond-hill/", "Richmond Hill"),
        ("/interlocking-stone-services-in-aurora/", "Aurora"),
        ("/interlocking-stone-services-in-newmarket/", "Newmarket"),
        ("/interlocking-stone-services-north-york/", "North York (Alt)"),
        ("/interlock-paving-contractor-in-east-gwillimbury/", "East Gwillimbury"),
        ("/interlock-paving-contractor-richmond-hill/", "Paving Richmond Hill"),
    ],
    "home-renovation": [
        ("/home-renovation-toronto/", "Toronto"),
        ("/home-renovation-north-york/", "North York"),
        ("/home-renovation-east-york/", "East York"),
        ("/home-renovation-scarborough/", "Scarborough"),
        ("/home-renovation-etobicoke/", "Etobicoke"),
        ("/home-renovation-markham/", "Markham"),
        ("/home-renovation-vaughan/", "Vaughan"),
        ("/home-renovation-woodbridge/", "Woodbridge"),
        ("/home-renovation-richmond-hill/", "Richmond Hill"),
        ("/home-renovation-aurora/", "Aurora"),
        ("/home-renovation-newmarket/", "Newmarket"),
    ],
    "carpenter-services": [
        ("/carpenter-services-toronto/", "Toronto"),
        ("/carpenter-services-north-york/", "North York"),
        ("/carpenter-services-east-york/", "East York"),
        ("/carpenter-services-scarborough/", "Scarborough"),
        ("/carpenter-services-etobicoke/", "Etobicoke"),
        ("/carpenter-services-markham/", "Markham"),
        ("/carpenter-services-vaughan/", "Vaughan"),
        ("/carpenter-services-woodbridge/", "Woodbridge"),
        ("/carpenter-services-richmond-hill/", "Richmond Hill"),
        ("/carpenter-services-aurora/", "Aurora"),
        ("/carpenter-services-newmarket/", "Newmarket"),
        ("/carpenter-services-brampton/", "Brampton"),
        ("/carpenter-services-mississauga/", "Mississauga"),
    ],
    "renovation-service": [
        ("/renovation-services-in-toronto/", "Toronto"),
        ("/renovation-services-in-north-york/", "North York"),
        ("/renovation-services-in-richmond-hill/", "Richmond Hill"),
        ("/renovation-services-in-aurora/", "Aurora"),
        ("/renovation-services-in-newmarket/", "Newmarket"),
        ("/renovation-services-in-vaughan/", "Vaughan"),
        ("/renovation-services-in-toronto-2/", "Toronto (Specialists)"),
        ("/renovation-services-in-toronto-gta/", "Toronto GTA"),
    ],
    "christmas-lights-installation-toronto-gta": [
        ("/christmas-lights-installation-in-richmond-hill/", "Richmond Hill"),
        ("/christmas-lights-installation-in-forest-hill/", "Forest Hill"),
    ],
    "landscaping-services": [
        ("/landscaping-services-toronto/", "Toronto"),
    ],
    # These have no location pages
    "canopy": [],
    "excavation-services": [],
    "electrical-handyman-services": [],
}

# ── SERVICE → BLOG POSTS mapping ─────────────────────────────────
SERVICE_BLOGS = {
    "basement-renovation": [
        ("/a-look-at-tips-to-remodel-your-basement-with-low-ceiling/", "Tips to Remodel a Basement with Low Ceilings"),
        ("/affordable-basement-renovation-toronto-guide/", "Affordable Basement Renovation in Toronto: A Practical Guide"),
        ("/basement-renovation-costs-toronto-guide/", "Basement Renovation Costs in Toronto: Complete Guide"),
        ("/expensive-parts-basement-renovation/", "The Most Expensive Parts of a Basement Renovation"),
        ("/is-it-really-worth-it-to-renovate-a-basement/", "Is It Really Worth It to Renovate a Basement?"),
        ("/navigating-basement-renovation-in-toronto-top-contractors-to-consider/", "Navigating Basement Renovation: Choosing the Right Contractor"),
        ("/reasons-to-hire-amaximum-construction-for-basement-renovation-services/", "5 Reasons to Choose aMaximum for Basement Renovation"),
        ("/1-basement-renovation-near-me/", "Basement Renovation Near Me"),
        ("/blog/basement-renovation-ideas/", "Creative Basement Renovation Ideas"),
        ("/best-basement-renovation-service-in-aurora/", "Best Basement Renovation Service in Aurora"),
        ("/best-basement-renovation-service-in-newmarket/", "Best Basement Renovation Service in Newmarket"),
        ("/best-basement-renovation-service-richmond-hill/", "Best Basement Renovation Service in Richmond Hill"),
    ],
    "bathroom-renovation": [
        ("/accessorizing-renovated-bathroom-toronto/", "Accessorizing Your Renovated Bathroom in Toronto"),
        ("/electing-materials-bathroom-renovation-toronto/", "Selecting Materials for Bathroom Renovation in Toronto"),
        ("/elegant-bathroom-makeovers-selecting-the-right-renovation-services-in-toronto/", "Elegant Bathroom Makeovers: Selecting the Right Renovation Services"),
        ("/interior-bathroom-renovation-toronto/", "Interior Bathroom Renovation in Toronto"),
        ("/navigating-permits-regulations-bathroom-renovation-toronto/", "Navigating Permits & Regulations for Bathroom Renovation"),
        ("/blog/bathroom-renovation-guide/", "Complete Bathroom Renovation Guide"),
        ("/basement-and-bathroom-renovation-in-north-york/", "Basement & Bathroom Renovation in North York"),
    ],
    "deck-builder": [
        ("/3-easy-ways-to-care-for-your-deck-so-it-always-looks-great/", "3 Easy Ways to Care for Your Deck"),
        ("/amazing-decks-in-richmond-hill/", "Amazing Decks in Richmond Hill"),
        ("/best-decking-materials-outdoor-decks/", "Best Decking Materials for Outdoor Decks"),
        ("/building-a-deck-in-aurora/", "Building a Deck in Aurora"),
        ("/building-a-small-deck-in-toronto/", "Building a Small Deck in Toronto"),
        ("/choosing-perfect-deck-contractor/", "Choosing the Perfect Deck Contractor"),
        ("/choose-right-decking-material-landscape/", "Choose the Right Decking Material"),
        ("/custom-decks-richmond-hill/", "Custom Decks in Richmond Hill"),
        ("/deck-maintenance-in-markhams-variable-climate/", "Deck Maintenance in Markham's Climate"),
        ("/essential-deck-maintenance-for-newmarket-homes/", "Essential Deck Maintenance for Newmarket Homes"),
        ("/expert-deck-building-in-aurora/", "Expert Deck Building in Aurora"),
        ("/expert-richmond-hill-deck-builders-quality-decks/", "Expert Richmond Hill Deck Builders"),
        ("/find-perfect-deck-contractor/", "Find the Perfect Deck Contractor"),
        ("/how-amaximum-repair-damaged-deck-boards/", "How aMaximum Repairs Damaged Deck Boards"),
        ("/how-can-i-ensure-timely-completion-of-my-deck-construction-project/", "How to Ensure Timely Completion of Your Deck Project"),
        ("/how-long-does-it-take-to-complete-a-deck-construction-project/", "How Long Does a Deck Construction Project Take?"),
        ("/how-to-repair-wood-decks/", "How to Repair Wood Decks"),
        ("/is-it-cheaper-to-build-your-own-deck-aurora/", "Is It Cheaper to Build Your Own Deck in Aurora?"),
        ("/reasons-to-hire-professional-deck-contractors/", "Reasons to Hire Professional Deck Contractors"),
        ("/richmond-hill-custom-decks-sustainable-stylish/", "Richmond Hill Custom Decks: Sustainable & Stylish"),
        ("/starting-deck-boards-installation/", "Starting Deck Board Installation"),
        ("/toronto-deck-builders-combining-aesthetics-with-durability/", "Toronto Deck Builders: Aesthetics & Durability"),
        ("/trex-rainescape-system-toronto/", "Trex RainEscape System in Toronto"),
        ("/what-is-a-good-price-for-a-deck-in-toronto/", "What Is a Good Price for a Deck in Toronto?"),
        ("/wood-deck-repair-in-unionville/", "Wood Deck Repair in Unionville"),
        ("/amaximum-deck-builder-blog/", "aMaximum Deck Builder Blog"),
        ("/blog/deck-maintenance-tips/", "Deck Maintenance Tips"),
        ("/privacy-screen-deck/", "Privacy Screen for Decks"),
        ("/exploring-the-benefits-of-outdoor-living-spaces-enhancing-your-home-and-lifestyle/", "Benefits of Outdoor Living Spaces"),
    ],
    "deck-railings": [
        ("/privacy-screen-installation-in-north-york/", "Privacy Screen Installation in North York"),
    ],
    "fence-installation": [
        ("/choosing-the-best-fence-contractor/", "Choosing the Best Fence Contractor"),
        ("/searching-for-the-top-rated-fence-contractors/", "Searching for Top-Rated Fence Contractors"),
        ("/torontos-top-rated-fence-contractors-a-comprehensive-comparison/", "Toronto's Top-Rated Fence Contractors: A Comparison"),
        ("/ultimate-guide-finding-best-fence-contractor/", "Ultimate Guide to Finding the Best Fence Contractor"),
        ("/blog/fence-installation-options/", "Fence Installation Options"),
    ],
    "general-contractor": [
        ("/expert-insights-crafting-excellence-with-torontos-general-contracting-services/", "Expert Insights: Toronto's General Contracting Services"),
        ("/scammer-in-contractors-industry-toronto/", "How to Spot Contractor Scams in Toronto"),
        ("/avoiding-general-contractor-scams/", "Avoiding General Contractor Scams"),
        ("/blog/contractor-selection-guide/", "Contractor Selection Guide"),
    ],
    "handyman-services": [
        ("/a-review-of-the-7-best-handyman-services-in-toronto-2023/", "Review of 7 Best Handyman Services in Toronto"),
        ("/advantages-of-hiring-a-handyman/", "Advantages of Hiring a Handyman"),
        ("/avoid-handyman-scams/", "How to Avoid Handyman Scams"),
        ("/handyman-charges/", "Handyman Charges: What to Expect"),
        ("/rate-for-a-handyman/", "Rate for a Handyman in Toronto"),
        ("/selecting-top-notch-handyman-and-contractor-services/", "Selecting Top-Notch Handyman Services"),
        ("/handyman-drywall-repair/", "Handyman Drywall Repair"),
        ("/handyman-furniture-assembly/", "Handyman Furniture Assembly"),
        ("/handyman-painting-services/", "Handyman Painting Services"),
        ("/handyman-plumbing-services/", "Handyman Plumbing Services"),
    ],
    "demolition-services": [
        ("/expert-demolition-services-a-maximum-construction/", "Expert Demolition Services by aMaximum"),
        ("/professional-demolition-services/", "Professional Demolition Services"),
        ("/backyard-demolition-services-landscaper/", "Backyard Demolition & Landscaping Services"),
    ],
    "interlocking-paver-services": [
        ("/benefits-of-interlocking-pavers-in-toronto/", "Benefits of Interlocking Pavers in Toronto"),
    ],
    "home-renovation": [
        ("/affordable-home-renovation-tips-toronto/", "Affordable Home Renovation Tips for Toronto"),
        ("/transforming-spaces-your-trusted-partners-for-home-renovation-in-toronto/", "Transforming Spaces: Home Renovation in Toronto"),
        ("/construction-project-in-the-winter/", "Construction Projects in Winter"),
    ],
    "carpenter-services": [
        ("/blog-carpenter-services-toronto-gta/", "Carpenter Services in Toronto & GTA"),
    ],
    "renovation-service": [
        ("/affordable-home-renovation-tips-toronto/", "Affordable Home Renovation Tips for Toronto"),
        ("/avoiding-general-contractor-scams/", "Avoiding General Contractor Scams"),
        ("/construction-project-in-the-winter/", "Can You Do a Construction Project in Winter?"),
        ("/contractor-not-warranty/", "When Your Contractor Doesn't Honour Warranty"),
        ("/contractor-warranty-client-materials-guide/", "Contractor Warranty with Client Materials"),
        ("/effective-communication/", "Effective Communication with Your Contractor"),
        ("/expert-tips/", "Expert Tips for a Successful Renovation"),
        ("/first-steps-renovation-permits/", "First Steps: Renovation Permits in Ontario"),
        ("/installation-timelines/", "Renovation Timelines: What to Expect"),
        ("/legal-considerations-renovating/", "Legal Considerations When Renovating"),
        ("/material-costs-in-billing-explained/", "Material Costs in Billing Explained"),
        ("/scammer-in-contractors-industry-toronto/", "How to Spot Contractor Scams"),
        ("/selecting-top-notch-handyman-and-contractor-services/", "Selecting Top-Notch Contractor Services"),
        ("/small-contractors-in-toronto/", "Small Contractors in Toronto"),
        ("/supply-my-own-materials/", "Should You Supply Your Own Materials?"),
        ("/top-affordable-small-contractors-in-toronto/", "Top Affordable Small Contractors in Toronto"),
        ("/transforming-spaces-your-trusted-partners-for-home-renovation-in-toronto/", "Transforming Spaces: Home Renovation in Toronto"),
        ("/trusted-small-contractors-toronto/", "Trusted Small Contractors in Toronto"),
        ("/understanding-additional-service-costs/", "Understanding Additional Service Costs"),
    ],
    "christmas-lights-installation-toronto-gta": [
        ("/bright-ideas-christmas-light-displays/", "Bright Ideas for Christmas Light Displays"),
        ("/how-to-avoid-injury-while-hanging-christmas-lights/", "How to Avoid Injury Hanging Christmas Lights"),
        ("/professional-christmas-lights-installer-aurora/", "Professional Christmas Lights Installer in Aurora"),
    ],
    "landscaping-services": [
        ("/5-types-of-landscaping-features-you-can-find-in-toronto/", "5 Types of Landscaping Features in Toronto"),
        ("/backyard-oasis-in-richmond-hill/", "Backyard Oasis in Richmond Hill"),
        ("/exploring-the-benefits-of-outdoor-living-spaces-enhancing-your-home-and-lifestyle/", "Benefits of Outdoor Living Spaces"),
    ],
    "excavation-services": [],
    "canopy": [],
    "electrical-handyman-services": [
        ("/blog/plumbing-emergency-guide/", "Plumbing Emergency Guide"),
    ],
}

# Service display names for section headings
SERVICE_NAMES = {
    "basement-renovation": "Basement Renovation",
    "bathroom-renovation": "Bathroom Renovation",
    "deck-builder": "Deck Building",
    "deck-railings": "Deck Railings",
    "fence-installation": "Fence Installation",
    "general-contractor": "General Contractor",
    "handyman-services": "Handyman Services",
    "demolition-services": "Demolition Services",
    "interlocking-paver-services": "Interlocking & Paving",
    "home-renovation": "Home Renovation",
    "carpenter-services": "Carpentry",
    "renovation-service": "Renovation Services",
    "christmas-lights-installation-toronto-gta": "Christmas Lights Installation",
    "landscaping-services": "Landscaping",
    "excavation-services": "Excavation",
    "canopy": "Canopy & Awnings",
    "electrical-handyman-services": "Electrical Services",
}


def build_location_grid_html(hub_slug):
    """Build the full location-grid section HTML."""
    locations = SERVICE_LOCATIONS.get(hub_slug, [])
    if not locations:
        return ""
    name = SERVICE_NAMES.get(hub_slug, hub_slug.replace("-", " ").title())
    lines = []
    lines.append(f'<section class="island reveal service-locations" id="locations" aria-label="Service locations">')
    lines.append(f'  <span class="shine" aria-hidden="true"></span>')
    lines.append(f'  <div class="section-head">')
    lines.append(f'    <h2>{name} in Your Area</h2>')
    lines.append(f'    <p>We provide professional {name.lower()} services across the Greater Toronto Area. Select your location:</p>')
    lines.append(f'  </div>')
    lines.append(f'  <div class="location-grid">')
    for url, display in sorted(locations, key=lambda x: x[1]):
        lines.append(f'    <a href="{url}" class="location-card">{display}</a>')
    lines.append(f'  </div>')
    lines.append(f'</section>')
    return "\n".join(lines)


def build_related_blogs_html(hub_slug):
    """Build the related-blogs section HTML."""
    blogs = SERVICE_BLOGS.get(hub_slug, [])
    if not blogs:
        return ""
    lines = []
    lines.append(f'<section id="related-blogs" class="shell" style="padding:32px 0 0;">')
    lines.append(f'  <h2 style="font-size:1.25rem;font-weight:700;color:#121826;margin-bottom:12px;">Related Blog Posts</h2>')
    lines.append(f'  <ul style="margin:0;padding-left:18px;display:flex;flex-direction:column;gap:10px;">')
    for url, title in blogs:
        lines.append(f'    <li><a href="{url}">{title}</a></li>')
    lines.append(f'  </ul>')
    lines.append(f'</section>')
    return "\n".join(lines)


def build_articles_section_html(hub_slug):
    """Build the related-articles cards section HTML."""
    blogs = SERVICE_BLOGS.get(hub_slug, [])
    if not blogs:
        return ""
    name = SERVICE_NAMES.get(hub_slug, hub_slug.replace("-", " ").title())
    lines = []
    lines.append(f'<section class="island reveal related-articles" id="articles" aria-label="Related articles">')
    lines.append(f'  <span class="shine" aria-hidden="true"></span>')
    lines.append(f'  <div class="section-head">')
    lines.append(f'    <h2>Related Articles</h2>')
    lines.append(f'    <p>Learn more about {name.lower()} with our helpful guides and tips.</p>')
    lines.append(f'  </div>')
    lines.append(f'  <div class="cards">')
    for url, title in blogs:
        short = title[:50] + "..." if len(title) > 50 else title
        lines.append(f'    <a href="{url}" class="card">')
        lines.append(f'      <h3>{short}</h3>')
        lines.append(f'    </a>')
    lines.append(f'  </div>')
    lines.append(f'</section>')
    return "\n".join(lines)


def replace_section(html, section_id, new_html, tag="section"):
    """Replace a <section id="..."> ... </section> block."""
    # Match the section by id attribute
    pattern = re.compile(
        rf'<{tag}[^>]*\bid=["\']?{re.escape(section_id)}["\']?[^>]*>.*?</{tag}>',
        re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(html)
    if match:
        if new_html:
            return html[:match.start()] + new_html + html[match.end():]
        else:
            return html  # Don't remove if no replacement
    return None  # Section not found


def find_insert_point(html):
    """Find the best place to insert new sections (before footer)."""
    # Insert before <footer
    idx = html.find('<footer')
    if idx != -1:
        return idx
    return None


def process_hub(hub_slug):
    hub_path = ROOT / hub_slug / "index.html"
    if not hub_path.exists():
        print(f"  ⚠  Hub file not found: {hub_path}")
        return False

    html = hub_path.read_text(encoding="utf-8")
    original = html
    changes = []

    # 1) Replace or add location-grid section
    new_loc = build_location_grid_html(hub_slug)
    if new_loc:
        # Try to find existing service-locations section
        loc_pattern = re.compile(
            r'<section[^>]*\bclass=["\'][^"\']*service-locations[^"\']*["\'][^>]*>.*?</section>',
            re.DOTALL | re.IGNORECASE
        )
        loc_match = loc_pattern.search(html)
        if not loc_match:
            # Also try by id="locations"
            loc_pattern2 = re.compile(
                r'<section[^>]*\bid=["\']?locations["\']?[^>]*>.*?</section>',
                re.DOTALL | re.IGNORECASE
            )
            loc_match = loc_pattern2.search(html)
        
        if loc_match:
            html = html[:loc_match.start()] + new_loc + html[loc_match.end():]
            changes.append("replaced location-grid")
        else:
            # Insert before footer
            idx = find_insert_point(html)
            if idx:
                html = html[:idx] + "\n" + new_loc + "\n\n" + html[idx:]
                changes.append("added location-grid")

    # 2) Replace or add related-blogs section
    new_blogs = build_related_blogs_html(hub_slug)
    if new_blogs:
        result = replace_section(html, "related-blogs", new_blogs)
        if result:
            html = result
            changes.append("replaced related-blogs")
        else:
            # Insert before location section or footer
            loc_sec = re.search(r'<section[^>]*\bclass=["\'][^"\']*service-locations', html)
            if loc_sec:
                html = html[:loc_sec.start()] + new_blogs + "\n\n" + html[loc_sec.start():]
            else:
                idx = find_insert_point(html)
                if idx:
                    html = html[:idx] + "\n" + new_blogs + "\n\n" + html[idx:]
            changes.append("added related-blogs")

    # 3) Replace or add related-articles section
    new_articles = build_articles_section_html(hub_slug)
    if new_articles:
        result = replace_section(html, "articles", new_articles)
        if result:
            html = result
            changes.append("replaced related-articles")
        else:
            # Insert after location section or before footer
            loc_sec_end = re.search(r'</section>\s*(?=<section[^>]*related-articles|<footer)', html)
            idx = find_insert_point(html)
            if idx:
                html = html[:idx] + "\n" + new_articles + "\n\n" + html[idx:]
            changes.append("added related-articles")

    if html != original:
        hub_path.write_text(html, encoding="utf-8")
        print(f"  ✅ {hub_slug}: {', '.join(changes)}")
        return True
    else:
        print(f"  ── {hub_slug}: no changes needed")
        return False


def main():
    print("=" * 60)
    print("Fixing hub page structure (locations + blogs)")
    print("=" * 60)
    
    changed = 0
    total = 0
    
    for hub_slug in SERVICE_LOCATIONS:
        total += 1
        print(f"\n[{total}] Processing: {hub_slug}")
        if process_hub(hub_slug):
            changed += 1
    
    print(f"\n{'=' * 60}")
    print(f"Done. Updated {changed}/{total} hub pages.")
    print("=" * 60)


if __name__ == "__main__":
    main()
