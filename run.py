from app import app


app.config.from_object('server_config.DevelopmentConfig')  # app configs

app.run(host='127.0.0.1')
