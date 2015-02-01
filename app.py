import httplib2
import webapp2
import random
import math
import json
import cgi
import urllib
from apiclient.discovery import build
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

url = 'https://www.googleapis.com/auth/bigquery'
PROJECT_NUMBER = '637239282909'

credentials = AppAssertionCredentials(scope=url)
httpss = credentials.authorize(httplib2.Http())
bigquery_service = build('bigquery','v2',http=httpss)
DEFAULT_CIRCLE_DB_NAME = 'default_circle_db'
DEFAULT_PLAYER_DB_NAME = 'default_player_db'

tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),  
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),  
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),  
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),  
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# returns the db?
def circle_db_key(circle_db_name = DEFAULT_CIRCLE_DB_NAME):
	return ndb.Key('CircleDB', circle_db_name)
def player_db_key(player_db_name = DEFAULT_PLAYER_DB_NAME):
	return ndb.Key('PlayerDB', player_db_name)

class Player(ndb.Model):
	name = ndb.StringProperty(indexed = False)
	email = ndb.StringProperty(indexed = False)
	color = ndb.StringProperty(indexed = False)
	date = ndb.DateTimeProperty(auto_now_add=True)

class Circle(ndb.Model):
	player = ndb.StructuredProperty(Player)
	date = ndb.DateTimeProperty(auto_now_add=True)
	x = ndb.IntegerProperty(indexed = False)
	y = ndb.IntegerProperty(indexed = False)

class PollCircleData(webapp2.RequestHandler):
	def get(self):
		# TODO create dirty bit for each connected client

		circle_db_name = self.request.get('circle_db_name', DEFAULT_CIRCLE_DB_NAME)
		circles = Circle.query(ancestor=circle_db_key(DEFAULT_CIRCLE_DB_NAME)).order(Circle.date)
		self.response.out.write(str(circles.count()))

class AddPlayer(webapp2.RequestHandler):
	def post(self):

		# get posted data
		name = self.request.get('name')
		email = self.request.get('email')
		print name, email

		# get current db
		player_db_name = self.request.get('player_db_name', DEFAULT_PLAYER_DB_NAME)
		players = Player.query(ancestor=player_db_key(DEFAULT_PLAYER_DB_NAME)).order(Player.date)

		# check if player already exists
		for p in players:
			if p.email == email and p.name == name:
				print 'player already added', name
				return

		# add new player to db
		player = Player(parent=player_db_key(player_db_name))
		player.name = name
		player.email = email
		player.color = 'red' #tableau20(players.count())
		player.put()

# AddCircle
#	
class AddCircle(webapp2.RequestHandler):
	def post(self):

		# get posted data
		email = int(self.request.get('email'))
		x = int(self.request.get('x'))
		y = int(self.request.get('y'))

		# get db name 
		circle_db_name = self.request.get('circle_db_name', DEFAULT_CIRCLE_DB_NAME)
		circles = Circle.query(ancestor=circle_db_key(DEFAULT_CIRCLE_DB_NAME)).order(Circle.date)

		# get player
		player = Player.query(Player.email == email).order(Player.date).fetch(1)
		if not player:
			print 'ERROR -- attempting to add circle without player'
			return

		# check if circle already exists
		radius = 10 #pixels
		addFlag = True
		for c in circles:
			dx = c.x - circle.x
			dy = c.y - circle.y
			d = math.sqrt(dx*dx + dy*dy)
			if d < radius:
				addFlag = False
				c.key.delete()
				return

		# add new item to db
		circle = Circle(parent=circle_db_key(circle_db_name))
		circle.player = player
		circle.x = x
		circle.y = y
		circle.put()

class GetPlayers(webapp2.RequestHandler):
	def get(self):

		# get db name, else use default
		player_db_name = self.request.get('player_db_name', DEFAULT_PLAYER_DB_NAME)

		# query db
		resp = []
		players = Player.query(ancestor=player_db_key(DEFAULT_PLAYER_DB_NAME)).order(Player.date)
		for p in players:
			resp.append({ 'name': p.name, 'c': p.color})

		# send player data back as json
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(resp))


class GetCircles(webapp2.RequestHandler):
	def get(self):

		# get db name, else use default
		circle_db_name = self.request.get('circle_db_name', DEFAULT_CIRCLE_DB_NAME)

		# query db
		resp = []
		circles = Circle.query(ancestor=circle_db_key(DEFAULT_CIRCLE_DB_NAME)).order(Circle.date)
		for c in circles:
			resp.append({ 'x': c.x, 'y': c.y , 'c': c.player.color})

		# send circle data back as json
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(resp))

class ShowHome(webapp2.RequestHandler):
	def get(self):
		temp_data = {}
		temp_path = 'Templates/index.html'
		self.response.out.write(template.render(temp_path, temp_data))

class ShowChartPage(webapp2.RequestHandler):
	def get(self):
		temp_data = {}
		temp_path = 'Templates/chart.html'
		queryData = {'query':'SELECT word FROM [publicdata:samples.shakespeare] LIMIT 1000'}
		tableData = bigquery_service.jobs()
		response = tableData.query(projectId=PROJECT_NUMBER,body=queryData).execute()
		self.response.out.write(response)
		#self.response.out.write(template.render(temp_path, temp_data))
		 
class DisplayChart(webapp2.RequestHandler):
	def get(self):
		temp_data = {}
		temp_path = 'Templates/displayChart.html'
		self.response.out.write(template.render(temp_path, temp_data))

class GetChartData(webapp2.RequestHandler):
	def get(self):
		inputData = self.request.get("inputData")
		# query based on input data

		resp = []
		for i in range(10):
			resp.append({ 'x': random.randrange(0,1000), 'y': random.randrange(0,500) })
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(resp))
		 
## Here is the WSGI application instance that routes requests
application = webapp2.WSGIApplication([
	('/chart', ShowChartPage),
	('/displayChart', DisplayChart),
	('/getChartData', GetChartData),
	('/pollCircleData', PollCircleData),
	('/addCircle', AddCircle),
	('/addPlayer', AddPlayer),
	('/getCircles', GetCircles),
	('/getPlayers', GetPlayers),
	('/', ShowHome),
], debug=True)
