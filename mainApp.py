from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json
import requests
from flask_bootstrap import Bootstrap
from os.path import join, dirname

 # try:
import http.client as http_client
 # except ImportError:
     # import httplib as http_client

app = Flask(__name__)
Bootstrap(app)

port = int(os.getenv('PORT', 8000))

@app.route('/')
def index():
    # return app.send_static_file('index.html')
    try:
        connection = http_client.HTTPConnection('api.football-data.org')
        headers = { 'X-Auth-Token': '78df3a8be6e74031926b71bceca8978b',  'Content-type': 'application/json' }
        connection.request('GET', '/v1/competitions', None, headers )
        response = json.loads(connection.getresponse().read().decode())
    except(ValueError, KeyError, TypeError):
        return render_template('error.html')
    teamsInLeagueTable = []
    listLeague = []
    for element in response:
        league = {
            'id' : element['id'],
            'name' : element['caption'],
            'numberOfTeams' : element['numberOfTeams'],
        }
        listLeague.append(league)
    return render_template("index.html", leagues=listLeague)

@app.route('/competitions/<id>/leagueTable')
def leagueTable(id):
    try:
        connection = http_client.HTTPConnection('api.football-data.org')
        headers = { 'X-Auth-Token': '78df3a8be6e74031926b71bceca8978b', 'Content-type': 'application/json' }
        connection.request('GET', '/v1/competitions/{0}/leagueTable'.format(id), None, headers )
        response = json.loads(connection.getresponse().read().decode())
    except(ValueError, KeyError, TypeError):
        return render_template('error.html')
    print (response)
    try:
        leagueCaption = response['leagueCaption']
    except(ValueError, KeyError, TypeError):
        return render_template('noData.html')
    teamsInLeagueTable = []
    for team in response['standing']:
        team = {
            'position' : team['position'],
            'name' : team['teamName'],
            'logoHref' : team['crestURI'],
            'playedGames' : team['playedGames'],
            'points' : team['points'],
            'wins' : team['wins'],
            'draws' : team['draws'],
            'losses' : team['losses'],
            'goals' : team['goals'],
            'goalsAgainst' : team['goalsAgainst'],
        }
        if team['logoHref'] is None:
            team['logoHref']=''
        teamsInLeagueTable.append(team)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'audio/wav',
    }
    data = '{"text": "%s"}' % leagueCaption

    audioName = leagueCaption[:12]
    if "/" in audioName:
        audioName = audioName.replace("/", "")

    audioName =  ''.join(audioName.split());
    audioLocationAndName = './static/%s.wav' % audioName
    response = requests.post('https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize', headers=headers, data=data, auth=('426492a8-9cc8-4c2b-a24d-f05e0550c985', 'szVQwuJipJmn'))
    with open(join(dirname(__file__), audioLocationAndName ), 'wb') as audio_file:
        audio_file.write(response.content)
    return render_template('leagueTable.html', teamsTable=teamsInLeagueTable, competitionName=leagueCaption, audioFileName=audioName)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
