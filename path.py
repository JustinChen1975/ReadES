from flask import render_template,Flask,jsonify,request
import time
app = Flask(__name__)

@app.route('/get_path',methods=['get','post'])
def get_path():
	page=open('/home/yyj/path_graph.html',encoding='utf-8');
	res=page.read()
	return res;

app.run(host='58.199.65.161',port=8787,debug=True)
