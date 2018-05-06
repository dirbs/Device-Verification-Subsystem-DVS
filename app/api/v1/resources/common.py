from app import app

@app.route('/')
def index_route():
    return 'Welcome to DVS'
