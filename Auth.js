class Auth {
    constructor() {
        // Forms
        this.loginForm = document.getElementById('loginForm');
        this.registerForm = document.getElementById('registerForm');

        // Tabs
        this.tabLogin = document.getElementById('tabLogin');
        this.tabRegister = document.getElementById('tabRegister');

        // Errors
        this.loginError = document.getElementById('loginError');
        this.regError = document.getElementById('regError');

        // Logout
        this.logoutBtn = document.getElementById('logoutBtn');

        // Forgot Password
        this.forgotLink = document.getElementById('forgotPasswordLink');
        this.forgotModal = document.getElementById('forgotModal');
        this.closeForgotBtn = document.getElementById('closeForgotBtn');
        this.sendRecoveryBtn = document.getElementById('sendRecoveryBtn');

        this.bindEvents();
    }

    bindEvents() {
        // Login Logic
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
            this.tabLogin.addEventListener('click', () => this.switchTab('login'));
            this.tabRegister.addEventListener('click', () => this.switchTab('register'));

            this.registerForm.addEventListener('submit', (e) => this.handleRegister(e));

            // Forgot Password
            this.forgotLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.forgotModal.classList.remove('hidden');
            });
            this.closeForgotBtn.addEventListener('click', () => this.forgotModal.classList.add('hidden'));
            this.sendRecoveryBtn.addEventListener('click', () => {
                alert('Solicitação enviada (Simulação).');
                this.forgotModal.classList.add('hidden');
            });
        }

        // Logout Logic
        if (this.logoutBtn) {
            this.logoutBtn.addEventListener('click', async () => {
                try {
                    await fetch('/api/logout', { method: 'POST' });
                    // Force redirect to login page
                    window.location.href = '/';
                } catch (err) {
                    console.error("Logout failed", err);
                    window.location.href = '/'; // Redirect anyway
                }
            });
        }
    }

    switchTab(tab) {
        if (tab === 'login') {
            this.loginForm.classList.add('active');
            this.registerForm.classList.remove('active');
            this.tabLogin.classList.add('active');
            this.tabRegister.classList.remove('active');
        } else {
            this.loginForm.classList.remove('active');
            this.registerForm.classList.add('active');
            this.tabLogin.classList.remove('active');
            this.tabRegister.classList.add('active');
        }
        this.loginError.textContent = '';
        this.regError.textContent = '';
    }

    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        this.loginError.textContent = 'Autenticando...';

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await response.json();

            if (data.success) {
                window.location.href = '/map';
            } else {
                this.loginError.textContent = data.message;
            }
        } catch (err) {
            this.loginError.textContent = 'Erro de conexão.';
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        this.regError.textContent = 'Criando conta...';

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await response.json();

            if (data.success) {
                alert('Conta criada! Faça login com seu e-mail.');
                this.switchTab('login');
            } else {
                this.regError.textContent = data.message;
            }
        } catch (err) {
            this.regError.textContent = 'Erro de conexão.';
        }
    }
}

new Auth();
