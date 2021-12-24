#coding:utf-8
from elasticsearch import Elasticsearch
host="58.199.65.161"
port=9200

num=0

def init():
    es = Elasticsearch(hosts=host, port=9200, timeout=200)
    # es = Elasticsearch(hosts=host, port=9200, timeout=200 , http_auth=())
    return es
def search(index,type,q,time,intpath,larr):
    es = init()
    if not q:
        q={"query" : {
       "bool": {
              "must": [
                {
                  "range": {
                    "@timestamp": {
                      "gte": time,
                      "lte": "now",
                      "format": "yyyy-MM-dd HH:mm:ss.SSS"
                    }
                  }
                }
              ]
       }
    },
            "size":"100",
            "sort":{"@timestamp":"asc"},
            "_source":["counter","@timestamp","INT path","INT metadata"]}
    query = es.search(index=index, body=q)
    results = query['hits']['hits']
    total = query['hits']['total']
    data={}
    flag=0
    if total['value']<=1:
        return data
    for hit in results:
        tstr = str(hit['_source']['@timestamp']).replace('T',' ').replace('Z','')
        #tstr1 = tstr[0:19]
        #print(tstr1)
        #tstr2 = tstr[20:24]
        #print(tstr2)
        #datatime_str = datetime.strptime(tstr1,"%Y-%m-%d %H:%M:%S")
        #print(str(int(datatime_str.timestamp()))+tstr2)
        #time2 = str(int(datatime_str.timestamp()))+tstr2

        if tstr>=time:
            time = tstr
            print(time)
        if intpath == []:
            intpath = hit['_source']['INT path']
            for node in intpath:
                latencysum = 0
                larr[node] = latencysum
        elif hit['_source']['INT path']!=intpath:
            print(hit['_source']['INT path'])
            intpath=hit['_source']['INT path']
            print(larr)
            flag = 1
            larr = {}
            for node in intpath:
                latencysum = 0
                larr[node]=latencysum
            for value in hit['_source']['INT metadata']:
                larr[value['nodeID']] += value['latency']
                larr[value['nodeID']] = larr[value['nodeID']] / 2
            data[0] = time
            data[1] = intpath
            data[2] = larr
            data[3] = flag
            graph2(data)
            continue
        #print(larr)
        #print(hit['_source']['INT metadata'])
        for value in hit['_source']['INT metadata']:
            larr[value['nodeID']]+=value['latency']
            larr[value['nodeID']] = larr[value['nodeID']]/2

        #print(hit['_source']['@timestamp'])
        #print(hit['_source']['INT metadata'])
        #print(hit['_source']['INT path'])
        data[0]=time
        data[1]=intpath
        data[2]=larr
        data[3]=flag
    print(larr)
    return data

import time
def timer(n):
    timenum = "2021-11-19 00:00:00.000"
    path = []
    latemcyarr = {}
    while True:
        res=search("intbeat*","data",None,timenum,path,latemcyarr)
        if len(res)>0:
            timenum=res[0]
            path=res[1]
            graph(res)
            time.sleep(n)
        else:
            time.sleep(n)

from pyecharts import options as opts
from pyecharts.charts import Graph
def graph(data):
    #data[1] = intpath
    #data[2] = larr
    rtpath = data[1].copy()
    rtlink = data[2]
    rtpath.insert(0,'Start')
    rtpath.append('End')
    nodes_data = []
    rtpath2 = list(dict.fromkeys(rtpath).keys())
    for r in rtpath2:
        nodes_data.append(opts.GraphNode(name=str(r),symbol_size=40))
    links_data = []
    i = 0
    while i<len(rtpath)-1:
        if rtpath[i] == 'Start':
            links_data.append(opts.GraphLink(source='Start', target=rtpath[i + 1], value=0))
        else:
            links_data.append(opts.GraphLink(source=rtpath[i], target=rtpath[i+1], value=int(rtlink[rtpath[i]])))
        i = i + 1
    titleopt = {}
    if data[3]==1:
        titleopt = opts.TextStyleOpts(color="red",font_size="15")
    else:
        titleopt = opts.TextStyleOpts(color="black",font_size="15")
    c = (
        Graph()
        .add(
	    "",
            nodes_data,
            links_data,
            layout="circular",
            repulsion=4000,
            gravity=0.5,
            symbol= "roundRect",
            edge_label=opts.LabelOpts(
                is_show=True, position="middle", formatter="Latency:{c}"
            ),
            edge_symbol=['circle', 'arrow'],
            linestyle_opts=opts.LineStyleOpts(type_='dotted')
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="ONOS Router Path Graph",subtitle=data[0],subtitle_textstyle_opts=titleopt)
        )
        .render("/data/wwwroot/path/static/path_graph.html")
    )
    with open('/data/wwwroot/path/static/path_graph.html','+r') as f:
        t = f.read()
        t = t.replace('<meta charset="UTF-8">', '<meta http-equiv="refresh" content="2;url=/static/path_graph.html">')
        f.seek(0, 0)    
        f.write(t)

def graph2(data):
    #data[1] = intpath
    #data[2] = larr
    rtpath = data[1].copy()
    rtlink = data[2]
    rtpath.insert(0,'Start')
    rtpath.append('End')
    nodes_data = []
    rtpath2 = list(dict.fromkeys(rtpath).keys())
    for r in rtpath2:
        nodes_data.append(opts.GraphNode(name=str(r),symbol_size=40))
    links_data = []
    i = 0
    while i<len(rtpath)-1:
        if rtpath[i] == 'Start':
            links_data.append(opts.GraphLink(source='Start', target=rtpath[i + 1], value=0))
        else:
            links_data.append(opts.GraphLink(source=rtpath[i], target=rtpath[i+1], value=int(rtlink[rtpath[i]])))
        i = i + 1
    titleopt = {}
    if data[3]==1:
        titleopt = opts.TextStyleOpts(color="red",font_size="15")
    else:
        titleopt = opts.TextStyleOpts(color="black",font_size="15")
    pwd = "/data/wwwroot/path/static/history/path_graph"+data[0].replace("-","S").replace(":","T").replace(".","U").replace(" ","V")+".html"
    c = (
        Graph()
        .add(
	    "",
            nodes_data,
            links_data,
            layout="circular",
            repulsion=4000,
            gravity=0.5,
            symbol= "roundRect",
            edge_label=opts.LabelOpts(
                is_show=True, position="middle", formatter="Latency:{c}"
            ),
            edge_symbol=['circle', 'arrow'],
            linestyle_opts=opts.LineStyleOpts(type_='dotted')
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="ONOS Router Path Graph",subtitle=data[0],subtitle_textstyle_opts=titleopt)
        )
        .render(pwd)
    )

if __name__=="__main__":
    timer(2)
    #res=search("intbeat*","data",None)
    #print(res)
