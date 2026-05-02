#!/usr/bin/env python3
"""
Add location navigation grid to ALL spoke (service+location) pages.
Each spoke page gets a grid showing all other locations for the SAME service,
plus a link back to the service hub.

Does NOT change URLs. Inserts sections before <footer>.
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).parent

# ── SERVICE → (hub_url, hub_name, [(spoke_url, spoke_name), ...]) ──
SERVICES = {
    "basement-renovation": {
        "hub": "/basement-renovation/",
        "name": "Basement Renovation",
        "spokes": [
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
            ("/basement-renovation-in-toronto/", "Basement Renovation Toronto"),
            ("/basement-and-bathroom-renovation-in-north-york/", "Basement & Bathroom North York"),
            ("/basement-bathroom-renovation-richmond-hill/", "Basement & Bathroom Richmond Hill"),
        ],
        "blogs": [
            ("/a-look-at-tips-to-remodel-your-basement-with-low-ceiling/", "Tips to Remodel a Basement with Low Ceilings"),
            ("/affordable-basement-renovation-toronto-guide/", "Affordable Basement Renovation Guide"),
            ("/basement-renovation-costs-toronto-guide/", "Basement Renovation Costs Guide"),
            ("/expensive-parts-basement-renovation/", "Most Expensive Parts of Basement Renovation"),
            ("/is-it-really-worth-it-to-renovate-a-basement/", "Is It Worth Renovating a Basement?"),
            ("/blog/basement-renovation-ideas/", "Basement Renovation Ideas"),
        ],
    },
    "bathroom-renovation": {
        "hub": "/bathroom-renovation/",
        "name": "Bathroom Renovation",
        "spokes": [
            ("/bathroom-renovation-aurora/", "Aurora"),
            ("/bathroom-renovation-mississauga/", "Mississauga"),
            ("/bathroom-renovation-richmond-hill/", "Richmond Hill"),
            ("/bathrooms-renovation-in-north-york/", "North York"),
        ],
        "blogs": [
            ("/accessorizing-renovated-bathroom-toronto/", "Accessorizing Your Renovated Bathroom"),
            ("/navigating-permits-regulations-bathroom-renovation-toronto/", "Navigating Permits for Bathroom Renovation"),
            ("/blog/bathroom-renovation-guide/", "Complete Bathroom Renovation Guide"),
        ],
    },
    "deck-builder": {
        "hub": "/deck-builder/",
        "name": "Deck Building",
        "spokes": [
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
        "blogs": [
            ("/3-easy-ways-to-care-for-your-deck-so-it-always-looks-great/", "3 Easy Ways to Care for Your Deck"),
            ("/how-to-repair-wood-decks/", "How to Repair Wood Decks"),
            ("/what-is-a-good-price-for-a-deck-in-toronto/", "What Is a Good Price for a Deck?"),
            ("/blog/deck-maintenance-tips/", "Deck Maintenance Tips"),
        ],
    },
    "deck-railings": {
        "hub": "/deck-railings/",
        "name": "Deck Railings",
        "spokes": [
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
        "blogs": [
            ("/privacy-screen-installation-in-north-york/", "Privacy Screen Installation in North York"),
        ],
    },
    "fence-installation": {
        "hub": "/fence-installation/",
        "name": "Fence Installation",
        "spokes": [
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
        "blogs": [
            ("/choosing-the-best-fence-contractor/", "Choosing the Best Fence Contractor"),
            ("/ultimate-guide-finding-best-fence-contractor/", "Ultimate Guide to Finding a Fence Contractor"),
            ("/blog/fence-installation-options/", "Fence Installation Options"),
        ],
    },
    "general-contractor": {
        "hub": "/general-contractor/",
        "name": "General Contractor",
        "spokes": [
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
        "blogs": [
            ("/avoiding-general-contractor-scams/", "Avoiding General Contractor Scams"),
            ("/blog/contractor-selection-guide/", "Contractor Selection Guide"),
        ],
    },
    "handyman-services": {
        "hub": "/handyman-services/",
        "name": "Handyman Services",
        "spokes": [
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
        "blogs": [
            ("/advantages-of-hiring-a-handyman/", "Advantages of Hiring a Handyman"),
            ("/avoid-handyman-scams/", "How to Avoid Handyman Scams"),
            ("/handyman-charges/", "Handyman Charges: What to Expect"),
            ("/rate-for-a-handyman/", "Rate for a Handyman in Toronto"),
        ],
    },
    "demolition-services": {
        "hub": "/demolition-services/",
        "name": "Demolition Services",
        "spokes": [
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
        "blogs": [
            ("/expert-demolition-services-a-maximum-construction/", "Expert Demolition Services"),
            ("/professional-demolition-services/", "Professional Demolition Services"),
        ],
    },
    "interlocking-paver-services": {
        "hub": "/interlocking-paver-services/",
        "name": "Interlocking & Paving",
        "spokes": [
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
        "blogs": [
            ("/benefits-of-interlocking-pavers-in-toronto/", "Benefits of Interlocking Pavers"),
        ],
    },
    "home-renovation": {
        "hub": "/home-renovation/",
        "name": "Home Renovation",
        "spokes": [
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
        "blogs": [
            ("/affordable-home-renovation-tips-toronto/", "Affordable Home Renovation Tips"),
            ("/construction-project-in-the-winter/", "Construction Projects in Winter"),
        ],
    },
    "carpenter-services": {
        "hub": "/carpenter-services/",
        "name": "Carpentry",
        "spokes": [
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
        "blogs": [
            ("/blog-carpenter-services-toronto-gta/", "Carpenter Services in Toronto & GTA"),
        ],
    },
    "renovation-service": {
        "hub": "/renovation-service/",
        "name": "Renovation Services",
        "spokes": [
            ("/renovation-services-in-toronto/", "Toronto"),
            ("/renovation-services-in-north-york/", "North York"),
            ("/renovation-services-in-richmond-hill/", "Richmond Hill"),
            ("/renovation-services-in-aurora/", "Aurora"),
            ("/renovation-services-in-newmarket/", "Newmarket"),
            ("/renovation-services-in-vaughan/", "Vaughan"),
            ("/renovation-services-in-toronto-2/", "Toronto (Specialists)"),
            ("/renovation-services-in-toronto-gta/", "Toronto GTA"),
        ],
        "blogs": [
            ("/first-steps-renovation-permits/", "Renovation Permits in Ontario"),
            ("/legal-considerations-renovating/", "Legal Considerations When Renovating"),
        ],
    },
    "christmas-lights": {
        "hub": "/christmas-lights-installation-toronto-gta/",
        "name": "Christmas Lights Installation",
        "spokes": [
            ("/christmas-lights-installation-in-richmond-hill/", "Richmond Hill"),
            ("/christmas-lights-installation-in-forest-hill/", "Forest Hill"),
        ],
        "blogs": [
            ("/bright-ideas-christmas-light-displays/", "Bright Ideas for Christmas Lights"),
            ("/how-to-avoid-injury-while-hanging-christmas-lights/", "Avoid Injury Hanging Christmas Lights"),
        ],
    },
    "landscaping": {
        "hub": "/landscaping-services/",
        "name": "Landscaping",
        "spokes": [
            ("/landscaping-services-toronto/", "Toronto"),
        ],
        "blogs": [
            ("/5-types-of-landscaping-features-you-can-find-in-toronto/", "5 Types of Landscaping Features in Toronto"),
            ("/backyard-oasis-in-richmond-hill/", "Backyard Oasis in Richmond Hill"),
        ],
    },
}


def url_to_dir(url):
    """Convert URL like /handyman-service-in-toronto/ to directory name."""
    return url.strip("/")


def build_spoke_nav_html(service_key, current_spoke_url):
    """Build location nav + blog section for a spoke page."""
    svc = SERVICES[service_key]
    hub_url = svc["hub"]
    name = svc["name"]
    spokes = svc["spokes"]
    blogs = svc["blogs"]
    
    lines = []
    
    # Location navigation
    lines.append(f'<section class="island reveal service-locations" id="other-locations" aria-label="Other locations">')
    lines.append(f'  <span class="shine" aria-hidden="true"></span>')
    lines.append(f'  <div class="section-head">')
    lines.append(f'    <h2>{name} in Other Areas</h2>')
    name_lc = name.lower()
    # Avoid "services services" duplication  
    if name_lc.endswith("services") or name_lc.endswith("installation"):
        lines.append(f'    <p>We also provide {name_lc} in these areas. <a href="{hub_url}">View all {name_lc} &rarr;</a></p>')
    else:
        lines.append(f'    <p>We also provide {name_lc} services in these areas. <a href="{hub_url}">View all {name_lc} services &rarr;</a></p>')
    lines.append(f'  </div>')
    lines.append(f'  <div class="location-grid">')
    for url, display in sorted(spokes, key=lambda x: x[1]):
        if url == current_spoke_url:
            # Current page - show as active/disabled
            lines.append(f'    <span class="location-card location-card-active">{display}</span>')
        else:
            lines.append(f'    <a href="{url}" class="location-card">{display}</a>')
    lines.append(f'  </div>')
    lines.append(f'</section>')
    
    # Related blogs (compact)
    if blogs:
        lines.append(f'')
        lines.append(f'<section id="related-blogs" class="shell" style="padding:32px 0 0;">')
        lines.append(f'  <h2 style="font-size:1.25rem;font-weight:700;color:#121826;margin-bottom:12px;">Related Articles</h2>')
        lines.append(f'  <ul style="margin:0;padding-left:18px;display:flex;flex-direction:column;gap:10px;">')
        for url, title in blogs:
            lines.append(f'    <li><a href="{url}">{title}</a></li>')
        lines.append(f'  </ul>')
        lines.append(f'</section>')
    
    return "\n".join(lines)


def process_spoke(service_key, spoke_url):
    """Add location nav to a single spoke page."""
    dir_name = url_to_dir(spoke_url)
    file_path = ROOT / dir_name / "index.html"
    
    if not file_path.exists():
        return "missing"
    
    html = file_path.read_text(encoding="utf-8")
    
    # Check if already has location nav - remove it for re-generation
    if 'id="other-locations"' in html:
        # Remove old section
        start = html.find('<section class="island reveal service-locations" id="other-locations"')
        if start != -1:
            end = html.find('</section>', start)
            if end != -1:
                end += len('</section>')
                # Also remove related-blogs section if it follows
                next_section = html[end:end+200].strip()
                if next_section.startswith('<section id="related-blogs"'):
                    end2 = html.find('</section>', end + 1)
                    if end2 != -1:
                        end = end2 + len('</section>')
                html = html[:start] + html[end:]
    
    new_section = build_spoke_nav_html(service_key, spoke_url)
    
    # Find insertion point - before <footer
    footer_idx = html.find("<footer")
    if footer_idx == -1:
        return "no-footer"
    
    # Also check if there's a service-hub-link div - insert before it or before footer
    hub_link_idx = html.find('<div class="service-hub-link">')
    
    if hub_link_idx != -1 and hub_link_idx < footer_idx:
        insert_idx = hub_link_idx
    else:
        insert_idx = footer_idx
    
    html = html[:insert_idx] + "\n" + new_section + "\n\n" + html[insert_idx:]
    
    file_path.write_text(html, encoding="utf-8")
    return "updated"


def main():
    print("=" * 60)
    print("Adding location navigation to spoke pages")
    print("=" * 60)
    
    stats = {"updated": 0, "skip": 0, "missing": 0, "no-footer": 0}
    
    for service_key, svc in SERVICES.items():
        print(f"\n[{svc['name']}] ({len(svc['spokes'])} spoke pages)")
        for spoke_url, spoke_name in svc["spokes"]:
            result = process_spoke(service_key, spoke_url)
            stats[result] += 1
            if result == "updated":
                print(f"  OK {spoke_name}: {url_to_dir(spoke_url)}")
            elif result == "missing":
                print(f"  WARN {spoke_name}: file not found ({url_to_dir(spoke_url)})")
            elif result == "skip":
                print(f"  SKIP {spoke_name}: already has nav")
            elif result == "no-footer":
                print(f"  FAIL {spoke_name}: no <footer> found")
    
    print(f"\n{'=' * 60}")
    print(f"Done. Updated: {stats['updated']}, Skipped: {stats['skip']}, Missing: {stats['missing']}, No footer: {stats['no-footer']}")
    print(f"Total spoke pages processed: {sum(stats.values())}")
    print("=" * 60)


if __name__ == "__main__":
    main()
