import httplib2
import webapp2
from google.appengine.ext.webapp import template
from apiclient.discovery import build
from oauth2client.appengine import AppAssertionCredentials

url = 'https://www.googleapis.com/auth/bigquery'
PROJECT_NUMBER = '637239282909'

credentials = AppAssertionCredentials(scope=url)
httpss = credentials.authorize(httplib2.Http())
bigquery_service = build('bigquery','v2',http=httpss)

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
			 
	 
		 
## Here is the WSGI application instance that routes requests
application = webapp2.WSGIApplication([
	('/chart', ShowChartPage),
	('/displayChart', DisplayChart),
	('/', ShowHome),
], debug=True)
