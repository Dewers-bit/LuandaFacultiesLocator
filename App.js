class App {
    constructor() {
        this.mapManager = new MapManager('map', (inst) => this.showInfoCard(inst));
        this.institutionList = document.getElementById('institutionList');
        this.searchInput = document.getElementById('searchInput');

        // Info Card Elements
        this.infoOverlay = document.getElementById('infoOverlay');
        this.closeInfoBtn = document.getElementById('closeInfoBtn');
        this.infoTitle = document.getElementById('infoTitle');
        this.infoType = document.getElementById('infoType');
        this.infoDetails = document.getElementById('infoDetails');
        this.infoRanking = document.getElementById('infoRanking');
        this.infoCourses = document.getElementById('infoCourses');
        this.infoWebsite = document.getElementById('infoWebsite');

        this.institutions = [];

        // Admin Elements
        this.adminBadge = document.getElementById('adminBadge');
        this.adminModal = document.getElementById('adminModal');
        this.closeAdminBtn = document.getElementById('closeAdminBtn');

        this.loadData();
        this.checkAdmin(); // Check if current user is admin
        this.bindEvents();
    }

    async checkAdmin() {
        try {
            // Force fetch with credentials explicitly if needed
            const response = await fetch('/api/admin/stats', { cache: "no-store" });

            if (response.ok) {
                console.log("Admin identified. Showing badge.");
                this.adminBadge.classList.remove('force-hidden'); // Show it

                // Re-bind to ensure clean events
                const newBadge = this.adminBadge.cloneNode(true);
                this.adminBadge.parentNode.replaceChild(newBadge, this.adminBadge);
                this.adminBadge = newBadge;
                this.adminBadge.addEventListener('click', () => this.loadStats());

                // Fix close admin btn
                const newClose = this.closeAdminBtn.cloneNode(true);
                this.closeAdminBtn.parentNode.replaceChild(newClose, this.closeAdminBtn);
                this.closeAdminBtn = newClose;
                this.closeAdminBtn.addEventListener('click', () => this.adminModal.classList.add('hidden'));
            } else {
                console.log("User is not admin. Hiding badge.");
                this.adminBadge.classList.add('force-hidden');
            }
        } catch (e) {
            console.error("Check admin failed", e);
            this.adminBadge.classList.add('force-hidden');
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/admin/stats');
            const data = await response.json();

            document.getElementById('totalVisits').textContent = data.total_visits;
            document.getElementById('totalUsers').textContent = data.total_users;
            document.getElementById('totalInstitutions').textContent = data.total_institutions;

            const tbody = document.getElementById('logTableBody');
            tbody.innerHTML = '';

            data.recent_logs.forEach(log => {
                const row = document.createElement('tr');
                row.innerHTML = `<td>${new Date(log.timestamp).toLocaleString()}</td><td>${log.username}</td><td>${log.ip}</td>`;
                tbody.appendChild(row);
            });

            this.adminModal.classList.remove('hidden');
        } catch (e) { console.error(e); }
    }

    async loadData() {
        try {
            const response = await fetch('/api/institutions');
            if (response.status === 401) {
                window.location.href = '/';
                return;
            }
            this.institutions = await response.json();
            this.renderList(this.institutions);
            this.mapManager.addMarkers(this.institutions);
        } catch (err) {
            console.error("Failed to load institutions", err);
        }
    }

    bindEvents() {
        this.searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = this.institutions.filter(inst =>
                inst.name.toLowerCase().includes(term) ||
                inst.type.toLowerCase().includes(term)
            );
            this.renderList(filtered);
        });

        this.closeInfoBtn.addEventListener('click', () => {
            this.hideInfoCard();
        });

        // Close on outside click
        this.infoOverlay.addEventListener('click', (e) => {
            if (e.target === this.infoOverlay) {
                this.hideInfoCard();
            }
        });

        // Admin modal outside click
        this.adminModal.addEventListener('click', (e) => {
            if (e.target === this.adminModal) {
                this.adminModal.classList.add('hidden');
            }
        });
    }

    showInfoCard(inst) {
        this.infoTitle.textContent = inst.name;
        this.infoType.textContent = inst.type;
        this.infoDetails.textContent = inst.details;
        this.infoRanking.textContent = inst.ranking || 'N/A';
        this.infoCourses.textContent = inst.courses || 'Informação não disponível';
        this.infoWebsite.href = inst.website;

        this.infoOverlay.classList.remove('hidden');
    }

    hideInfoCard() {
        this.infoOverlay.classList.add('hidden');
    }

    renderList(items) {
        this.institutionList.innerHTML = '';
        items.forEach(inst => {
            const li = document.createElement('li');
            li.className = 'institution-item';
            li.innerHTML = `
                <h3>${inst.name}</h3>
                <p>${inst.type}</p>
            `;
            li.addEventListener('click', () => {
                this.mapManager.focusMarker(inst.id);
            });
            this.institutionList.appendChild(li);
        });
    }
}

if (document.getElementById('map')) {
    new App();
}
