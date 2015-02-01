import httplib2
import webapp2
import random
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

# returns the circle db?
def circle_db_key(circle_db_name = DEFAULT_CIRCLE_DB_NAME):
	return ndb.Key('CircleDB', circle_db_name)

class Player(ndb.Model):
	name = ndb.StringProperty(indexed = False)

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

# AddCircle
#	http://localhost:8080/addCircle?x=200&y=100&name=usrname
class AddCircle(webapp2.RequestHandler):
	def post(self):

		# get db name 
		circle_db_name = self.request.get('circle_db_name', DEFAULT_CIRCLE_DB_NAME)

		# create item to add
		circle = Circle(parent=circle_db_key(circle_db_name))
		circle.player = Player(
			name = self.request.get('name'))#name = users.get_current_user().user_id()
		circle.x = int(self.request.get('x'))
		circle.y = int(self.request.get('y'))

		# add to db
		circle.put()

		# redirect to get data page
		#self.redirect('/displayChart?')

class GetCircleData(webapp2.RequestHandler):
	def get(self):

		# get db name, else use default
		circle_db_name = self.request.get('circle_db_name', DEFAULT_CIRCLE_DB_NAME)

		# query db
		resp = []
		circles = Circle.query(ancestor=circle_db_key(DEFAULT_CIRCLE_DB_NAME)).order(Circle.date)
		for c in circles:
			resp.append({ 'x': c.x, 'y': c.y })

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
	('/getCircleData', GetCircleData),
	('/', ShowHome),
], debug=True)
