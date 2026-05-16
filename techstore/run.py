# from app import app

# app.run(host="0.0.0.0", port=8080, debug=True)

# from app import create_app

# app = create_app()

# if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=8080, debug=True)


from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    try:
        db.engine.connect()
        print("✅ Conexión exitosa con MySQL")
    except Exception as e:
        print("❌ Error de conexión:", e)



# app.run(host="0.0.0.0", port=8080, debug=True)
from app import create_app
app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
