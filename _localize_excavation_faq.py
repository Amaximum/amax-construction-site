# -*- coding: utf-8 -*-
"""Localize excavation-location FAQs (visible + schema in sync)."""
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

OLD = {
 'q1': 'How much does excavation cost in Toronto?',
 'a1': 'Small excavation projects start around $3,000\u2013$8,000. Foundation digs for additions run $15,000\u2013$35,000. Pool excavation ranges $5,000\u2013$15,000. Free quotes available.',
 'q2': 'Do you call Ontario One Call before digging?',
 'a2': 'Always \u2014 we request utility locates through Ontario One Call (1-800-400-2255) before any excavation. This is required by law and protects against hitting gas, hydro, or water lines.',
 'q3': 'How long does excavation take?',
 'a3': 'A standard foundation dig takes 1\u20133 days. Pool excavation takes 1\u20132 days. Timeline depends on site access and soil conditions.',
 'q4': 'What happens to the excavated soil?',
 'a4': 'Clean fill can be repurposed on-site for grading or hauled away. Contaminated soil requires special disposal. We assess and advise.',
 'q5': 'Do you do underpinning?',
 'a5': "Yes \u2014 we provide basement lowering through underpinning and bench-footing. This requires a structural engineer's drawings, which we arrange.",
}

CITY = {
'excavation-services-in-markham': {
 'q1': 'How much does excavation cost in Markham?',
 'a1': "In Markham, small excavation jobs start around $3,000\u2013$8,000, foundation digs for home additions run $15,000\u2013$35,000, and pool excavation lands at $5,000\u2013$15,000. Markham\u2019s dense clay soil can affect pricing, so every quote is free and site-specific.",
 'q2': 'Do you call Ontario One Call before digging in Markham?',
 'a2': "Always. Before any Markham excavation we request utility locates through Ontario One Call (1-800-400-2255) \u2014 it\u2019s required by law and protects your property from struck gas, hydro or water lines, which are common under Markham\u2019s established neighbourhoods.",
 'q3': 'How long does excavation take in Markham?',
 'a3': "A standard Markham foundation dig takes 1\u20133 days and pool excavation 1\u20132 days. Heavy clay and tight side-yard access on older Markham lots can add time, which we flag in the quote.",
 'q4': 'What happens to the excavated soil in Markham?',
 'a4': "Clean fill can be regraded on-site or hauled to an approved York Region facility; contaminated soil needs special disposal. We test, assess and advise before we dig.",
 'q5': 'Do you do basement underpinning in Markham?',
 'a5': "Yes \u2014 we lower Markham basements with underpinning and bench-footing. This needs stamped structural engineer\u2019s drawings and a City of Markham permit, both of which we arrange.",
},
'excavation-services-in-newmarket': {
 'q1': 'How much does excavation cost in Newmarket?',
 'a1': "Newmarket excavation typically starts at $3,000\u2013$8,000 for small jobs, $15,000\u2013$35,000 for addition foundations, and $5,000\u2013$15,000 for pools. Low-lying lots near the Holland River may need extra dewatering, which we price up front for free.",
 'q2': 'Do you call Ontario One Call before digging in Newmarket?',
 'a2': "Yes, every time. We book utility locates through Ontario One Call (1-800-400-2255) before excavating in Newmarket \u2014 a legal requirement that prevents strikes on buried gas, hydro and water services.",
 'q3': 'How long does excavation take in Newmarket?',
 'a3': "Most Newmarket foundation digs take 1\u20133 days and pool excavation 1\u20132 days. High water tables on some Newmarket properties can extend the schedule; we account for that in advance.",
 'q4': 'What happens to the excavated soil in Newmarket?',
 'a4': "Clean fill is reused on-site for grading or trucked to an approved facility, while contaminated material is disposed of under regulation. We assess Newmarket soil conditions before starting.",
 'q5': 'Do you do underpinning in Newmarket?',
 'a5': "Yes \u2014 we offer basement lowering by underpinning and bench-footing in Newmarket, arranged with a structural engineer\u2019s drawings and Town of Newmarket permits.",
},
'excavation-services-in-richmond-hill': {
 'q1': 'How much does excavation cost in Richmond Hill?',
 'a1': "In Richmond Hill, small excavation runs $3,000\u2013$8,000, addition foundations $15,000\u2013$35,000, and pool digs $5,000\u2013$15,000. Properties on the Oak Ridges Moraine can involve sandy soil and groundwater, so quotes are free and site-specific.",
 'q2': 'Do you call Ontario One Call before digging in Richmond Hill?',
 'a2': "Always \u2014 Richmond Hill excavation begins only after utility locates through Ontario One Call (1-800-400-2255). It\u2019s the law and it protects against hitting gas, hydro or water lines on your lot.",
 'q3': 'How long does excavation take in Richmond Hill?',
 'a3': "A Richmond Hill foundation dig usually takes 1\u20133 days and pool excavation 1\u20132 days. Sloped estate lots and moraine soils near Oak Ridges can affect timing, which we detail in your quote.",
 'q4': 'What happens to the excavated soil in Richmond Hill?',
 'a4': "Clean fill can be regraded on-site or hauled away; contaminated or moraine-sensitive soil requires controlled disposal. We test and advise before any Richmond Hill dig.",
 'q5': 'Do you do basement underpinning in Richmond Hill?',
 'a5': "Yes \u2014 we lower basements via underpinning and bench-footing in Richmond Hill, using stamped engineer\u2019s drawings and City of Richmond Hill permits that we manage for you.",
},
'excavation-services-in-vaughan': {
 'q1': 'How much does excavation cost in Vaughan?',
 'a1': "Vaughan excavation starts around $3,000\u2013$8,000 for small jobs, $15,000\u2013$35,000 for addition foundations, and $5,000\u2013$15,000 for pools. Lots in Woodbridge, Maple or Kleinburg near valley lands may need extra shoring, quoted free.",
 'q2': 'Do you call Ontario One Call before digging in Vaughan?',
 'a2': "Yes \u2014 before excavating anywhere in Vaughan we request Ontario One Call locates (1-800-400-2255). It\u2019s legally required and prevents damage to buried gas, hydro and water infrastructure.",
 'q3': 'How long does excavation take in Vaughan?',
 'a3': "Standard Vaughan foundation digs take 1\u20133 days and pools 1\u20132 days. Properties backing onto TRCA valleys or with limited access can take longer, which we outline in the quote.",
 'q4': 'What happens to the excavated soil in Vaughan?',
 'a4': "Clean fill is reused on-site or hauled to an approved facility; contaminated soil is disposed of under regulation. We assess Vaughan sites, including valley-land setbacks, before digging.",
 'q5': 'Do you do underpinning in Vaughan?',
 'a5': "Yes \u2014 we provide basement lowering by underpinning and bench-footing in Vaughan, arranged with structural engineer\u2019s drawings and City of Vaughan permits.",
},
'excavation-services-in-toronto': {
 'q1': 'How much does excavation cost in Toronto?',
 'a1': "For Toronto\u2019s tight urban lots, small excavation runs $3,000\u2013$8,000, addition foundations $15,000\u2013$35,000, and pool digs $5,000\u2013$15,000. Restricted access often calls for compact excavators, which we factor into a free quote.",
 'q2': 'Do you call Ontario One Call before digging in Toronto?',
 'a2': "Always \u2014 Toronto excavation starts only after utility locates through Ontario One Call (1-800-400-2255). It\u2019s mandatory and essential in Toronto\u2019s dense grid of gas, hydro and water services.",
 'q3': 'How long does excavation take in Toronto?',
 'a3': "A Toronto foundation dig typically takes 1\u20133 days and pool excavation 1\u20132 days. Laneway access, ravine bylaws and neighbouring structures can affect the schedule, which we plan for.",
 'q4': 'What happens to the excavated soil in Toronto?',
 'a4': "Clean fill can be regraded on-site or hauled to an approved facility; Toronto\u2019s excess-soil rules require tracking and, for contaminated soil, controlled disposal. We handle assessment and paperwork.",
 'q5': 'Do you do basement underpinning in Toronto?',
 'a5': "Yes \u2014 basement lowering by underpinning and bench-footing is one of our most requested Toronto services, completed with stamped engineer\u2019s drawings and City of Toronto permits we arrange.",
},
}

def main():
    changed = 0
    for slug, repl in CITY.items():
        p = os.path.join(ROOT, slug, 'index.html')
        if not os.path.exists(p):
            print('MISSING', slug); continue
        raw = open(p, encoding='utf-8').read(); orig = raw
        for key in ('q1','a1','q2','a2','q3','a3','q4','a4','q5','a5'):
            old = OLD[key]; new = repl[key]
            if old == new: continue
            if old not in raw:
                print(f'  !! {slug}: OLD not found {key}: {old[:45]}'); continue
            raw = raw.replace(old, new)
        if raw != orig:
            open(p, 'w', encoding='utf-8').write(raw); changed += 1
            print('LOCALIZED', slug)
    print(f'\nfiles changed: {changed}')

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
