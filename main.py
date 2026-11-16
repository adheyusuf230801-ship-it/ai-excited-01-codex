"""Abyssal Ascension: a deterministic, entirely procedural light painting."""
import os
import math
import random
import struct
import zlib

S = 640
SIZE = 896
rng = random.Random(20261116)
pixels = [0.0] * (S * S * 3)


def add(x, y, color, strength=1.0):
    if 0 <= x < S and 0 <= y < S:
        k = (y * S + x) * 3
        for c in range(3):
            pixels[k + c] += color[c] * strength


def glow(x, y, radius, color, strength=1.0):
    for yy in range(max(0, int(y-radius)), min(S, int(y+radius)+1)):
        for xx in range(max(0, int(x-radius)), min(S, int(x+radius)+1)):
            d = ((xx-x)**2 + (yy-y)**2) / (radius*radius)
            if d < 1:
                add(xx, yy, color, strength * (1-d)**3)


def stroke(a, b, width, color, strength=1.0):
    ax, ay = a
    bx, by = b
    dx, dy = bx-ax, by-ay
    den = dx*dx + dy*dy or 1
    radius = width/2 + 0.7
    for y in range(max(0, int(min(ay, by)-radius)), min(S, int(max(ay, by)+radius)+1)):
        for x in range(max(0, int(min(ax, bx)-radius)), min(S, int(max(ax, bx)+radius)+1)):
            t = max(0, min(1, ((x-ax)*dx + (y-ay)*dy)/den))
            d = math.hypot(x-ax-t*dx, y-ay-t*dy)
            a = min(1, max(0, radius-d))
            if a:
                add(x, y, color, strength*a)


def curve(points, width, color, strength=1.0):
    for a, b in zip(points, points[1:]):
        stroke(a, b, width, color, strength)


def polygon(points, color):
    for y in range(max(0, int(min(p[1] for p in points))), min(S, int(max(p[1] for p in points))+1)):
        hits = []
        for a, b in zip(points, points[1:]+points[:1]):
            if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                hits.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
        hits.sort()
        for a, b in zip(hits[::2], hits[1::2]):
            for x in range(max(0, int(a)), min(S, int(b)+1)):
                k = (y*S+x)*3
                pixels[k:k+3] = color


# Sea and sky share a continuous midnight volume.
for y in range(S):
    for x in range(S):
        mist = (math.sin(x*.012+y*.009)+math.sin(x*.006-y*.019)+2)/4
        cloud = math.exp(-((x-330-y*.15)/230)**2) * mist**3
        k = (y*S+x)*3
        pixels[k:k+3] = [.004+cloud*.009, .009+cloud*.021, .027+cloud*.052]
for _ in range(510):
    x, y = rng.uniform(10, 630), rng.uniform(8, 470)
    r = rng.choice([.65, .8, 1.1, 1.6])
    glow(x, y, r+1, (.25, .48, .65), rng.uniform(.2, .9))

# Tilted coordinates: the crown surges up and right.
def world(u, v):
    return (374 + .91*u - .415*v, 245 + .415*u + .91*v)

orange = (1.0, .21, .035)
cyan = (.045, .72, .95)
glow(397, 200, 220, orange, .20)
glow(417, 173, 140, (1, .38, .08), .13)

# Distant water glints and a broken reflected pillar.
for _ in range(1650):
    y = rng.uniform(452, 640)
    center = 310 - (y-452)*.21
    x = rng.gauss(center, 24+(y-452)*.39)
    f = math.exp(-((x-center)/(35+(y-452)*.43))**2)
    color = cyan if rng.random() < .38 else (1, .30, .075)
    stroke((x,y), (x+rng.uniform(1,10)*(y/640),y), .5, color, rng.uniform(.025,.16)*f)
for _ in range(190):
    x,y = rng.uniform(0,640),rng.uniform(480,640)
    stroke((x,y),(x+rng.uniform(2,12),y),.5,(.035,.16,.22),.22)

# Feeding ribbons, translucent and gently folding in the current.
for n in range(7):
    u0 = -123+n*40
    phase = rng.uniform(0,6)
    points=[]
    for j in range(91):
        t=j/90
        u=u0-100*t+20*math.sin(t*8+phase)*t
        v=17+310*t
        points.append(world(u,v))
    curve(points, 13, (.08,.20,.23), .12)
    curve(points, 5, (.18,.53,.53), .11)
    curve(points, 1, (.55,.64,.43), .25)

# Fine living filaments stream behind the ascent.
for n in range(43):
    u0=rng.uniform(-151,151)
    length=rng.uniform(210,390)*(1-.15*abs(u0)/151)
    phase=rng.uniform(0,6.28)
    points=[]
    for j in range(105):
        t=j/104
        u=u0-118*t+math.sin(t*8+phase)*(7+20*t)+12*math.sin(t*17+phase)*t*t
        v=18+length*t
        points.append(world(u,v))
    col = cyan if n%3 else (1,.39,.12)
    curve(points, 5, col, .035)
    curve(points, .85, col, rng.uniform(.32,.66))
    if n%4==0:
        for j in range(10,100,9):
            x,y=points[j]
            glow(x,y,2.2,(.30,.95,1),.7)

# A volumetric bell: irregular molten tissue inside a clean dome contour.
for y in range(55,360):
    for x in range(188,586):
        dx,dy=x-374,y-245
        u=.91*dx+.415*dy
        v=-.415*dx+.91*dy
        q=u/170
        if abs(q)>=1:
            continue
        top=-139*math.sqrt(1-q*q)
        bottom=15+20*(1-q*q)
        if top <= v <= bottom:
            edge=min(v-top,bottom-v, (170-abs(u))*.8)
            a=min(1,edge/1.8)
            core=math.exp(-((u-15)/88)**2-((v+55)/64)**2)
            tissue=(math.sin(u*.038+v*.041+1.4*math.sin(u*.018)) + math.sin(v*.071-u*.013))/2
            rim=math.exp(-((v-bottom+12)/8)**2)
            dark=.11*math.exp(-((v-top-17-5*math.sin(u*.05))/3)**2)
            c=(.77+.48*core+.055*tissue-dark, .15+.68*core+.035*tissue-rim*.07, .025+.36*core)
            k=(y*S+x)*3
            for ch in range(3):
                pixels[k+ch]=pixels[k+ch]*(1-a)+c[ch]*a

# Scalloped cyan lip and luminous crown edge.
edge=[]
for j in range(181):
    u=-170+340*j/180
    v=15+20*(1-(u/170)**2)+1.4*math.sin(u*.24)
    edge.append(world(u,v))
curve(edge,9,cyan,.10)
curve(edge,2.0,(.13,.94,1),.85)
curve(edge,.65,(.71,1,1),.55)
arch=[world(170*math.cos(t),-139*math.sin(t)) for t in [j*math.pi/160 for j in range(161)]]
curve(arch,6,(1,.36,.06),.11)
curve(arch,1.2,(1,.70,.27),.5)

# Sparse glowing flecks trace the immense animal's wake.
for _ in range(260):
    u=rng.uniform(-215,220)
    v=rng.uniform(-185,390)
    x,y=world(u-0.22*max(v,0),v)
    if 15<x<625 and 10<y<620:
        color = (1,.57,.18) if rng.random()<.5 else (.12,.78,.91)
        glow(x,y,rng.uniform(1,3.4),color,rng.uniform(.25,.9))
for _ in range(25):
    x,y=world(rng.uniform(-90,130),rng.uniform(-205,-150))
    stroke((x,y),(x+2,y-5),.7,(1,.65,.25),.5)

# Tiny fishing boat, readable against the illuminated water.
glow(94,554,22,(1,.40,.08),.18)
polygon([(69,558),(116,558),(107,567),(80,567)],(.002,.004,.009))
polygon([(85,548),(103,548),(107,558),(82,558)],(.003,.006,.012))
stroke((96,523),(96,557),1.4,(.004,.008,.014))
stroke((76,540),(108,540),1,(.005,.01,.016))
stroke((96,524),(109,548),.6,(.025,.04,.05))
glow(106,550,7,(1,.44,.09),.85)
glow(106,550,2.1,(1,.90,.49),1.6)
for j in range(13):
    y=572+j*3
    x=105+rng.uniform(-5,4)
    stroke((x-2-j*.2,y),(x+2+j*.2,y),.6,(1,.44,.10),.15*(1-j/15))


def png_bytes():
    # Bilinear reconstruction and a restrained filmic shoulder.
    lut = [int(255*min(1, max(0, (i/4096)/(1+i/4096*.30)))**.78+.5) for i in range(16385)]
    raw=bytearray()
    for y in range(SIZE):
        raw.append(0)
        fy=y*(S-1)/(SIZE-1)
        iy=int(fy)
        ty=fy-iy
        jy=min(S-1,iy+1)
        for x in range(SIZE):
            fx=x*(S-1)/(SIZE-1)
            ix=int(fx)
            tx=fx-ix
            jx=min(S-1,ix+1)
            a=(iy*S+ix)*3
            b=(iy*S+jx)*3
            c=(jy*S+ix)*3
            d=(jy*S+jx)*3
            for ch in range(3):
                value=(pixels[a+ch]*(1-tx)+pixels[b+ch]*tx)*(1-ty)+(pixels[c+ch]*(1-tx)+pixels[d+ch]*tx)*ty
                raw.append(lut[min(16384,max(0,int(value*4096)))])
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',SIZE,SIZE,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')


if __name__ == '__main__':
    output=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
    os.makedirs(output,exist_ok=True)
    with open(os.path.join(output,'entry.png'),'wb') as handle:
        handle.write(png_bytes())
