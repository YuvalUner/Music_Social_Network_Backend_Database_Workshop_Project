from app_conf import app
from routes import albums_routes
from routes.songs import songs_routes

if __name__ == '__main__':
    app.register_blueprint(albums_routes, url_prefix='/albums')
    app.register_blueprint(songs_routes, url_prefix='/songs')

    app.run(port=8080, debug=True)