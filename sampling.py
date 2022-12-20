import random
cloudy={True:0.5,False:0.5}
sprinkler={'cloudy':{
        True:{
            True:0.1,False:0.9
        },
        False:{
            True:0.5,False:0.5
        }
    }
}
rain={'cloudy':{
        True:{
            True:0.8,False:0.2
        },
        False:{
            True:0.2,False:0.8
        }
    }
}
wetGrass={
    'sprinkler':{
        True:{
            'rain':{
                True:{True:0.99,False:0.01},
                False:{True:0.90,False:0.10},
                }
            },
        False:{
            'rain':{
                True:{True:0.90,False:0.1},
                False:{True:0.0,False:1.0},
            }
        },
    }
}


def priorSampling(cloudy,sprinkler,rain,wetGrass):
    a=random.random()

    cloudy_val=True if a<cloudy[True] else False
    b=random.random()
    sprinkler_val=True if b<sprinkler['cloudy'][cloudy_val][True] else False
    c=random.random()
    rain_val=True if c<rain['cloudy'][cloudy_val][True] else False
    d=random.random()
    wetGrass_val=True if d<wetGrass['sprinkler'][sprinkler_val]['rain'][rain_val][True] else False
    return (cloudy_val,sprinkler_val,rain_val,wetGrass_val)

# # priorSampling(cloudy,sprinkler,rain,wetGrass)
# dict={}
# for i in range(1000):
#     a=priorSampling(cloudy,sprinkler,rain,wetGrass)
#     dict[a]=dict.get(a,0)+1
# for i,v in dict.items():
#     print(i,v)

def rejectionSampling(bn,e,N):
    cloudy,sprinkler,rain,wetGrass=bn
    k=N
    dict={}
    while N>0:
        a=priorSampling(cloudy,sprinkler,rain,wetGrass)
        rej=False
        for i,v in e.items():
            if i=='cloudy':
                if a[0]!=v: rej = True
            if i=='sprinkler':
                if a[1]!=v: rej = True
            if i=='rain':
                if a[2]!=v: rej = True
            if i=='wetGrass':
                if a[3]!=v: rej = True
        if rej: continue
        dict[a]=dict.get(a,0)+1
        N-=1
    for i in dict:
        dict[i]=dict[i]/k
    return dict

# s=0
# for i,v in rejectionSampling((cloudy,sprinkler,rain,wetGrass),{'cloudy':True,'wetGrass':False},100000).items():
#     print(i,v)
#     s+=v
# print(s)

def weighted_sample(bn,e):
    w=1
    cloudy,sprinkler,rain,wetGrass=bn
    if 'cloudy' in e:
        cloudy_val=True if e['cloudy'] else False
        w=w*cloudy[cloudy_val]
    else:
        a=random.random()
        cloudy_val=True if a<cloudy[True] else False
    if 'sprinkler' in e:
        sprinkler_val=True if e['sprinkler'] else False
        w*=sprinkler['cloudy'][cloudy_val][sprinkler_val]
    else:
        b=random.random()
        sprinkler_val=True if b<sprinkler['cloudy'][cloudy_val][True] else False
    if 'rain' in e:
        rain_val=True if e['rain'] else False
        w*=rain['cloudy'][cloudy_val][rain_val]
    else:
        b=random.random()
        rain_val=True if b<rain['cloudy'][cloudy_val][True] else False
    if 'wetGrass' in e:
        wetGrass_val=True if e['wetGrass'] else False
        w*=wetGrass['sprinkler'][sprinkler_val]['rain'][rain_val][wetGrass_val]
    else:
        d=random.random()
        wetGrass_val=True if d<wetGrass['sprinkler'][sprinkler_val]['rain'][rain_val][True] else False
    return ((cloudy_val,sprinkler_val,rain_val,wetGrass_val),w)

def likelihoodWeighiting(bn,e,N):
    dict={}
    t=0
    for i in range(N):
        a=weighted_sample(bn,e)
        t+=a[1]
        dict[a[0]]=dict.get(a[0],0)+a[1]
    for i in dict:
        dict[i]=dict[i]/t
    return dict

for i,v in likelihoodWeighiting((cloudy,sprinkler,rain,wetGrass),{'cloudy':True,'wetGrass':False},100000).items():
    print(i,v)
print("---------------------------------------------")
def gibbsSampling(bn,e,N):
    dict={}
    cloudy,sprinkler,rain,wetGrass=bn
    nonevidenced=[i for i in ['cloudy','sprinkler','rain','wetGrass'] if i not in e]
    cloudy_val,sprinkler_val,rain_val,wetGrass_val=None,None,None,None
    for i in e:
        if i=='cloudy': cloudy_val=e[i]
        elif i=='sprinkler': sprinkler_val=e[i]
        elif i=='rain': rain_val=e[i]
        elif i=='wetGrass': wetGrass_val=e[i]
    if cloudy_val==None:
        a=random.random()
        cloudy_val=True if a<0.5 else False
    if sprinkler_val==None:
        b=random.random()
        sprinkler_val=True if b<sprinkler['cloudy'][cloudy_val][True] else False
    if rain_val==None:
        b=random.random()
        rain_val=True if b<rain['cloudy'][cloudy_val][True] else False
    if wetGrass_val==None:
        d=random.random()
        wetGrass_val=wetGrass_val=True if d<wetGrass['sprinkler'][sprinkler_val]['rain'][rain_val][True] else False
    curr=[cloudy_val,sprinkler_val,rain_val,wetGrass_val]
    for i in range(N):
        for j in nonevidenced:
            if j=='cloudy':
                a=random.random()
                cloudy_val=True if a<cloudy[True] else False
                curr[0]=cloudy_val
                prob=cloudy[cloudy_val]*sprinkler['cloudy'][cloudy_val][sprinkler_val]*rain['cloudy'][cloudy_val][rain_val]
                dict[tuple(curr)]=dict.get(tuple(curr),0)+prob
                
            if j=='sprinkler':
                b=random.random()
                sprinkler_val=True if b<sprinkler['cloudy'][cloudy_val][True] else False
                curr[1]=sprinkler_val
                prob=sprinkler['cloudy'][cloudy_val][sprinkler_val]*wetGrass['sprinkler'][sprinkler_val]['rain'][rain_val][wetGrass_val]
                dict[tuple(curr)]=dict.get(tuple(curr),0)+prob
            if j=='rain':
                b=random.random()
                rain_val=True if b<rain['cloudy'][cloudy_val][True] else False
                curr[2]=rain_val
                prob=rain['cloudy'][cloudy_val][sprinkler_val]*wetGrass['sprinkler'][sprinkler_val]['rain'][rain_val][wetGrass_val]
                dict[tuple(curr)]=dict.get(tuple(curr),0)+prob
            if j=='wetGrass':
                d=random.random()
                wetGrass_val=True if d<wetGrass['sprinkler'][sprinkler_val]['rain'][rain_val][True] else False
                curr[3]=wetGrass_val
                prob=wetGrass['sprinkler'][sprinkler_val]['rain'][rain_val][wetGrass_val]
                dict[tuple(curr)]=dict.get(tuple(curr),0)+prob
    t=sum(list(dict.values()))
    for i in dict:
        dict[i]=dict[i]/t
    return dict

for i,v in gibbsSampling((cloudy,sprinkler,rain,wetGrass),{'cloudy':True,'wetGrass':False},1000).items():
    print(i,v)    
