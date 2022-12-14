import routes
from app_conf import app

if __name__ == '__main__':
    app.register_blueprint(routes.albums_routes, url_prefix='/albums')
    app.register_blueprint(routes.songs_routes, url_prefix='/songs')
    app.register_blueprint(routes.artists_routes, url_prefix='/artists')

    app.run(port=8080, debug=True)