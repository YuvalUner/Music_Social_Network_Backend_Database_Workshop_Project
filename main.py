import routes
from app_conf import app

if __name__ == '__main__':
    app.register_blueprint(routes.albums_routes, url_prefix='/albums')
    app.register_blueprint(routes.songs_routes, url_prefix='/songs')
    app.register_blueprint(routes.artists_routes, url_prefix='/artists')
    app.register_blueprint(routes.favorite_songs_routes, url_prefix='/favorite-songs')
    app.register_blueprint(routes.comment_routes, url_prefix='/comments')
    app.register_blueprint(routes.genres_routes, url_prefix='/genres')
    app.run(port=8080, debug=True)