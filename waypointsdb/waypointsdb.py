from __future__ import with_statement
import os
import sqlite3
from contextlib import closing
from flask import Flask, request, Response, make_response, g, json, render_template
from tempfile import mkstemp

DEBUG = True
DATABASE = 'data.db'
SECRET_KEY = 'dev key'
MARKERSDB = "markersDB.js"
JS_MAIN = "main"

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('WAYPOINTSDB_CONFIG', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE']);

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0],value)
        for idx,value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def index():
    return render_template('index.html', jsMain=app.config['JS_MAIN'],
            scriptRoot = request.script_root)

@app.route('/about')
def about():
    return render_template('about.html', scriptRoot = request.script_root)

@app.route('/template/<path:template>')
def js_template(template):
    return render_template(template)

@app.route('/download', methods=['POST'])
def build_file():
    data = request.json
    points = query_db('select * from waypoints where id in (%s)'%
            ','.join('?'*len(data)),data)
    out = []
    for point in points:
        out.append('%s:%s:%s:%s:true:%s'%
            (point['name'],point['x'],point['y'],point['z'],point['color'][1:]))
    fd,path = mkstemp()
    f = os.fdopen(fd,'w')
    f.write("\n".join(out));
    f.close();
    return path;

@app.route('/download/<path:filename>')
def download(filename):
    filename = '/'+filename
    f = open('/'+filename);
    resp = make_response(f.read())
    resp.headers['Content-Disposition'] = 'attachment; filename=mc.rampant.io.DIM0.points'
    f.close();
    os.remove(filename);
    return resp;

@app.route('/api/points', methods=['GET'])
def api_points():
    points = query_db('select * from waypoints order by name')
    return Response(json.dumps(points),mimetype='application/json')

@app.route('/api/points/<pId>', methods=['GET'])
def api_point(pId):
    point = query_db('select * from waypoints where id=?', [pId], one=True)
    if point is None:
        return Response(status=404)
    else:
        return Response(json.dumps(point), mimetype='application/json')

@app.route('/api/points', methods=['POST'])
def api_create_point():
    if( request.headers['Content-Type'] != 'application/json'):
        return Response('Unsupported Media Type', status=415)

    data = request.json
    g.db.execute('insert into waypoints (name,color,x,z,y,poiType) values (?,?,?,?,?)',
        [data['name'],data['color'],data['x'],data['z'],data['y'],data['poiType']])
    g.db.commit()

    point = query_db('select * from waypoints where rowid=last_insert_rowid()',one=True)

    build_poi();
    return Response(json.dumps(point), mimetype='application/json')

@app.route('/api/points/<pId>', methods=['PUT'])
def api_update_point(pId):
    if( request.headers['Content-Type'] != 'application/json'):
        return Response('Unsupported Media Type', status=415)

    data = request.json
    g.db.execute('update waypoints set name=?,color=?,x=?,z=?,y=?,poiType=? where id=?',
            [data['name'],data['color'],data['x'],data['z'],data['y'],data['poiType'],pId])
    g.db.commit()

    build_poi();
    return Response(json.dumps(data), status=200,mimetype='application/json')

@app.route('/api/points/<pId>', methods=['DELETE'])
def api_delete_point(pId):
    g.db.execute('delete from waypoints where id=?', [pId])
    g.db.commit()
    return Response(status=200)


@app.route('/api/poi/build', methods=['PUT'])
def build_poi():
    points = query_db("select * from waypoints where poiType != 'none' order by poiType, name")

    markers = dict(default=[
        dict(displayName="Outposts",
            groupName="default-outpost",
            icon="/minecraft/map/icons/outpost.png",
            createInfoWIndow="true"),
        dict(displayName="Points of Interest",
            groupName="default-poi",
            icon="/minecraft/map/icons/poi.png",
            createInfoWIndow="true"),
        dict(displayName="Rail Station Stops",
            groupName="default-rail",
            icon="/minecraft/map/icons/rail.png",
            createInfoWIndow="true"),
        dict(displayName="Dungeons",
            groupName="default-dungeon",
            icon="/minecraft/map/icons/dungeon.png",
            createInfoWIndow="true"),
    ])

    markersDB = dict()
    for p in points:
        dbKey = 'default-'+p['poiType']
        if dbKey not in markersDB:
            markersDB[dbKey] = dict(raw=[],name="",created="false")

        markersDB[dbKey]['raw'].append(dict(
            x=p['x'],y=p['y'],z=p['z'],
            alt=p['name'],
            icon="/minecraft/map/icons/%s.png"%p['poiType']))

    f = open(app.config['MARKERSDB'], 'w')
    f.write("var markersDB="+json.dumps(markersDB)+";");
    f.close();
    return Response();


if __name__ == '__main__':
    app.run()


