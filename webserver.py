from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                resturants = session.query(Restaurant).all()
                for resturant in resturants:
                    output += "<h3>%s</h3>" % resturant.name
                    output += "<a href='/%s/edit'>Edit</a><br>" % resturant.id
                    output += "<a href='/%s/delete'>Delete</a><br><br><br>" % resturant.id

                output += "<a href='/new'>Make a New Restaurant Here</a>"
                self.wfile.write(bytes(output, 'utf-8'))
                return

            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = '''
                    <h1>Make a New Restaurant</h1>
                    <form method='POST' enctype='multipart/form-data'>
                        <label>
                            Name
                            <input type='text' name='name'>
                        </label>
                        <br><br>
                        <input type='submit' value='Create'>
                    </form>
                '''

                self.wfile.write(bytes(output, 'utf-8'))
                return

            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurant_id = self.path.split('/')[-2]
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

                output = '''
                    <h1>Are you sure you want to delete %s?</h1>
                    <form method='POST' enctype='multipart/form-data'>
                        <input type='hidden' value='%s' name='id'>
                        <input type='submit' value='Delete'>
                    </form>
                ''' % (restaurant.name, restaurant_id)

                self.wfile.write(bytes(output, 'utf-8'))
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurant_id = self.path.split('/')[-2]
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

                output = '''
                    <h1>%s?</h1>
                    <form method='POST' enctype='multipart/form-data'>
                        <input type='hidden' value='%s' name='id'>
                        <input type='text' name=name>
                        <br><br>
                        <input type='submit' value='Rename'>
                    </form>
                ''' % (restaurant.name, restaurant_id)

                self.wfile.write(bytes(output, 'utf-8'))
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

        
    def do_POST(self):
        try:
            if self.path.endswith("/new"):
                ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                pdict['CONTENT-LENGTH'] = int(self.headers.get('Content-length'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    name_content = fields.get('name')

                session.add(Restaurant(name = name_content[0]))
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants') # redirect
                self.end_headers()

                return

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                pdict['CONTENT-LENGTH'] = int(self.headers.get('Content-length'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    name_content = fields.get('name')
                    id_content = fields.get('id')

                restaurant = session.query(Restaurant).filter_by(id = id_content[0]).one()
                restaurant.name = name_content[0]
                session.add(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants') # redirect
                self.end_headers()

                return

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                pdict['CONTENT-LENGTH'] = int(self.headers.get('Content-length'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    id_content = fields.get('id')

                restaurant = session.query(Restaurant).filter_by(id = id_content[0]).one()
                session.delete(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants') # redirect
                self.end_headers()

                return

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()