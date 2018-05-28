from app import app, Host, Port

app.config.from_object('server_config.DevelopmentConfig')  # app configs

app.run(host=Host, port=Port)
