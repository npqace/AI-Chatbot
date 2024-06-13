from flask import Flask, render_template, request
from model import db
from route import api

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'  # replace with your actual database URI
    db.init_app(app)
    app.register_blueprint(api, url_prefix='/api')

    # @app.before_request
    # def log_request_info():
    #     app.logger.debug('Headers: %s', request.headers)
    #     app.logger.debug('Body: %s', request.get_data())

    @app.route('/')
    def home():
        return render_template('index.html')  

    # @app.errorhandler(403)
    # def forbidden(e):
    #     return render_template('403.html'), 403

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)