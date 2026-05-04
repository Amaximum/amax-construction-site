import re
t=open('deck-builder-in-richmond-hill/index.html',encoding='utf-8').read()
body=re.search(r'<body.*?</body>',t,re.S).group(0)
ps=re.findall(r'<p[^>]*>(.*?)</p>',body,re.S)
print('p words:', sum(len(re.sub(r'<[^>]+>',' ',x).split()) for x in ps))
txt=re.sub(r'<[^>]+>',' ',body)
for ph in ['richmond hill deck builder','deck builders','deck builder','decking services','perfect deck','affordable rates','dream deck','new deck','deck building','outdoor space','deck project']:
    print(f'{ph:30}', len(re.findall(ph, txt, re.I)))
