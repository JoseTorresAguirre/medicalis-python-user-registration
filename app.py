from flask import Flask, request, jsonify, session 
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash , check_password_hash
from emailTest import enviar_correo
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clave secreta para sesiones
#app.secret_key = 'una_clave_secreta_segura_y_larga'
CORS(app, origins=["http://localhost:5173"], methods=["GET", "POST", "OPTIONS"], supports_credentials=True)


# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/clinica'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definición del modelo
class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    tdni = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(100), unique=True, nullable=False)
    paterno = db.Column(db.String(100), nullable=False)
    materno = db.Column(db.String(100), nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    fnac = db.Column(db.Date, nullable=False)
    genero = db.Column(db.Enum('M', 'F', 'Otro'))
    celular = db.Column(db.String(100))
    pais = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    distrito = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    rol = db.Column(db.Enum('paciente', 'especialista', 'admin'), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    imagen_perfil_url = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Endpoint para registrar usuarios
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    hashed_password = generate_password_hash(data['dni'], method='pbkdf2:sha256')

    new_user = Usuario(
        tdni=data['tdni'],
        dni=data['dni'],
        paterno=data['paterno'],
        materno=data['materno'],
        nombres=data.get('nombres'),
        fnac=data['fnac'],
        genero=data.get('genero'),
        celular=data.get('celular'),
        pais=data.get('pais'),
        departamento=data.get('departamento'),
        provincia=data.get('provincia'),
        distrito=data.get('distrito'),
        email=data.get('email'),
        rol="paciente",
        fecha_registro=data.get('fecha_registro'),
        imagen_perfil_url="no-imge.png",
        password=hashed_password,
    )
    
    try:
        # Envía el correo de bienvenida
        
        db.session.add(new_user)
        db.session.commit()
        enviar_correo(new_user.email)  # Llama a la función para enviar el correo

        
        
        return jsonify({"message": "Usuario registrado exitosamente."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
    #Endpoint para login
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user = Usuario.query.filter_by(email=data['email']).first()
    #obtiene el email enviado desde el front y lo busca en la base de datos si existe

    #verifica la existencia del usuario
    if user:
        #contaseña de la base de datos este en formato bytes
        # # Convierte la contraseña almacenada a bytes
        if check_password_hash(user.password, data['password']): # Convierte la contraseña del login a bytes y la compara
            # Iniciar sesión y almacenar el rol del usuario en el backend
            session['user_id'] = user.id_usuario
            session['email'] = user.email
            session['role'] = user.rol

            # Devolver el rol y el mensaje al frontend
            return jsonify({
                'message': 'Login exitoso',
                'role': user.rol
            }), 200
        else:
            return jsonify({'message': 'Credenciales incorrectas'}), 401
    else:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
# Endpoint de logout
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"message": "Logout exitoso"}), 200
    
if __name__ == '__main__':
    app.run(debug=True)