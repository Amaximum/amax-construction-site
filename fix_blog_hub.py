#!/usr/bin/env python3
"""
Update the blog hub page (/blog/index.html) to include ALL blog posts
organized by service category, using collapsible sections.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent

# Blog posts organized by category (service)
BLOG_CATEGORIES = {
    "Deck Building & Maintenance": [
        ("/blog/deck-maintenance-tips/", "Deck Maintenance Tips for Canadian Winters"),
        ("/3-easy-ways-to-care-for-your-deck-so-it-always-looks-great/", "3 Easy Ways to Care for Your Deck"),
        ("/amazing-decks-in-richmond-hill/", "Amazing Decks in Richmond Hill"),
        ("/best-decking-materials-outdoor-decks/", "Best Decking Materials for Outdoor Decks"),
        ("/building-a-deck-in-aurora/", "Building a Deck in Aurora"),
        ("/building-a-small-deck-in-toronto/", "Building a Small Deck in Toronto"),
        ("/choosing-perfect-deck-contractor/", "Choosing the Perfect Deck Contractor"),
        ("/choose-right-decking-material-landscape/", "Choose the Right Decking Material for Your Landscape"),
        ("/custom-decks-richmond-hill/", "Custom Decks in Richmond Hill"),
        ("/deck-maintenance-in-markhams-variable-climate/", "Deck Maintenance in Markham's Variable Climate"),
        ("/essential-deck-maintenance-for-newmarket-homes/", "Essential Deck Maintenance for Newmarket Homes"),
        ("/expert-deck-building-in-aurora/", "Expert Deck Building in Aurora"),
        ("/expert-richmond-hill-deck-builders-quality-decks/", "Expert Richmond Hill Deck Builders: Quality Decks"),
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
        ("/privacy-screen-deck/", "Privacy Screen for Decks"),
        ("/privacy-screen-installation-in-north-york/", "Privacy Screen Installation in North York"),
        ("/exploring-the-benefits-of-outdoor-living-spaces-enhancing-your-home-and-lifestyle/", "Benefits of Outdoor Living Spaces"),
    ],
    "Basement Renovation": [
        ("/blog/basement-renovation-ideas/", "Creative Basement Renovation Ideas"),
        ("/a-look-at-tips-to-remodel-your-basement-with-low-ceiling/", "Tips to Remodel a Basement with Low Ceilings"),
        ("/affordable-basement-renovation-toronto-guide/", "Affordable Basement Renovation in Toronto: A Practical Guide"),
        ("/basement-renovation-costs-toronto-guide/", "Basement Renovation Costs in Toronto: Complete Guide"),
        ("/expensive-parts-basement-renovation/", "The Most Expensive Parts of a Basement Renovation"),
        ("/is-it-really-worth-it-to-renovate-a-basement/", "Is It Really Worth It to Renovate a Basement?"),
        ("/navigating-basement-renovation-in-toronto-top-contractors-to-consider/", "Navigating Basement Renovation: Choosing the Right Contractor"),
        ("/reasons-to-hire-amaximum-construction-for-basement-renovation-services/", "5 Reasons to Choose aMaximum for Basement Renovation"),
        ("/1-basement-renovation-near-me/", "Basement Renovation Near Me"),
        ("/best-basement-renovation-service-in-aurora/", "Best Basement Renovation Service in Aurora"),
        ("/best-basement-renovation-service-in-newmarket/", "Best Basement Renovation Service in Newmarket"),
        ("/best-basement-renovation-service-richmond-hill/", "Best Basement Renovation Service in Richmond Hill"),
    ],
    "Bathroom Renovation": [
        ("/blog/bathroom-renovation-guide/", "Complete Bathroom Renovation Guide"),
        ("/accessorizing-renovated-bathroom-toronto/", "Accessorizing Your Renovated Bathroom in Toronto"),
        ("/electing-materials-bathroom-renovation-toronto/", "Selecting Materials for Bathroom Renovation"),
        ("/elegant-bathroom-makeovers-selecting-the-right-renovation-services-in-toronto/", "Elegant Bathroom Makeovers: Selecting the Right Services"),
        ("/interior-bathroom-renovation-toronto/", "Interior Bathroom Renovation in Toronto"),
        ("/navigating-permits-regulations-bathroom-renovation-toronto/", "Navigating Permits & Regulations for Bathroom Renovation"),
        ("/basement-and-bathroom-renovation-in-north-york/", "Basement & Bathroom Renovation in North York"),
        ("/basement-bathroom-renovation-richmond-hill/", "Basement & Bathroom Renovation in Richmond Hill"),
    ],
    "Fence Installation": [
        ("/blog/fence-installation-options/", "Fence Installation: Wood, Vinyl & Metal Compared"),
        ("/choosing-the-best-fence-contractor/", "Choosing the Best Fence Contractor"),
        ("/searching-for-the-top-rated-fence-contractors/", "Searching for Top-Rated Fence Contractors"),
        ("/torontos-top-rated-fence-contractors-a-comprehensive-comparison/", "Toronto's Top-Rated Fence Contractors: A Comparison"),
        ("/ultimate-guide-finding-best-fence-contractor/", "Ultimate Guide to Finding the Best Fence Contractor"),
    ],
    "Handyman & Contractor Services": [
        ("/blog/contractor-selection-guide/", "How to Choose the Right Construction Contractor"),
        ("/a-review-of-the-7-best-handyman-services-in-toronto-2023/", "Review of 7 Best Handyman Services in Toronto"),
        ("/advantages-of-hiring-a-handyman/", "Advantages of Hiring a Handyman"),
        ("/avoid-handyman-scams/", "How to Avoid Handyman Scams"),
        ("/handyman-charges/", "Handyman Charges: What to Expect"),
        ("/rate-for-a-handyman/", "Rate for a Handyman in Toronto"),
        ("/selecting-top-notch-handyman-and-contractor-services/", "Selecting Top-Notch Handyman Services"),
        ("/handyman-drywall-repair/", "Handyman Drywall Repair"),
        ("/handyman-furniture-assembly/", "Handyman Furniture Assembly"),
        ("/expert-insights-crafting-excellence-with-torontos-general-contracting-services/", "Expert Insights: Toronto's General Contracting"),
        ("/avoiding-general-contractor-scams/", "Avoiding General Contractor Scams"),
        ("/scammer-in-contractors-industry-toronto/", "How to Spot Contractor Scams in Toronto"),
    ],
    "Home Renovation & General": [
        ("/affordable-home-renovation-tips-toronto/", "Affordable Home Renovation Tips for Toronto"),
        ("/transforming-spaces-your-trusted-partners-for-home-renovation-in-toronto/", "Transforming Spaces: Home Renovation in Toronto"),
        ("/construction-project-in-the-winter/", "Can You Do a Construction Project in Winter?"),
        ("/contractor-not-warranty/", "When Your Contractor Doesn't Honour Warranty"),
        ("/contractor-warranty-client-materials-guide/", "Contractor Warranty with Client Materials"),
        ("/effective-communication/", "Effective Communication with Your Contractor"),
        ("/expert-tips/", "Expert Tips for a Successful Renovation"),
        ("/first-steps-renovation-permits/", "First Steps: Renovation Permits in Ontario"),
        ("/installation-timelines/", "Renovation Timelines: What to Expect"),
        ("/legal-considerations-renovating/", "Legal Considerations When Renovating"),
        ("/material-costs-in-billing-explained/", "Material Costs in Billing Explained"),
        ("/supply-my-own-materials/", "Should You Supply Your Own Materials?"),
        ("/understanding-additional-service-costs/", "Understanding Additional Service Costs"),
        ("/small-contractors-in-toronto/", "Small Contractors in Toronto"),
        ("/top-affordable-small-contractors-in-toronto/", "Top Affordable Small Contractors in Toronto"),
        ("/trusted-small-contractors-toronto/", "Trusted Small Contractors in Toronto"),
    ],
    "Demolition & Excavation": [
        ("/expert-demolition-services-a-maximum-construction/", "Expert Demolition Services by aMaximum"),
        ("/professional-demolition-services/", "Professional Demolition Services"),
        ("/backyard-demolition-services-landscaper/", "Backyard Demolition & Landscaping Services"),
    ],
    "Landscaping & Outdoor": [
        ("/5-types-of-landscaping-features-you-can-find-in-toronto/", "5 Types of Landscaping Features in Toronto"),
        ("/backyard-oasis-in-richmond-hill/", "Backyard Oasis in Richmond Hill"),
        ("/benefits-of-interlocking-pavers-in-toronto/", "Benefits of Interlocking Pavers in Toronto"),
    ],
    "Christmas Lights": [
        ("/bright-ideas-christmas-light-displays/", "Bright Ideas for Christmas Light Displays"),
        ("/how-to-avoid-injury-while-hanging-christmas-lights/", "How to Avoid Injury Hanging Christmas Lights"),
        ("/professional-christmas-lights-installer-aurora/", "Professional Christmas Lights Installer in Aurora"),
    ],
    "Carpentry": [
        ("/blog-carpenter-services-toronto-gta/", "Carpenter Services in Toronto & GTA"),
    ],
    "Plumbing & Electrical": [
        ("/blog/plumbing-emergency-guide/", "Plumbing Emergency Guide: What to Do First"),
    ],
}


def build_all_articles_section():
    """Build HTML for the 'All Articles by Service' section."""
    lines = []
    lines.append('    <!-- ALL ARTICLES BY SERVICE -->')
    lines.append('    <section class="blog-all-articles" id="all-articles">')
    lines.append('      <div class="blog-section-label">')
    lines.append('        <h2>All Articles by Service</h2>')
    lines.append('      </div>')
    lines.append('      <p style="margin-bottom:24px;">Browse our complete library of guides, tips, and expert advice — organized by service type.</p>')
    lines.append('')

    for category, posts in BLOG_CATEGORIES.items():
        safe_id = category.lower().replace(" ", "-").replace("&", "and").replace(",", "")
        lines.append(f'      <details class="blog-category-group" id="cat-{safe_id}" open>')
        lines.append(f'        <summary class="blog-category-header">')
        lines.append(f'          <h3>{category} <span class="blog-count">({len(posts)} articles)</span></h3>')
        lines.append(f'        </summary>')
        lines.append(f'        <ul class="blog-article-list">')
        for url, title in posts:
            lines.append(f'          <li><a href="{url}">{title}</a></li>')
        lines.append(f'        </ul>')
        lines.append(f'      </details>')
        lines.append('')

    lines.append('    </section>')
    return "\n".join(lines)


def main():
    blog_path = ROOT / "blog" / "index.html"
    html = blog_path.read_text(encoding="utf-8")

    new_section = build_all_articles_section()

    # Insert after the "Browse by Category" section (blog-cats-section), before </div></main>
    # Find the end of blog-cats-section
    pattern = re.compile(r'(</section>\s*)(</div>\s*</main>)', re.DOTALL)
    match = pattern.search(html)
    if match:
        # Find the LAST </section> before </div></main>
        # We need to insert between the cats section closing and the main closing
        insert_pos = html.rfind('</section>', 0, html.find('</main>'))
        if insert_pos != -1:
            insert_pos = html.find('\n', insert_pos) + 1
            html = html[:insert_pos] + "\n" + new_section + "\n\n" + html[insert_pos:]
            blog_path.write_text(html, encoding="utf-8")
            total_posts = sum(len(posts) for posts in BLOG_CATEGORIES.values())
            print(f"✅ Updated blog hub page with {len(BLOG_CATEGORIES)} categories, {total_posts} articles total")
        else:
            print("⚠  Could not find insertion point")
    else:
        print("⚠  Could not find pattern in blog/index.html")


if __name__ == "__main__":
    main()
