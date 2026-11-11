"""Asset pipeline: originals -> optimised WebP renditions, poster frames, favicon, OG image."""
import os, glob, subprocess, shutil
from PIL import Image, ImageOps

SITE='/home/claude/proj/site'
ATT=glob.glob('/mnt/user-data/attachments/*/')[0]
UP='/mnt/user-data/uploads/'

def find(prefix_or_name):
    for d in (ATT,UP):
        for f in glob.glob(d+'*'):
            if os.path.basename(f).endswith(prefix_or_name) or os.path.basename(f).startswith(prefix_or_name):
                return f
    raise FileNotFoundError(prefix_or_name)

def save_webp(im,path,q=80):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    im.save(path,'WEBP',quality=q,method=6)
    return os.path.getsize(path)

def renditions(src,out_dir,slug,widths=(480,960),full=1600):
    """returns dict(sizes=[(w,h,path_rel)], full=(w,h,path), w,h)"""
    im=ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    W,H=im.size
    res={'w':W,'h':H,'thumbs':[]}
    for w in widths:
        if w>=W: continue
        h=round(H*w/W); r=im.resize((w,h),Image.LANCZOS)
        p=f'{out_dir}/{slug}-{w}.webp'; save_webp(r,f'{SITE}/{p}',78)
        res['thumbs'].append((w,h,p))
    fw=min(W,full); fh=round(H*fw/W)
    r=im if fw==W else im.resize((fw,fh),Image.LANCZOS)
    p=f'{out_dir}/{slug}-{fw}.webp'; save_webp(r,f'{SITE}/{p}',82)
    res['thumbs'].append((fw,fh,p)); res['full']=(fw,fh,p)
    return res

def build():
    out={}
    laos=[('seo-planning','7a8eb026'),('seo-team','356b4c61'),('seo-channel','4a36c4f1'),('seo-archive','a86b574a'),
          ('seo-google','04a80c85'),('seo-instagram','64d8118d'),('seo-telegram-vip','6d008117'),('seo-github','91629411')]
    for slug,pre in laos:
        out[slug]=renditions(find(pre),'assets/img/laos',slug)
    ban={'rooster':'81d4938c','jungle':'59834d97','pirate':'4d30fa4d','leprechaun':'309f16ad','western':'83cfc7d1','waterfall':'0f5799df',
         'fortune-god':'612ad1e7','floating-market':'9f852abd','tiger-mouse':'ce693221','penguin':'b29ad586','ganesha':'IMG_9554.JPG',
         'piglet':'IMG_9555.JPG','dragon':'IMG_9556.JPG'}
    for slug,pre in ban.items():
        out['b-'+slug]=renditions(find(pre),'assets/img/albania',slug,widths=(400,))
    out['stay']=renditions(UP+'IMG_7657.jpg','assets/img/albania','stay',widths=(480,960))
    # UI art with alpha
    def trim(path):
        im=Image.open(path).convert('RGBA'); return im.crop(im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox())
    hero=trim(UP+'Design_sem_nome__4_.png')
    save_webp(hero,f'{SITE}/assets/img/ui/hero.webp',92); out['hero']=hero.size
    for k,n in {'home':10,'la':8,'kh':7,'ph':6,'al':5,'am':9}.items():
        im=trim(UP+f'Design_sem_nome__{n}_.png'); im=im.resize((round(im.width*120/im.height),120),Image.LANCZOS)
        save_webp(im,f'{SITE}/assets/img/nav/{k}.webp',90); out['nav-'+k]=im.size
    # coin sprite for click burst (cut from white/checker background)
    import numpy as np
    from PIL import ImageFilter
    im=Image.open(UP+'1794376764095_image.png').convert('RGB'); a=np.asarray(im).astype('int16')
    mn=a.min(2); mx=a.max(2); bg=(mn>=215)&((mx-mn)<=16)
    al=Image.fromarray(np.where(bg,0,255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    c=im.convert('RGBA'); c.putalpha(al); c=c.crop(c.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox())
    c=c.resize((96,round(c.height*96/c.width)),Image.LANCZOS); save_webp(c,f'{SITE}/assets/img/ui/coin.webp',90)
    # video: strip + posters
    shutil.copy('/home/claude/site/coins-4k.mp4',f'{SITE}/assets/video/coins-4k.mp4')
    subprocess.run(['ffmpeg','-y','-v','error','-i',f'{SITE}/assets/video/coins-4k.mp4','-vf','select=eq(n\\,0),scale=1920:160','-frames:v','1','/tmp/poster.png'],check=True)
    save_webp(Image.open('/tmp/poster.png').convert('RGB'),f'{SITE}/assets/video/coins-poster.webp',82)
    # promo video: re-encode lighter + poster
    subprocess.run(['ffmpeg','-y','-v','error','-i',UP+'Design_sem_nome__1_.mp4','-an','-vf','scale=540:-2','-c:v','libx264','-crf','26','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart',f'{SITE}/assets/video/promo.mp4'],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-ss','1','-i',f'{SITE}/assets/video/promo.mp4','-frames:v','1','/tmp/promo.png'],check=True)
    save_webp(Image.open('/tmp/promo.png').convert('RGB'),f'{SITE}/assets/video/promo-poster.webp',80)
    # OG image 1200x630
    ogbg=Image.new('RGB',(1200,630),(74,5,8))
    from PIL import ImageDraw
    d=ImageDraw.Draw(ogbg)
    for y in range(630): d.line([(0,y),(1200,y)],fill=(int(122-60*y/630),int(10-6*y/630),int(20-10*y/630)))
    h=hero.copy(); h.thumbnail((1100,560)); ogbg.paste(h,((1200-h.width)//2,(630-h.height)//2),h)
    ogbg.save(f'{SITE}/assets/og-image.jpg',quality=86)
    # flags
    for c in ('la','al','kh','ph','am','pk','in'):
        shutil.copy(f'/tmp/fl/node_modules/flag-icons/flags/4x3/{c}.svg',f'{SITE}/assets/flags/{c}.svg')
    return out

if __name__=='__main__':
    import json
    info=build()
    json.dump(info,open('/home/claude/proj/assets.json','w'),default=list)
    tot=sum(os.path.getsize(os.path.join(dp,f)) for dp,_,fs in os.walk(SITE) for f in fs)
    print('total bytes',tot)
