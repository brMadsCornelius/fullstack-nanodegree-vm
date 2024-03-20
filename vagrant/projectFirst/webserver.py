from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()   # session=interface to DB - no changes on session will happen untill i call session commit

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("/hello"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = "<html><body>"
            message += "<h1>Hello!</h1>"
            message += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
            message += "</body></html>"
            self.wfile.write(message.encode('utf-8'))
            
            return
        elif self.path.endswith("/hola"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = "<html><body>Hola!</body></html>"
            self.wfile.write(message.encode('utf-8'))
            
            return
        elif self.path.endswith("/restaurants"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = "<html><body>"
            # Query all restaurants in restaurants DB
            message += "<a href='/restaurants/new'>Make a new restuarant here</a>"
            message += "</br></br></br>"
            resaurtants = session.query(Restaurant).all()
            for restaurant in resaurtants:
                message += f"{restaurant.name}"
                message += "</br>"
                message += f"<a href='restaurants/{restaurant.id}/edit'>Edit</a>"
                message += "</br>"
                message += f"<a href='restaurants/{restaurant.id}/delete'>Delete</a>"
                message += "</br></br></br>"
               
            message += "</body></html>"
            self.wfile.write(message.encode('utf-8'))
            
            return
        elif self.path.endswith("/restaurants/new"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += "<html><body>"
            message += "<h1>Make a new Restaurant</h1>"
            message += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
            message += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
            message += "<input type='submit' value='Create'>"
            message += "</form></body></html>"
            self.wfile.write(message.encode('utf-8'))
            
            return
        elif self.path.endswith("/edit"):
            restaurantIDPath = self.path.split("/")[2]
            print(restaurantIDPath)
            myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
            if myRestaurantQuery:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = "<html><body>"
                message += "<h1>"
                message += myRestaurantQuery.name
                message += "</h1>"
                message += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % restaurantIDPath
                message += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name
                message += "<input type = 'submit' value = 'Rename'>"
                message += "</form>"
                message += "</body></html>"

                self.wfile.write(message.encode('utf-8'))
        elif self.path.endswith("/delete"):
            restaurantIDPath = self.path.split("/")[2]

            myRestaurantQuery = session.query(Restaurant).filter_by(
                id=restaurantIDPath).one()
            if myRestaurantQuery:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = ""
                message += "<html><body>"
                message += "<h1>Are you sure you want to delete %s?" % myRestaurantQuery.name
                message += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/%s/delete'>" % restaurantIDPath
                message += "<input type = 'submit' value = 'Delete'>"
                message += "</form>"
                message += "</body></html>"

                self.wfile.write(message.encode('utf-8'))
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            if ctype == 'multipart/form-data':
                post_data = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                messagecontent = post_data.getvalue('newRestaurantName')

                if self.path.endswith("/restaurants/new"):
                    # Create new Restaurant obj
                    newRestaurant = Restaurant(name=messagecontent)
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants') # Will redirect to restaurants page
                    self.end_headers()
                elif self.path.endswith("/edit"):
                    # edit restaurant name
                    restaurantIDPath = self.path.split("/")[2]
                    print(f"edit id: {restaurantIDPath}")
                    myRestaurantQuery = session.query(Restaurant).filter_by(
                        id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        print(f"{myRestaurantQuery.name} changed to: {messagecontent}")
                        myRestaurantQuery.name = messagecontent
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
                elif self.path.endswith("/delete"):
                    # delete restaurant name
                    restaurantIDPath = self.path.split("/")[2]
                    myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                    if myRestaurantQuery:
                        print(f"Deleting: {myRestaurantQuery.name}")
                        session.delete(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants') ## Some how redirection here doesnt work??? Never found out why.
                        self.end_headers()
                
                return
        except Exception as e:
            print("Error:", e)

def main():
    try:
        port = 8082
        server = HTTPServer(('', port), WebServerHandler)
        print("Web Server running on port " + str(port))
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()
