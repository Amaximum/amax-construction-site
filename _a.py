from PIL import Image
src='img/services/handyman-1.jpg'
im=Image.open(src).convert('RGB')
for w in (800,1200,1600):
    h=int(im.size[1]*w/im.size[0])
    r=im.resize((w,h), Image.LANCZOS)
    r.save(f'img/services/handyman-1-{w}.webp','WEBP',quality=78,method=6)
    r.save(f'img/services/handyman-1-{w}.jpg','JPEG',quality=82,optimize=True,progressive=True)
print('done')
