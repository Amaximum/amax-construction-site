# -*- coding: utf-8 -*-
"""Localize canopy-location FAQs so each city page is unique (visible + schema).

The 5 canopy location pages currently share the hub's generic 'Toronto' FAQ.
This rewrites each page's 5 Q&A with city-specific, locally-relevant content.
Because the visible <details> text and the JSON-LD text are identical strings,
a whole-file replace updates BOTH copies in sync.
"""
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Shared source strings currently on every canopy location page.
OLD = {
    'q1': 'How much does a canopy cost in Toronto?',
    'a1': 'A basic retractable awning starts around $1,500\u2013$3,500. Custom patio canopies range from $5,000\u2013$15,000. Larger pergolas and carports run $10,000\u2013$25,000+. Free quotes available.',
    'q2': 'Do canopies need a permit in Toronto?',
    'a2': "Attached structures over a certain size require a permit. Freestanding shade sails and small awnings often don't. We confirm permit requirements for your specific project.",
    'q3': 'What materials are used for canopies?',
    'a3': "We use aluminum frames (rust-proof), cedar wood, polycarbonate panels, and weather-resistant fabric. All materials are chosen for Toronto's climate.",
    'q4': 'Can a canopy withstand Toronto winters?',
    'a4': 'We recommend removing retractable fabric awnings in winter. Permanent aluminum and polycarbonate canopies are engineered for snow loads to Ontario standards.',
    'q5': 'How long does canopy installation take?',
    'a5': 'Most canopy and awning installations are completed in 1\u20133 days.',
}

CITY = {
'canopy-installation-in-markham': {
    'q1': 'How much does a canopy cost in Markham?',
    'a1': 'In Markham, a basic retractable awning typically runs $1,500\u2013$3,500, while custom patio canopies for the area\u2019s larger detached backyards land between $5,000 and $15,000. Pergolas and carports for double-driveway homes in Cornell or Wismer can reach $10,000\u2013$25,000+. We provide free written quotes.',
    'q2': 'Do I need a permit for a canopy in Markham?',
    'a2': 'The City of Markham Building Standards department requires a permit for attached canopies and carports above a set size, while freestanding shade sails and small awnings usually don\u2019t. We prepare the Markham permit application and drawings for you.',
    'q3': 'What canopy materials hold up best in Markham?',
    'a3': 'For Markham\u2019s humid summers and freeze\u2013thaw winters we use rust-proof aluminum frames, cedar, polycarbonate roofing and marine-grade fabric \u2014 selected to suit local homes from heritage Unionville to newer subdivisions.',
    'q4': 'Can a canopy handle Markham winters and snow load?',
    'a4': 'Yes. Permanent aluminum and polycarbonate canopies we build in Markham are engineered to Ontario snow-load standards for York Region; we recommend retracting fabric awnings before heavy snowfall.',
    'q5': 'How long does canopy installation take in Markham?',
    'a5': 'Most Markham canopy and awning installations are finished in 1\u20133 days once any required permit is approved.',
},
'canopy-installation-in-newmarket': {
    'q1': 'How much does a canopy cost in Newmarket?',
    'a1': 'Newmarket homeowners generally pay $1,500\u2013$3,500 for a retractable awning and $5,000\u2013$15,000 for a custom patio canopy. Larger pergolas or carports for properties near Stonehaven or Summerhill Estates run $10,000\u2013$25,000+. Quotes are free and itemized.',
    'q2': 'Do canopies need a permit in Newmarket?',
    'a2': 'The Town of Newmarket requires a building permit for larger attached structures and carports; small freestanding awnings and shade sails often don\u2019t. We confirm requirements with the Town and manage the paperwork.',
    'q3': "Which canopy materials suit Newmarket's climate?",
    'a3': 'We use rust-proof aluminum, cedar, polycarbonate panels and weather-resistant fabric chosen for Newmarket\u2019s open, exposed lots and York Region freeze\u2013thaw cycles.',
    'q4': 'Will a canopy survive Newmarket winters?',
    'a4': 'Permanent canopies we install in Newmarket meet Ontario snow-load standards. On wind-exposed lots we reinforce anchoring, and we advise removing fabric awnings over winter.',
    'q5': 'How quickly can you install a canopy in Newmarket?',
    'a5': 'Typical Newmarket canopy and awning projects take 1\u20133 days after any required Town permit is issued.',
},
'canopy-installation-in-richmond-hill': {
    'q1': 'How much does a canopy cost in Richmond Hill?',
    'a1': 'In Richmond Hill, retractable awnings start around $1,500\u2013$3,500 and custom patio canopies range $5,000\u2013$15,000. Large pergolas and carports for the area\u2019s estate lots near Oak Ridges can reach $10,000\u2013$25,000+. Free on-site quotes available.',
    'q2': 'Do I need a permit for a canopy in Richmond Hill?',
    'a2': 'The City of Richmond Hill requires permits for attached canopies and carports above a certain size, and properties on the Oak Ridges Moraine may have extra siting rules. We verify this and file the application for you.',
    'q3': 'What materials do you use for Richmond Hill canopies?',
    'a3': 'Rust-proof aluminum frames, cedar, polycarbonate roofing and UV-stable fabric \u2014 matched to Richmond Hill\u2019s mix of mature-tree lots and newer estate homes.',
    'q4': 'Can a canopy withstand Richmond Hill winters?',
    'a4': 'Yes \u2014 permanent aluminum and polycarbonate canopies are engineered to York Region snow-load standards. Fabric awnings should be retracted before heavy snow.',
    'q5': 'How long does canopy installation take in Richmond Hill?',
    'a5': 'Most Richmond Hill installations wrap up in 1\u20133 days once permits are approved.',
},
'canopy-installation-in-vaughan': {
    'q1': 'How much does a canopy cost in Vaughan?',
    'a1': 'Vaughan homeowners in Woodbridge, Maple and Kleinburg typically spend $1,500\u2013$3,500 on a retractable awning and $5,000\u2013$15,000 on a custom patio canopy, with large pergolas and carports at $10,000\u2013$25,000+. All quotes are free.',
    'q2': 'Do canopies need a permit in Vaughan?',
    'a2': 'The City of Vaughan requires a permit for larger attached canopies and carports; lots backing onto TRCA valley lands may need extra approval. We confirm and manage the Vaughan permit process.',
    'q3': 'What canopy materials work best in Vaughan?',
    'a3': 'We use rust-proof aluminum, cedar, polycarbonate and marine-grade fabric suited to Vaughan\u2019s newer large homes and open, sun-exposed yards.',
    'q4': 'Can a canopy handle Vaughan winters?',
    'a4': 'Permanent canopies we build in Vaughan meet Ontario snow-load standards for York Region; retractable fabric awnings are best stored over winter.',
    'q5': 'How long does canopy installation take in Vaughan?',
    'a5': 'Most Vaughan canopy and awning installs are done in 1\u20133 days after permit approval.',
},
'canopy-installation-in-toronto': {
    'q1': 'How much does a canopy cost in Toronto?',
    'a1': "For Toronto's compact semi and detached lots, retractable awnings run $1,500\u2013$3,500 and custom patio canopies $5,000\u2013$15,000. Rear-yard pergolas and carports typically reach $8,000\u2013$22,000+. Free quotes with a fixed price.",
    'q2': 'Do I need a permit for a canopy in Toronto?',
    'a2': 'The City of Toronto requires a permit for attached canopies and carports over a set size, and ravine-protected or heritage properties have added rules. We check zoning and file the Toronto permit for you.',
    'q3': 'What canopy materials suit Toronto homes?',
    'a3': "Rust-proof aluminum, cedar, polycarbonate and weather-resistant fabric \u2014 chosen for Toronto's tight urban lots, downtown wind exposure and freeze\u2013thaw winters.",
    'q4': 'Can a canopy withstand Toronto winters?',
    'a4': 'Permanent aluminum and polycarbonate canopies are engineered to City of Toronto and Ontario snow-load standards. Fabric awnings should be retracted in winter.',
    'q5': 'How long does canopy installation take in Toronto?',
    'a5': 'Most Toronto canopy and awning installations finish in 1\u20133 days once any required permit is issued.',
},
}

def main():
    changed = 0
    for slug, repl in CITY.items():
        p = os.path.join(ROOT, slug, 'index.html')
        if not os.path.exists(p):
            print('MISSING', slug); continue
        raw = open(p, encoding='utf-8').read()
        orig = raw
        for key in ('q1','a1','q2','a2','q3','a3','q4','a4','q5','a5'):
            old = OLD[key]; new = repl[key]
            if old == new:
                continue
            if old not in raw:
                print(f'  !! {slug}: OLD not found for {key}: {old[:40]}')
                continue
            raw = raw.replace(old, new)
        if raw != orig:
            open(p, 'w', encoding='utf-8').write(raw)
            changed += 1
            print('LOCALIZED', slug)
    print(f'\nfiles changed: {changed}')

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
