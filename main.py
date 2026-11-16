"""Abyssal Ascension: a deterministic, entirely procedural light painting."""
import os
import math
import random
import struct
import zlib

N = 640
S = N / 896.0
rng = random.Random(20261116)
pixels = [0.0] * (N * N * 3)


def add(x, y, color, amount=1.0):
    if 0 <= x < N and 0 <= y < N:
        k = (y * N + x) * 3
        pixels[k] += color[0] * amount
        pixels[k + 1] += color[1] * amount
        pixels[k + 2] += color[2] * amount


def glow(x, y, radius, color, strength=1.0):
    x, y, radius = x * S, y * S, radius * S
    for j in range(max(0, int(y-radius)), min(N, int(y+radius)+1)):
        dy = (j-y) / radius
        for i in range(max(0, int(x-radius)), min(N, int(x+radius)+1)):
            d = ((i-x)/radius)**2 + dy*dy
            if d < 1:
                add(i, j, color, strength * (math.exp(-5*d)-math.exp(-5)))


def polygon(points, color):
    pts = [(x*S, y*S) for x,y in points]
    for y in range(max(0,int(min(p[1] for p in pts))), min(N,int(max(p[1] for p in pts))+1)):
        crossings = []
        for a,b in zip(pts, pts[1:]+pts[:1]):
            if (a[1] <= y+.5 < b[1]) or (b[1] <= y+.5 < a[1]):
                crossings.append(a[0]+(y+.5-a[1])*(b[0]-a[0])/(b[1]-a[1]))
        crossings.sort()
        for a,b in zip(crossings[::2],crossings[1::2]):
            for x in range(max(0,int(a)),min(N,int(b)+1)):
                k=(y*N+x)*3
                pixels[k:k+3]=color


def curve(points, width, color, strength=1.0):
    for a,b in zip(points,points[1:]):
        distance=math.hypot(b[0]-a[0],b[1]-a[1])
        steps=max(1,int(distance/max(.8,width*.6)))
        for j in range(steps):
            t=j/steps
            glow(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,width,color,strength)


def world(u,v):
    return 501 + .906*u-.423*v, 292+.423*u+.906*v


def background():
    for y in range(N):
        yy=y/N
        for x in range(N):
            xx=x/N
            cloud=(math.sin(xx*8+yy*5)+math.sin(xx*17-yy*11)*.4+math.sin(xx*33+yy*19)*.15)
            mist=math.exp(-((xx-.32+yy*.18)/.24)**2)*(.5+.16*cloud)
            k=(y*N+x)*3
            pixels[k:k+3]=[.0025+mist*.009,.006+mist*.016+yy*.002,.021+mist*.040]
    for _ in range(470):
        x=rng.uniform(12,884); y=rng.uniform(8,780)
        if rng.random() < (1-y/1050):
            glow(x,y,rng.uniform(1,2.6),(.25,.48,.65),rng.uniform(.3,1.1))
    for x,y in [(119,161),(754,134),(681,66),(812,372)]:
        glow(x,y,9,(.12,.32,.48),.5)
        curve([(x-4,y),(x+4,y)],1.3,(.4,.65,.8),.6)
        curve([(x,y-5),(x,y+5)],1.2,(.4,.65,.8),.6)


def water():
    for _ in range(1250):
        y=rng.uniform(625,895); x=rng.uniform(0,896)
        reflection=math.exp(-((x-(390-(y-650)*.20))/(22+(y-610)*.25))**2)
        c=(.24,.075,.025) if rng.random()<.65 else (.015,.18,.22)
        length=rng.uniform(2,16)*(y/896)
        curve([(x,y),(x+length,y)],rng.uniform(.65,1.4),c,.035+reflection*.30)


def tentacles():
    # Soft, folded feeding arms behind the fine luminous filaments.
    for j in range(7):
        u=-145+j*45
        pts=[]
        for i in range(100):
            t=i/99
            v=30+410*t
            uu=u-115*t+math.sin(t*10+j)* (12+23*t)
            pts.append(world(uu,v))
        curve(pts,12,(.05,.16,.18),.12)
        for offset in [-5,4]:
            edge=[(x+offset*math.sin(i*.16+j),y) for i,(x,y) in enumerate(pts)]
            curve(edge,2.4,(.16,.36,.34),.18)
    for j in range(48):
        u=rng.uniform(-190,190)
        length=rng.uniform(300,565)*(1-.16*abs(u)/190)
        phase=rng.uniform(0,6.28)
        pts=[]
        for i in range(115):
            t=i/114
            uu=u-125*t-40*t*t+math.sin(t*11+phase)*(6+24*t)+math.sin(t*23+phase)*7*t
            pts.append(world(uu,27+length*t))
        warm=j%4!=0
        c=(.8,.18,.035) if warm else (.025,.42,.58)
        curve(pts,5.0,c,.095)
        curve(pts,1.65,(1,.43,.13) if warm else (.13,.8,.88),.56)
    for _ in range(260):
        v=rng.uniform(50,565); u=rng.gauss(-v*.24,112)
        x,y=world(u,v)
        glow(x,y,rng.uniform(1,3.5),(.9,.32,.06) if rng.random()<.7 else (.04,.55,.7),rng.uniform(.2,.9))


def dome():
    cx,cy=world(0,-40)
    glow(cx,cy,315,(.7,.10,.025),.26)
    # Tilted cap: softly modelled tissue with irregular subsurface light.
    for y in range(max(0,int(45*S)),int(450*S)):
        for x in range(int(240*S),min(N,int(770*S))):
            dx=x/S-501; dy=y/S-292
            u=.906*dx+.423*dy; v=-.423*dx+.906*dy
            q=u/223
            if abs(q)>=1: continue
            top=-157*math.sqrt(1-q*q)
            rim=25+15*(1-q*q)
            if top <= v <= rim:
                depth=(v-top)/(rim-top)
                crown=math.exp(-((u+28)/126)**2-((v+69)/77)**2)
                organic=math.sin(u*.027+v*.039+1.3*math.sin(u*.018))+ .4*math.sin(v*.09-u*.013)
                band=math.exp(-((depth-.70-.035*math.sin(u*.028))/.038)**2)
                edge=min(1,(v-top)/3,(rim-v)/2,(223-abs(u))/3)
                light=.60+.11*organic-.19*band
                c=(light*1.05+crown*1.9,light*.18+crown*1.17,light*.035+crown*.35)
                k=(y*N+x)*3
                for channel in range(3):
                    pixels[k+channel]=pixels[k+channel]*(1-edge)+c[channel]*edge
    toppts=[world(223*math.cos(t),-157*math.sin(t)) for t in [math.pi*i/180 for i in range(181)]]
    rimpts=[world(u,25+15*(1-(u/223)**2)+2*math.sin(u*.075)) for u in range(-223,224,2)]
    curve(toppts,7,(.9,.29,.07),.20)
    curve(toppts,1.8,(1,.64,.28),.7)
    curve(rimpts,10,(.015,.5,.65),.25)
    curve(rimpts,2.5,(.16,.9,1),.95)
    inner=[world(u,14+12*(1-(u/215)**2)) for u in range(-210,211,3)]
    curve(inner,2.1,(1,.36,.055),.65)
    for _ in range(65):
        u=rng.uniform(-225,225); v=rng.uniform(-220,-153)
        x,y=world(u,v)
        glow(x,y,rng.uniform(1,3),(.8,.48,.17),rng.uniform(.3,1))


def boat():
    glow(113,740,33,(.8,.25,.035),.25)
    polygon([(78,752),(135,752),(125,762),(92,761)],(.002,.005,.009))
    polygon([(104,738),(123,738),(127,752),(100,752)],(.003,.007,.012))
    polygon([(112,715),(114,715),(114,752),(112,752)],(.003,.006,.010))
    curve([(113,718),(94,739)],.8,(.04,.075,.09),.5)
    glow(120,743,7,(1,.35,.04),1.3)
    glow(120,743,2,(1,.8,.35),2)
    for i in range(12):
        y=767+i*4
        x=119+rng.uniform(-5,5)
        curve([(x-3-i*.35,y),(x+3+i*.35,y)],1,(.6,.23,.04),.15*(1-i/14))


def save_png(path):
    raw=bytearray()
    for y in range(896):
        raw.append(0)
        fy=y*(N-1)/895; y0=int(fy); y1=min(N-1,y0+1); ty=fy-y0
        for x in range(896):
            fx=x*(N-1)/895; x0=int(fx); x1=min(N-1,x0+1); tx=fx-x0
            a=(y0*N+x0)*3; b=(y0*N+x1)*3; c=(y1*N+x0)*3; d=(y1*N+x1)*3
            for ch in range(3):
                value=(pixels[a+ch]*(1-tx)+pixels[b+ch]*tx)*(1-ty)+(pixels[c+ch]*(1-tx)+pixels[d+ch]*tx)*ty
                value=1-math.exp(-max(0,value)*1.35)
                raw.append(min(255,int(255*value**.48+.5)))
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',896,896,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    with open(path,'wb') as f:
        f.write(data)


def main():
    background()
    water()
    tentacles()
    dome()
    boat()
    output=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
    os.makedirs(output,exist_ok=True)
    save_png(os.path.join(output,'entry.png'))


if __name__ == '__main__':
    main()
