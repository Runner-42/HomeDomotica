from flask import Flask

HomedomoticaPortal = Flask(__name__)

@HomedomoticaPortal.route('/')
def hello_world():
    return "Hello World!"
    
if __name__ == '__main__':
    HomedomoticaPortal.run(debug=True,host='0.0.0.0')