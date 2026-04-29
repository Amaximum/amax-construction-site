"""
Create 8 missing booking forms and update BOOK NOW links on service pages.
Uses book-deck.html as template.
"""
from pathlib import Path
import re

root = Path('.')
template = (root / 'book-deck.html').read_text(encoding='utf-8')

FORMS = {
    'book-landscaping.html': {
        'slug': 'landscaping',
        'title': 'Landscaping',
        'subject': 'New Landscaping Booking',
        'h1': 'Book Landscaping Service',
        'h2': 'Schedule Your Landscaping Consultation',
        'desc': 'Schedule a landscaping consultation or send project details. We\'ll confirm scope and the earliest available time.',
        'placeholder': 'Brief description of your landscaping project — lawn area, trees, garden beds, or any specific requirements...',
        'options': [
            'Lawn & Garden Design',
            'Sod Installation',
            'Tree & Shrub Planting',
            'Garden Bed Creation',
            'Yard Cleanup & Maintenance',
        ],
        'service_pages': ['landscaping-services-toronto'],
    },
    'book-contractor.html': {
        'slug': 'contractor',
        'title': 'General Contractor',
        'subject': 'New General Contractor Booking',
        'h1': 'Book General Contractor',
        'h2': 'Schedule Your Project Consultation',
        'desc': 'Schedule a consultation or send project details. We\'ll confirm scope and the earliest available time.',
        'placeholder': 'Brief description of your project — renovation type, scope, timeline, or any specific requirements...',
        'options': [
            'Full Home Renovation',
            'Home Addition & Extension',
            'Permit Management & Coordination',
            'Project Management',
            'Structural Work',
        ],
        'service_pages': ['general-contractor-in-toronto'],
    },
    'book-electrical.html': {
        'slug': 'electrical',
        'title': 'Electrical',
        'subject': 'New Electrical Booking',
        'h1': 'Book Electrical Service',
        'h2': 'Schedule Your Electrical Consultation',
        'desc': 'Schedule an electrical consultation or send job details. We\'ll confirm scope and the earliest available time.',
        'placeholder': 'Brief description of your electrical project — panel, outlets, lighting, wiring, or any specific requirements...',
        'options': [
            'Electrical Panel Upgrade',
            'Outlet & Switch Installation',
            'Lighting Installation',
            'Wiring & Rewiring',
            'EV Charger Installation',
        ],
        'service_pages': ['electrical-handyman-services'],
    },
    'book-painting.html': {
        'slug': 'painting',
        'title': 'Painting',
        'subject': 'New Painting Booking',
        'h1': 'Book Painting Service',
        'h2': 'Schedule Your Painting Consultation',
        'desc': 'Schedule a painting consultation or send project details. We\'ll confirm scope and the earliest available time.',
        'placeholder': 'Brief description of your painting project — rooms, surfaces, colours, or any specific requirements...',
        'options': [
            'Interior Painting',
            'Exterior Painting',
            'Cabinet Painting & Refinishing',
            'Deck Staining & Sealing',
            'Wallpaper Removal & Painting',
        ],
        'service_pages': ['handyman-painting-services'],
    },
    'book-demolition.html': {
        'slug': 'demolition',
        'title': 'Demolition',
        'subject': 'New Demolition Booking',
        'h1': 'Book Demolition Service',
        'h2': 'Schedule Your Demolition Consultation',
        'desc': 'Schedule a demolition consultation or send project details. We\'ll confirm scope and the earliest available time.',
        'placeholder': 'Brief description of your demolition project — structure type, size, access, or any specific requirements...',
        'options': [
            'Interior Demo (Walls & Floors)',
            'Deck & Structure Demolition',
            'Garage Demolition',
            'Shed & Outbuilding Removal',
            'Concrete Breaking & Removal',
        ],
        'service_pages': ['demolition-services'],
    },
    'book-excavation.html': {
        'slug': 'excavation',
        'title': 'Excavation',
        'subject': 'New Excavation Booking',
        'h1': 'Book Excavation Service',
        'h2': 'Schedule Your Excavation Consultation',
        'desc': 'Schedule an excavation consultation or send project details. We\'ll confirm scope and the earliest available time.',
        'placeholder': 'Brief description of your excavation project — depth, area, soil type, or any specific requirements...',
        'options': [
            'Foundation Excavation',
            'Grading & Leveling',
            'Trenching',
            'Pool Excavation',
            'Basement Lowering (Underpinning)',
        ],
        'service_pages': ['excavation-services'],
    },
    'book-renovation.html': {
        'slug': 'renovation',
        'title': 'Home Renovation',
        'subject': 'New Home Renovation Booking',
        'h1': 'Book Home Renovation',
        'h2': 'Schedule Your Renovation Consultation',
        'desc': 'Schedule a renovation consultation or send project details. We\'ll confirm scope and the earliest available time.',
        'placeholder': 'Brief description of your renovation — rooms, scope, timeline, or any specific requirements...',
        'options': [
            'Kitchen Renovation',
            'Living Area Renovation',
            'Full Home Renovation',
            'Room Addition',
            'Structural Changes & Open Concept',
        ],
        'service_pages': ['home-renovation'],
    },
    'book-christmas.html': {
        'slug': 'christmas',
        'title': 'Christmas Lights',
        'subject': 'New Christmas Lights Booking',
        'h1': 'Book Christmas Lights Installation',
        'h2': 'Schedule Your Christmas Lights Consultation',
        'desc': 'Schedule a Christmas lights consultation or send project details. We\'ll confirm scope and the earliest available time.',
        'placeholder': 'Brief description of your project — property size, lighting style, number of trees, or any specific requirements...',
        'options': [
            'Roofline & Eave Lighting',
            'Tree & Shrub Wrapping',
            'Pathway & Garden Lighting',
            'Commercial Holiday Display',
            'Installation & Takedown Package',
        ],
        'service_pages': ['christmas-lights-installation-toronto-gta'],
    },
}


def build_options(options):
    lines = ['              <option value="">Select service type...</option>']
    for opt in options:
        lines.append(f'              <option value="{opt}">{opt}</option>')
    lines.append('              <option value="Other">Other</option>')
    return '\n'.join(lines)


def make_form(filename, info):
    html = template

    # Title tag
    html = re.sub(r'<title>[^<]+</title>',
                  f'<title>Book {info["title"]} | aMaximum Construction</title>', html)

    # Meta description
    html = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="Book {info["title"].lower()} services with aMaximum Construction in Toronto & GTA. Share your project details and we\'ll confirm the earliest available time.">', html)

    # BOOK NOW nav link
    html = html.replace('href="/book-deck.html">BOOK NOW</a>',
                        f'href="/{filename}">BOOK NOW</a>')

    # Page hero h1 + p
    html = re.sub(r'<h1>Book Deck Project</h1>',
                  f'<h1>{info["h1"]}</h1>', html)
    html = re.sub(r'<p>Schedule a deck consultation.*?</p>',
                  f'<p>{info["desc"]}</p>', html)

    # Section h2
    html = re.sub(r'<h2>Schedule Your Deck Consultation</h2>',
                  f'<h2>{info["h2"]}</h2>', html)

    # Hidden service value + subject
    html = html.replace('name="service" value="deck"',
                        f'name="service" value="{info["slug"]}"')
    html = html.replace('name="_subject" value="New Deck Booking"',
                        f'name="_subject" value="{info["subject"]}"')

    # Service type dropdown options
    old_opts = re.search(
        r'(<select id="serviceType"[^>]*>)(.*?)(</select>)',
        html, re.DOTALL)
    if old_opts:
        html = html[:old_opts.start(2)] + '\n' + build_options(info['options']) + '\n            ' + html[old_opts.end(2):]

    # Textarea placeholder
    html = re.sub(r'placeholder="Brief description of your deck project[^"]*"',
                  f'placeholder="{info["placeholder"]}"', html)

    return html


created = []
for filename, info in FORMS.items():
    path = root / filename
    html = make_form(filename, info)
    path.write_text(html, encoding='utf-8')
    created.append(filename)
    print(f'  CREATED: {filename}')

print(f'\nCreated {len(created)} forms.')

# ── Update BOOK NOW links on service pages ─────────────────────────────────────
print('\nUpdating service page links...')
updated_pages = []

for filename, info in FORMS.items():
    for page_dir in info['service_pages']:
        idx = root / page_dir / 'index.html'
        if not idx.exists():
            print(f'  SKIP (not found): {page_dir}')
            continue
        html = idx.read_text(encoding='utf-8', errors='ignore')
        # Replace any /book-*.html link with the correct one
        new_html = re.sub(r'/book-[a-z]+\.html', f'/{filename}', html)
        if new_html != html:
            idx.write_text(new_html, encoding='utf-8')
            updated_pages.append(page_dir)
            print(f'  UPDATED links: {page_dir} → /{filename}')
        else:
            print(f'  NO CHANGE: {page_dir}')

print(f'\nUpdated {len(updated_pages)} service pages.')
