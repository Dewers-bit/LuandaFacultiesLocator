from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from src.database import Database
from src.models.user import User
from src.models.institution import Institution
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_luanda_locator' # Replace with env var in prod

# Initialize Database
db = Database()

# --- Routes ---

@app.route('/')
def home():
    """Renders the login page if not logged in, else map."""
    if 'user_id' in session:
        return redirect(url_for('map_view'))
    return render_template('index.html')

@app.route('/map')
def map_view():
    """Renders the main map page."""
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('map.html')

@app.route('/api/register', methods=['POST'])
def register():
    """Handles user registration."""
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    user_model = User(db)
    if user_model.find_by_email(email):
        return jsonify({"success": False, "message": "E-mail já cadastrado"}), 400
    
    # Create new user
    User(db, email=email, username=username, password=password).create()
    return jsonify({"success": True, "message": "Conta criada com sucesso!"})

@app.route('/api/login', methods=['POST'])
def login():
    """Handles user login and logs the visit."""
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User(db)
    found_user = user.find_by_email(email)

    if found_user and found_user.verify_password(password):
        session['user_id'] = found_user.id
        session['username'] = found_user.username
        session['email'] = found_user.email
        
        # Log the visit
        ip = request.remote_addr
        db.execute("INSERT INTO login_logs (user_id, ip_address) VALUES (?, ?)", (found_user.id, ip))
        
        # Check if admin (using email)
        is_admin = (found_user.email == 'admin@luanda.ao')
        
        return jsonify({"success": True, "message": "Login successful", "is_admin": is_admin})
    
    return jsonify({"success": False, "message": "Credenciais inválidas"}), 401

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Mock forgot password functionality."""
    # In a real app, send email. Here just return success.
    return jsonify({"success": True, "message": "Se o e-mail existir, você receberá instruções."})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Returns visit statistics. Only for admin."""
    # Check admin by email
    if 'user_id' not in session or session.get('email') != 'admin@luanda.ao':
        return jsonify({"error": "Unauthorized"}), 403
    
    # Get total visits
    total_visits = db.query("SELECT COUNT(*) as count FROM login_logs", one=True)['count']
    
    # Get total users
    total_users = db.query("SELECT COUNT(*) as count FROM users", one=True)['count']

    # Get total institutions
    total_institutions = db.query("SELECT COUNT(*) as count FROM institutions", one=True)['count']
    
    # Get recent logs
    recent_logs = db.query("SELECT l.timestamp, u.username, u.email, l.ip_address FROM login_logs l JOIN users u ON l.user_id = u.id ORDER BY l.timestamp DESC LIMIT 10")
    
    logs_data = [{"timestamp": row['timestamp'], "username": f"{row['username']} ({row['email']})", "ip": row['ip_address']} for row in recent_logs]
    
    return jsonify({
        "total_visits": total_visits,
        "total_users": total_users,
        "total_institutions": total_institutions,
        "recent_logs": logs_data
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    return jsonify({"success": True})

@app.route('/api/institutions', methods=['GET'])
def get_institutions():
    """Returns list of all institutions."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    inst_model = Institution(db)
    data = inst_model.get_all()
    return jsonify(data)

# --- Seeding Data (For Demo Purposes) ---
def seed_data():
    """Seeds the database with initial data if empty."""
    user = User(db)
    # Seed Admin with Email
    if not user.find_by_email("admin@luanda.ao"):
        print("Seeding admin user...")
        User(db, email="admin@luanda.ao", username="Administrador", password="Luanda2026").create()

    inst_model = Institution(db)
    if not inst_model.get_all():
        print("Seeding institutions...")
        # Universities in Luanda
        institutions = [
             {
                "name": "Universidade Agostinho Neto (UAN)", 
                "type": "University", 
                "lat": -8.9555, 
                "lng": 13.1633, 
                "details": "Campus Universitário da Camama", 
                "website": "https://www.uan.ao",
                "ranking": "Top 1-2 em Angola",
                "courses": "Engenharia (Civil, Informática, Minas), Medicina, Direito, Economia, Ciências (Biologia, Química), Letras"
            },
            {
                "name": "Universidade Católica de Angola (UCAN)", 
                "type": "University", 
                "lat": -8.8258, 
                "lng": 13.2555, 
                "details": "Rua N. Sra. da Muxima", 
                "website": "https://ucan.edu.ao",
                "ranking": "Top 3 em Angola",
                "courses": "Direito, Economia, Gestão, Engenharia Informática, Psicologia, Teologia, Engenharia de Telecomunicações"
            },
            {
                "name": "Universidade Metodista de Angola", 
                "type": "University", 
                "lat": -8.8185, 
                "lng": 13.2431, 
                "details": "Kinaxixi", 
                "website": "https://uma.ao",
                "ranking": "Top 5-10 em Angola",
                "courses": "Arquitetura, Eng. Civil, Direito, Economia, Gestão, Fisioterapia, Análises Clínicas, Enfermagem"
            },
            {
                "name": "Instituto Superior Politécnico de Tecnologias e Ciências (ISPTEC)", 
                "type": "Institute", 
                "lat": -8.9329, 
                "lng": 13.1762, 
                "details": "Talatona", 
                "website": "https://www.isptec.co.ao",
                "ranking": "Alta Qualidade Técnica",
                "courses": "Eng. Química, Eng. Mecânica, Eng. Informática, Eng. Civil, Economia, Gestão"
            },
            {
                "name": "Universidade Lusíada de Angola", 
                "type": "University", 
                "lat": -8.8368, 
                "lng": 13.2185, 
                "details": "Largo Lusiada", 
                "website": "https://www.ulusiada.ao",
                "ranking": "Reconhecida",
                "courses": "Direito, Arquitetura, Economia, Gestão, Psicologia, Relações Internacionais, Informática"
            },
            {
                "name": "Universidade Técnica de Angola (UTANGA)", 
                "type": "University", 
                "lat": -8.8788, 
                "lng": 13.2655, 
                "details": "Capolo II", 
                "website": "https://www.utanga.co.ao",
                "ranking": "Top 10 (Webometrics)",
                "courses": "Eng. Geologia e Minas, Eng. Informática, Eng. Telecomunicações, Arquitetura, Direito, Psicologia, Gestão"
            },
            {
                "name": "Universidade Privada de Angola (UPRA)", 
                "type": "University", 
                "lat": -8.9161, 
                "lng": 13.1944, 
                "details": "Talatona", 
                "website": "https://upra.ao",
                "ranking": "Boa Reputação Saúde",
                "courses": "Medicina, Odontologia, Enfermagem, Fisioterapia, Eng. Civil, Arquitetura, Comunicação Social, Relações Internacionais"
            },
            {
                "name": "Universidade de Belas", 
                "type": "University", 
                "lat": -8.9145, 
                "lng": 13.1850, 
                "details": "Benfica/Talatona", 
                "website": "https://www.unibelas-angola.com",
                "ranking": "N/A",
                "courses": "Direito, Psicologia, Fisioterapia, Enfermagem, Gestão Hospitalar, Eng. Petróleo, Eng. Informática"
            },
            {
                "name": "Universidade Independente de Angola (UnIA)", 
                "type": "University", 
                "lat": -8.9220, 
                "lng": 13.1915, 
                "details": "Morro Bento", 
                "website": "https://unia.ao",
                "ranking": "N/A",
                "courses": "Eng. Civil, Eng. Informática, Direito, Economia, Arquitetura, Ciências da Comunicação"
            },
            {
                "name": "Universidade Jean Piaget de Angola", 
                "type": "University", 
                "lat": -8.9350, 
                "lng": 13.3510, 
                "details": "Viana", 
                "website": "https://unipiaget-angola.org",
                "ranking": "N/A",
                "courses": "Medicina, Enfermagem, Farmácia, Direito, Eng. Civil, Eng. Petróleos, Economia"
            },
            {
                "name": "Universidade Gregório Semedo", 
                "type": "University", 
                "lat": -8.8650, 
                "lng": 13.2900, 
                "details": "Talatona", 
                "website": "https://www.ugs.edu.ao",
                "ranking": "N/A",
                "courses": "Direito, Gestão Comercial e Marketing, Eng. Informática, Organização e Gestão de Empresas"
            },
            {
                "name": "Instituto Superior de Ciências Sociais e Relações Internacionais (CIS)", 
                "type": "Institute", 
                "lat": -8.9250, 
                "lng": 13.1950, 
                "details": "Talatona", 
                "website": "https://cis-edu.ao",
                "ranking": "N/A",
                "courses": "Relações Internacionais, Ciência Política, Direito, Economia, Gestão de RH, Psicologia"
            },
            {
                "name": "Universidade de Luanda (UniLuanda)", 
                "type": "University", 
                "lat": -8.9400, 
                "lng": 13.1800, 
                "details": "Sapu, Talatona", 
                "website": "https://www.uniluanda.ao",
                "ranking": "Emergente",
                "courses": "Eng. Telecomunicações (Ex-ISUTIC), Artes, Serviço Social, Gestão"
            },
            {
                "name": "Instituto Superior Técnico de Angola (ISTA)", 
                "type": "Institute", 
                "lat": -8.8450, 
                "lng": 13.2800, 
                "details": "Palanca", 
                "website": "http://www.ista-angola.com",
                "ranking": "N/A",
                "courses": "Eng. Informática, Eng. Telecomunicações, Direito, Psicologia, Comunicação Social"
            },
            {
                "name": "Universidade Óscar Ribas", 
                "type": "University", 
                "lat": -8.9216, 
                "lng": 13.1830, 
                "details": "Talatona", 
                "website": "https://www.uor.edu.ao",
                "ranking": "N/A",
                "courses": "Direito, Psicologia, Relações Internacionais, Eng. Civil, Eng. Informática, Gestão e Marketing"
            },
            {
                "name": "Instituto Superior de Telecomunicações (ISUTIC)", 
                "type": "Institute", 
                "lat": -8.8195, 
                "lng": 13.2676, 
                "details": "Rangel", 
                "website": "https://www.isutic.gov.ao",
                "ranking": "Especializada TI",
                "courses": "Eng. Telecomunicações, Eng. Informática"
            },
            {
                "name": "Instituto Superior Politécnico do Cazenga (ISPOCA)", 
                "type": "Institute", 
                "lat": -8.8162, 
                "lng": 13.3172, 
                "details": "Cazenga", 
                "website": "https://ispoca.ao",
                "ranking": "Regional",
                "courses": "Enfermagem, Direito, Arquitetura, Eng. Informática, Gestão"
            },
            {
                "name": "Instituto Superior Dom Bosco", 
                "type": "Institute", 
                "lat": -8.8400, 
                "lng": 13.2650, 
                "details": "Palanca", 
                "website": "https://dombosco.ao",
                "ranking": "Filosófico/Pedagógico",
                "courses": "Filosofia, Pedagogia, Educação"
            },
            {
                "name": "Instituto Superior João Paulo II", 
                "type": "Institute", 
                "lat": -8.8280, 
                "lng": 13.2350, 
                "details": "Maianga", 
                "website": "https://isupjpii.edu.ao",
                "ranking": "Católica",
                "courses": "Ciências Sociais, Educação Moral, Serviço Social"
            },
            {
                "name": "Instituto Superior Politécnico Alvorecer da Juventude (ISPAJ)", 
                "type": "Institute", 
                "lat": -8.8750, 
                "lng": 13.2100, 
                "details": "Nova Vida", 
                "website": "https://ispaj.co.ao",
                "ranking": "N/A",
                "courses": "Direito, Economia, Gestão, Eng. Informática, Relações Internacionais"
            },
            {
                "name": "Instituto Superior de Ciências da Educação (ISCED)", 
                "type": "Institute", 
                "lat": -8.9100, 
                "lng": 13.1900, 
                "details": "Belas", 
                "website": "https://isced.edu.ao",
                "ranking": "Educação",
                "courses": "Ensino de (História, Matemática, Francês, Inglês, Português), Ciências da Educação"
            },
            {
                "name": "Instituto Superior de Ciências de Saúde (ISCISA)", 
                "type": "Institute", 
                "lat": -8.8250, 
                "lng": 13.2340, 
                "details": "Luanda", 
                "website": "https://iscisa.ao",
                "ranking": "Saúde Pública",
                "courses": "Enfermagem, Farmácia, Psicologia Clínica, Análises Clínicas"
            },
             {
                "name": "Academia de Ciências Sociais e Tecnologias (ACITE)", 
                "type": "Institute", 
                "lat": -8.8900, 
                "lng": 13.2200, 
                "details": "Kilamba Kiaxi", 
                "website": "#",
                "ranking": "Especializada",
                "courses": "Ciências Sociais, Tecnologias, Segurança"
            },
            {
                "name": "Instituto Superior Politécnico Metropolitano de Angola (IMETRO)", 
                "type": "Institute", 
                "lat": -8.9280, 
                "lng": 13.1880, 
                "details": "Morro Bento", 
                "website": "https://www.imetro.ao",
                "ranking": "N/A",
                "courses": "Gestão, Direito, Economia, Eng. Informática, Cinema e TV"
            }
        ]
        for item in institutions:
            Institution(db, 
                        name=item['name'], 
                        type=item['type'], 
                        latitude=item['lat'], 
                        longitude=item['lng'], 
                        details=item['details'], 
                        website=item['website'],
                        ranking=item.get('ranking', 'N/A'),
                        courses=item.get('courses', 'Vários cursos disponíveis')
            ).create()

if __name__ == '__main__':
    seed_data()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
