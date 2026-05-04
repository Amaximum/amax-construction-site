import re
p=open('handyman-service-in-richmond-hill/index.html',encoding='utf-8').read()
body=re.search(r'<body[^>]*>(.*?)</body>',p,re.S).group(1)
body2=re.sub(r'<(script|style|footer)[^>]*>.*?</\1>',' ',body,flags=re.S)
txt=re.sub(r'<[^>]+>',' ',body2)
words=re.findall(r"[A-Za-z']+",txt)
print('body words:',len(words))
strongs=re.findall(r'<(strong|b)[^>]*>(.*?)</\1>',body2,re.S)
sw=sum(len(re.findall(r"[A-Za-z']+",re.sub(r'<[^>]+>',' ',s[1]))) for s in strongs)
print('strong words:',sw,'elements:',len(strongs))
for ph in ['richmond hill','handyman services','richmond hill handyman','richmond hill handyman services','local handyman services','professional handyman services','local handyman','residential handyman services','home repair services','handyman service','home improvement','home maintenance','professional team','to do list','electrical work','customer satisfaction']:
    print(f'{ph:35} {len(re.findall(ph,txt,re.I))}')
