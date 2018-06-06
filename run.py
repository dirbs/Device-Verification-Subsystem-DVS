from app import app, Host, Port

app.config.from_object('server_config.DevelopmentConfig')  # app configs

if __name__ == "__main__":
    app.run(host=Host, port=Port)
