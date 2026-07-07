# -*- coding: utf-8 -*-
"""Localize painting-location FAQs (visible + schema in sync)."""
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))

OLD = {
 'q1': 'How much does interior painting cost in Toronto?',
 'a1': 'A standard bedroom costs $300\u2013$500 to paint. A full home interior (1,500 sq ft) runs $3,000\u2013$6,000. We provide room-by-room quotes so you know exactly what you are paying.',
 'q2': 'How many coats of paint do you apply?',
 'a2': 'We apply primer (on bare or stained surfaces) plus two finish coats minimum. This gives the best coverage and durability.',
 'q3': 'What paint brands do you use?',
 'a3': 'We use Benjamin Moore and Sherwin-Williams \u2014 premium paints with excellent coverage and durability. You can also supply your own paint.',
 'q4': 'How long does interior painting take?',
 'a4': 'A single room takes 1 day. A full home interior typically takes 3\u20137 business days depending on square footage and complexity.',
 'q5': 'Do you move furniture?',
 'a5': 'We move light furniture and protect everything with drop cloths. We recommend you remove fragile or valuable items before we start.',
}

CITY = {
'painting-services-in-markham': {
 'q1': 'How much does interior painting cost in Markham?',
 'a1': "In Markham, a standard bedroom runs $300\u2013$500 to paint and a full 1,500 sq ft home interior $3,000\u2013$6,000. Larger detached homes in Cornell, Wismer or Berczy often sit at the higher end. We give room-by-room quotes so you know exactly what you are paying.",
 'q2': 'How many coats of paint do you apply on Markham homes?',
 'a2': "We apply primer on bare, patched or stained surfaces plus a minimum of two finish coats \u2014 ideal for the drywall in Markham\u2019s newer subdivisions and the plaster in older Unionville homes.",
 'q3': 'What paint brands do you use in Markham?',
 'a3': "We use premium Benjamin Moore and Sherwin-Williams paints for lasting coverage in Markham homes, and you\u2019re welcome to supply your own.",
 'q4': 'How long does interior painting take in Markham?',
 'a4': "A single Markham room takes about 1 day; a full home interior runs 3\u20137 business days depending on square footage \u2014 larger Markham detached homes can take longer.",
 'q5': 'Do you move furniture when painting in Markham?',
 'a5': "Yes \u2014 we move light furniture and cover everything with drop cloths in your Markham home. We ask that you remove fragile or valuable items before we begin.",
},
'painting-services-in-newmarket': {
 'q1': 'How much does interior painting cost in Newmarket?',
 'a1': "Newmarket interior painting starts around $300\u2013$500 per bedroom, with a full 1,500 sq ft home at $3,000\u2013$6,000. Heritage homes near Main Street may need extra prep, which we itemize in a room-by-room quote.",
 'q2': 'How many coats of paint do you apply?',
 'a2': "We prime bare, repaired or stained surfaces and apply at least two finish coats \u2014 important for the older plaster walls found in many Newmarket homes.",
 'q3': 'What paint brands do you use in Newmarket?',
 'a3': "We use Benjamin Moore and Sherwin-Williams premium paints for durable results in Newmarket, or we\u2019ll happily work with paint you supply.",
 'q4': 'How long does interior painting take in Newmarket?',
 'a4': "A single room takes about 1 day and a full Newmarket home interior 3\u20137 business days, depending on size and the amount of prep an older home needs.",
 'q5': 'Do you move furniture?',
 'a5': "We shift light furniture and protect your Newmarket home with drop cloths. Please remove fragile or valuable pieces before we start.",
},
'painting-services-in-richmond-hill': {
 'q1': 'How much does interior painting cost in Richmond Hill?',
 'a1': "In Richmond Hill, a bedroom runs $300\u2013$500 and a full 1,500 sq ft interior $3,000\u2013$6,000. Estate homes with high ceilings and open foyers near Oak Ridges sit higher; every Richmond Hill quote is room-by-room.",
 'q2': 'How many coats of paint do you apply?',
 'a2': "We apply primer on bare or stained areas plus a minimum of two finish coats \u2014 essential for the tall, open walls common in Richmond Hill estate homes.",
 'q3': 'What paint brands do you use in Richmond Hill?',
 'a3': "We paint Richmond Hill homes with premium Benjamin Moore and Sherwin-Williams products, and you may supply your own paint if you prefer.",
 'q4': 'How long does interior painting take in Richmond Hill?',
 'a4': "One room takes about a day; a full Richmond Hill home interior takes 3\u20137 business days, and high-ceiling estate rooms may add time for staging and access.",
 'q5': 'Do you move furniture?',
 'a5': "Yes \u2014 we move light furniture and cover surfaces with drop cloths in your Richmond Hill home, and recommend removing fragile or valuable items first.",
},
'painting-services-in-vaughan': {
 'q1': 'How much does interior painting cost in Vaughan?',
 'a1': "Vaughan interior painting is about $300\u2013$500 per bedroom and $3,000\u2013$6,000 for a full 1,500 sq ft home. Larger new builds in Woodbridge, Maple and Kleinburg trend higher; we provide detailed room-by-room quotes.",
 'q2': 'How many coats of paint do you apply?',
 'a2': "We prime bare, patched or stained surfaces and apply at least two finish coats \u2014 the right approach for the smooth drywall in Vaughan\u2019s newer homes.",
 'q3': 'What paint brands do you use in Vaughan?',
 'a3': "We use Benjamin Moore and Sherwin-Williams premium paints for Vaughan homes, and you\u2019re welcome to supply your own.",
 'q4': 'How long does interior painting take in Vaughan?',
 'a4': "A single room takes around 1 day; a full Vaughan home interior takes 3\u20137 business days, with large Woodbridge and Kleinburg homes at the upper end.",
 'q5': 'Do you move furniture?',
 'a5': "We move light furniture and protect your Vaughan home with drop cloths. We ask that fragile or valuable items be removed before we start.",
},
'painting-services-in-toronto': {
 'q1': 'How much does interior painting cost in Toronto?',
 'a1': "In Toronto, a standard bedroom costs $300\u2013$500 to paint and a full 1,500 sq ft home $3,000\u2013$6,000. Older plaster walls in Victorians and semis may need extra prep; we quote room by room so pricing is clear.",
 'q2': 'How many coats of paint do you apply?',
 'a2': "We apply primer on bare, patched or stained surfaces plus two finish coats minimum \u2014 especially important for Toronto\u2019s older plaster and previously painted walls.",
 'q3': 'What paint brands do you use in Toronto?',
 'a3': "We use premium Benjamin Moore and Sherwin-Williams paints across Toronto, including low-VOC options for condos, and you can supply your own if you prefer.",
 'q4': 'How long does interior painting take in Toronto?',
 'a4': "A single room takes about 1 day; a full Toronto home interior takes 3\u20137 business days depending on size, prep and access in tighter downtown properties.",
 'q5': 'Do you move furniture?',
 'a5': "Yes \u2014 we move light furniture and cover everything with drop cloths in your Toronto home or condo, and recommend removing fragile or valuable items beforehand.",
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
