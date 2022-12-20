def listDiff(list1,list2):
    ans=[]
    for i in list1+list2:
        if i not in list1 or i not in list2:
            ans.append(i)
    return ans
def getAllowedColors(graph,city,colors):
    nA=[]
    for city in graph[(city,False)]:
        if city[1] != '':
            nA.append(city[1])
    allowColo=listDiff(colors,nA)
    return allowColo

def degreeHeu(graph):
    index_nei_len=[]
    for i,l in enumerate(graph.items()):
        if l[0][1] is False:
            index_nei_len.append((i,len(l[1])))
    max_nei=max(index_nei_len,key=lambda x:x[1])[1]
    max_index_neighbour_len = [t[0] for t in index_nei_len if t[1] == max_nei]
    cities=[]
    for i in max_index_neighbour_len:
        cities.append(list(graph)[i][0])
    return cities



#city or cities with minimum remaining values/colors
def mrv(graph, colors):
    noColorCiti=[]
    for city,boool in graph.items():
        if city[1] is False:
            noColorCiti.append((city[0]))
    allowed_color_each_city = {}
    for city in noColorCiti:
        allowed_color_each_city[city] = getAllowedColors(graph, city, colors)
    min_available_color_len = min([len(allowed_colors) for city, allowed_colors in allowed_color_each_city.items()])
    #cities = [city for city, colors in allowed_color_each_city.items() if len(colors) is min_available_color_len]
    cities=[]
    for city,colors in allowed_color_each_city.items():
        if len(colors) is min_available_color_len:
            cities.append(city)
    return cities



#least constraining val, most used color 
def lcv(graph, colors):
    city_color = []
    color_number = {}
    for nei in graph.values():
        for c in nei:
            if c[1] != '':
                city_color.append(c)
    all_used_colors=list(set(city_color))
    if not all_used_colors:
        return colors
    for cc in all_used_colors:
        if cc[1] not in color_number:
            color_number[cc[1]] = 1
        else:
            color_number[cc[1]] += 1
    number_of_max = max(color_number.items(), key=lambda x:x[1])[1]
    colors = [key for (key, value) in color_number.items() if value is number_of_max]
    return colors


def coloring(graph, city, color):
    nei=graph[(city,False)]
    graph.pop((city,False))
    graph[(city,True)]=nei
    for nei_list in graph.values():
        for n in nei_list:
            if n[0] == city:
                nei_list.append((n[0],color))
                nei_list.remove(n)

def do_stg(graph,colors):
    for i in range(len(graph)):
        max_deg_cities=degreeHeu(graph)
        cities_with_less_rem_col=mrv(graph,colors)
        most_used_col=lcv(graph,colors)
        cmnCities=set(max_deg_cities).intersection(set(cities_with_less_rem_col))
        if cmnCities:
            sel_city=cmnCities.pop()
        else:
            sel_city=max_deg_cities.pop()
#        sel_city = set(max_deg_cities).intersection(set(cities_with_less_rem_col)).pop()

        # sel_city=list(set(max_deg_cities) and set(cities_with_less_rem_col)).pop()
        cols_for_sel_city=getAllowedColors(graph,sel_city,colors)
        # commonColors=list(set(cols_for_sel_city) and set(most_used_col))
        commonColors = set(most_used_col).intersection(set(cols_for_sel_city))

        if commonColors:
            col=commonColors.pop()
        else:
            col=cols_for_sel_city.pop()
        coloring(graph,sel_city,col)
    for city,nei in graph.items():
        if len(nei)==0:
            graph[city]=['anyCol']
    # print(graph)
    return graph

graph={}
anna=open('schol.txt','r')
s=False
for i in anna:
    if i[0]=='p':
        s=True
        a=i.split()
        e=int(a[2])
        for j in range(1,e+1):
            graph[str(j)]=[]
        continue
    if not s: continue
    a=i.split()
    graph[str(a[1])].append(str(a[2]))

# graph={
#     "V1":["V3","V5","V2"],
#     "V2":['V1','V5','V6'],
#     "V3":['V1','V5','V6'],
#     "V4":['V6'],
#     "V5":['V1','V2','V3','V6'],
#     "V6":['V2','V3','V4','V5']
# }

colors=[]
n=int(input('enter no of colors'))
for i in range(1,n+1):
    colors.append("clr"+str(i))

# colors=['red','green','BLUE']
new_graph={}
for i in graph.items():
    new_graph[(i[0],False)]=[(j,'') for j in i[1]]


do_stg(new_graph,colors)



a=set()
any_col=[]
for k,i in new_graph.items():
    for j in i:
        if j=='anyCol':
            any_col.append(k[0])
            continue
        a.add(j)
print(a)
print( "any col nodes:" ,any_col)