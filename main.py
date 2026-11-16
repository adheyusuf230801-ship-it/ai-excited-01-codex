import os, math, random, struct, zlib

W=H=768
pix=[0.0]*(W*H*3)
def put(x,y,c,a=1.0):
    if 0<=x<W and 0<=y<H:
        i=(y*W+x)*3
        pix[i]=min(1,pix[i]+c[0]*a); pix[i+1]=min(1,pix[i+1]+c[1]*a); pix[i+2]=min(1,pix[i+2]+c[2]*a)
def glow(cx,cy,r,col,pow=2.0):
    x0=max(0,int(cx-r)); x1=min(W-1,int(cx+r)); y0=max(0,int(cy-r)); y1=min(H-1,int(cy+r))
    rr=1.0/r
    for y in range(y0,y1+1):
      dy=(y-cy)*rr
      for x in range(x0,x1+1):
        d=math.hypot((x-cx)*rr,dy)
        if d<1: put(x,y,col,(1-d)**pow)
def line(x0,y0,x1,y1,width,col,a=1):
    r=width/2; xmin=max(0,int(min(x0,x1)-r)); xmax=min(W-1,int(max(x0,x1)+r)); ymin=max(0,int(min(y0,y1)-r)); ymax=min(H-1,int(max(y0,y1)+r))
    dx=x1-x0; dy=y1-y0; den=dx*dx+dy*dy or 1
    for y in range(ymin,ymax+1):
      for x in range(xmin,xmax+1):
        t=max(0,min(1,((x-x0)*dx+(y-y0)*dy)/den)); d=math.hypot(x-(x0+t*dx),y-(y0+t*dy))
        if d<r: put(x,y,col,a*(1-d/r)**1.5)
def ellipse(cx,cy,rx,ry,col):
    for y in range(max(0,int(cy-ry)),min(H,int(cy+ry+1))):
      for x in range(max(0,int(cx-rx)),min(W,int(cx+rx+1))):
        q=((x-cx)/rx)**2+((y-cy)/ry)**2
        if q<1:
          edge=(1-q)**.18; put(x,y,col,edge)

# deep indigo space with layered nebula
for y in range(H):
  for x in range(W):
    n=(math.sin(x*.018+math.sin(y*.011)*2)+math.sin(y*.025+x*.004)+math.sin((x+y)*.009))*.5
    t=y/H
    put(x,y,(.008+.018*(1-t)+.012*max(0,n), .012+.018*(1-t)+.008*max(0,n), .045+.065*(1-t)+.025*max(0,n)))
rng=random.Random(20261116)
for i in range(240):
  x=rng.randrange(W); y=rng.randrange(H); s=rng.choice([1,1,1,2]); glow(x,y,s*2,(.2,.45,1),1.5); put(x,y,(.6,.8,1),.45)

# Broken horizontal glints form a quiet sea beneath the ascending animal.
for k in range(420):
  depth=rng.random(); y=548+depth*219
  center=405-45*depth; spread=22+95*depth
  x=center+rng.gauss(0,spread)
  strength=(.035+.09*(1-depth))*rng.random()
  col=(1,.31,.065) if rng.random()<.48 else (.035,.65,.85)
  half=rng.uniform(1,9)*(0.5+depth)
  line(x-half,y,x+half,y,rng.uniform(.8,2.1),col,strength)
for k in range(100):
  y=rng.uniform(555,767); x=rng.uniform(25,740)
  line(x,y,x+rng.uniform(5,36),y,1.2,(.025,.13,.23),.22)

# Rising motes follow the curved wake and continue ahead of the crown.
for i in range(260):
  t=rng.random(); x=245+335*t+math.sin(i*2.3)*95; y=700-570*t+rng.random()*65
  glow(x,y,rng.uniform(1.3,5),(0.05,.8,1) if i%4 else (1,.42,.09),2.2)

# tentacles behind dome, diagonal streaming
for j in range(15):
  phase=j*.63; x0=255+j*25; y0=355-(x0-430)*.385; prev=(x0,y0)
  for k in range(1,66):
    u=k/65; x=x0-205*u+55*math.sin(u*4+phase*.35)*u+24*math.sin(u*9+phase)*u*u; y=y0+270*u+32*math.sin(u*4+phase)*u
    line(prev[0],prev[1],x,y,10,(.02,.55,.75),.22); line(prev[0],prev[1],x,y,3,(.1,.95,1),.7); prev=(x,y)
  glow(prev[0],prev[1],8,(.2,1,1),2)

# Broad translucent feeding ribbons wind amongst the fine blue threads.
for j in range(5):
  x0=325+j*47; y0=355-(x0-430)*.385; prev=(x0,y0)
  for k in range(1,61):
    t=k/60; x=x0-185*t+43*math.sin(t*5+j*.4)*t+13*math.sin(t*13+j)*t; y=y0+240*t
    col=(.65*(1-t)+.05,.22+.4*t,.12+.6*t)
    line(*prev,x,y,17*(1-t)+3,col,.24)
    line(*prev,x,y,4*(1-t)+1,(1-t,.52,.35+.6*t),.7)
    prev=(x,y)

# A tilted bell: uneven inner radiance, organic rim folds, and a warm halo.
glow(430,290,270,(.32,.075,.012),2.0)
glow(430,300,250,(0,.12,.20),2.2)
for y in range(110,455):
  for x in range(190,670):
    dx=x-430; dy=y-330; u=.933*dx-.36*dy; v=.36*dx+.933*dy
    if abs(u)>=205: continue
    roof=-145*math.sqrt(1-(u/205)**2)
    lip=25+8*math.cos(u*.12)
    if roof<v<lip:
      h=(v-roof)/(lip-roof); core=math.exp(-((u/90)**2+((v+65)/65)**2))
      angle=math.atan2(u,150-v)
      band=math.sin(angle*17+1.7*math.sin(angle*5)+v*.012)
      rib=.5+.5*band
      # Discontinuous curved folds collect in the lower translucent skirt.
      fold=math.exp(-((v-(8-19*(u/205)**2+5*math.sin(u*.035)))/3.5)**2)
      fold+=.55*math.exp(-((v-(-9-24*(u/205)**2+4*math.sin(u*.05+1)))/4)**2)
      fold*=.45+.55*math.sin(u*.027+1)**2
      warmth=max(0,1-h)*.06
      edge=math.exp(-((v-roof)/3)**2)
      c=(.43+.57*core+.022*rib+warmth-.10*fold, .065+.86*core+.018*rib-.035*fold, .025+.65*core+.012*rib-.012*fold)
      i=(y*W+x)*3
      pix[i:i+3]=[min(1,c[0]+edge*.05),min(1,c[1]+edge*.65),min(1,c[2]+edge*.9)]
for k in range(181):
  a=math.pi+k*math.pi/180; u=205*math.cos(a); v=145*math.sin(a)
  x=430+.933*u+.36*v; y=330-.36*u+.933*v
  glow(x,y,6,(.015,.45,.65),2)
for k in range(161):
  u=-200+400*k/160; v=25+8*math.cos(u*.12)
  x=430+.933*u+.36*v; y=330-.36*u+.933*v
  glow(x,y,5,(.06,.7,.85),2)
glow(416,273,40,(.45,.33,.17),2)
# sparks around crown
for i in range(90):
  a=rng.random()*math.tau; rr=rng.uniform(130,245); x=430+math.cos(a)*rr; y=320+math.sin(a)*rr*.65
  glow(x,y,rng.uniform(1,5),(1,.35,.08),2.4)

# A small inward-set boat with one warm lantern and a broken reflection.
for y in range(675,694):
  t=(y-675)/19
  left=111+14*t; right=211-19*t
  for x in range(int(left),int(right)+1):
    i=(y*W+x)*3; pix[i:i+3]=[.002,.003,.008]
line(114,675,208,675,2,(.13,.075,.035),.5)
line(158,675,158,641,3,(.008,.009,.014),1)
line(158,641,178,656,2,(.008,.009,.014),1)
glow(158,641,21,(1,.38,.08),2.3)
glow(158,641,4,(1,.85,.35),1)
for k in range(43):
  y=697+k*1.55; x=158+math.sin(k*2.1)*7; r=2+k*.20
  line(x-r,y,x+r,y,1.5,(.7,.25,.035),.32*(1-k/43))

def png(path):
  side=896
  raw=bytearray()
  for y in range(side):
    raw.append(0)
    sy=y*(H-1)/(side-1); iy=int(sy); fy=sy-iy; ny=min(H-1,iy+1)
    for x in range(side):
      sx=x*(W-1)/(side-1); ix=int(sx); fx=sx-ix; nx=min(W-1,ix+1)
      a=(iy*W+ix)*3; b=(iy*W+nx)*3; c=(ny*W+ix)*3; d=(ny*W+nx)*3
      for channel in range(3):
        v=(pix[a+channel]*(1-fx)+pix[b+channel]*fx)*(1-fy)+(pix[c+channel]*(1-fx)+pix[d+channel]*fx)*fy
        raw.append(int(max(0,min(255,v**.82*255))))
  def ch(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
  with open(path,'wb') as f:
    f.write(b'\x89PNG\r\n\x1a\n'); f.write(ch(b'IHDR',struct.pack('>IIBBBBB',side,side,8,2,0,0,0))); f.write(ch(b'IDAT',zlib.compress(bytes(raw),9))); f.write(ch(b'IEND',b''))
out=os.environ.get('MAKEFUN_OUTPUT_DIR','/output'); os.makedirs(out,exist_ok=True); png(os.path.join(out,'entry.png'))
