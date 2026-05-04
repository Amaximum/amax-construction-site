import re
t=open('deck-contractor-aurora/index.html',encoding='utf-8').read()
body=re.search(r'<body.*?</body>',t,re.S).group(0)
ps=re.findall(r'<p[^>]*>(.*?)</p>',body,re.S)
print('p words:', sum(len(re.sub(r'<[^>]+>',' ',x).split()) for x in ps))
txt=re.sub(r'<[^>]+>',' ',body)
phrases=['composite deck','deck design','deck builder','professional deck builder',
         'outdoor living spaces','outdoor living space','outdoor living',
         'professional deck','custom deck','great decks','quality workmanship',
         'unique features','cozy spot','weather damage','fully grasp',
         'affordable option','highly durable','greatest satisfaction',
         'living space','wide range','years of experience',
         'deck contractors','deck building','final inspection','deck builders']
for p in phrases:
    print(f'{p:30}', len(re.findall(p,txt,re.I)))
