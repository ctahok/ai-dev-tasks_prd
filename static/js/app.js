/**
 * Azerbaijani Court Case Sorter - Frontend JavaScript
 * Handles all client-side functionality
 */

class CourtCaseApp {
    constructor() {
        this.baseURL = window.location.origin;
        this.token = localStorage.getItem('authToken');
        this.currentUser = null;
        this.filterOptions = {};
        this.selectedFilters = {};

        this.initializeApp();
    }

    initializeApp() {
        this.setupEventListeners();
        this.checkAuthentication();
        this.loadFilterOptions();
        this.loadSystemStats();
        this.initializeChat();
    }

    setupEventListeners() {
        // Authentication
        document.getElementById('loginBtn').addEventListener('click', () => this.showLoginModal());
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
        document.getElementById('loginForm').addEventListener('submit', (e) => this.handleLogin(e));

        // File Upload
        document.getElementById('uploadForm').addEventListener('submit', (e) => this.handleUpload(e));
        document.getElementById('fileInput').addEventListener('change', (e) => this.validateFiles(e));

        // Search
        document.getElementById('searchBtn').addEventListener('click', () => this.performSearch());
        document.getElementById('searchQuery').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });

        // Filters
        document.getElementById('applyFiltersBtn').addEventListener('click', () => this.applyFilters());
        document.getElementById('clearFiltersBtn').addEventListener('click', () => this.clearFilters());

        // Chat
        document.getElementById('chatForm').addEventListener('submit', (e) => this.handleChat(e));
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleChat(e);
        });

        // Document Details Modal
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('view-document')) {
                this.showDocumentDetails(e.target.dataset.docId);
            }
        });
    }

    async checkAuthentication() {
        if (this.token) {
            try {
                const response = await fetch(`${this.baseURL}/verify-token`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    }
                });

                if (response.ok) {
                    const userData = await response.json();
                    this.currentUser = userData;
                    this.updateUIForAuthenticatedUser();
                } else {
                    this.token = null;
                    localStorage.removeItem('authToken');
                    this.updateUIForUnauthenticatedUser();
                }
            } catch (error) {
                console.error('Authentication check failed:', error);
                this.updateUIForUnauthenticatedUser();
            }
        } else {
            this.updateUIForUnauthenticatedUser();
        }
    }

    updateUIForAuthenticatedUser() {
        const userInfo = document.getElementById('userInfo');
        const loginBtn = document.getElementById('loginBtn');
        const logoutBtn = document.getElementById('logoutBtn');

        if (this.currentUser) {
            userInfo.textContent = `Salam, ${this.currentUser.username}!`;
            loginBtn.style.display = 'none';
            logoutBtn.style.display = 'inline-block';
        }
    }

    updateUIForUnauthenticatedUser() {
        const userInfo = document.getElementById('userInfo');
        const loginBtn = document.getElementById('loginBtn');
        const logoutBtn = document.getElementById('logoutBtn');

        userInfo.textContent = 'Giriş edilməmiş';
        loginBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
    }

    showLoginModal() {
        const modal = new bootstrap.Modal(document.getElementById('loginModal'));
        modal.show();
    }

    async handleLogin(e) {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${this.baseURL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.token;
                localStorage.setItem('authToken', this.token);
                this.currentUser = data.user;

                this.updateUIForAuthenticatedUser();

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
                modal.hide();

                // Clear form
                document.getElementById('loginForm').reset();

                this.showAlert('success', 'Uğurla giriş edildi!');
            } else {
                const error = await response.json();
                this.showAlert('danger', error.message || 'Giriş uğursuz oldu');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showAlert('danger', 'Giriş zamanı xəta baş verdi');
        }
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('authToken');
        this.updateUIForUnauthenticatedUser();
        this.showAlert('info', 'Çıxış edildi');
    }

    validateFiles(e) {
        const files = Array.from(e.target.files);
        const validFiles = [];
        const invalidFiles = [];

        files.forEach(file => {
            if (file.type === 'application/pdf' || file.name.endsWith('.zip')) {
                validFiles.push(file);
            } else {
                invalidFiles.push(file.name);
            }
        });

        if (invalidFiles.length > 0) {
            this.showAlert('warning', `Bu fayllar dəstəklənmir: ${invalidFiles.join(', ')}`);
        }

        return validFiles.length > 0;
    }

    async handleUpload(e) {
        e.preventDefault();

        if (!this.token) {
            this.showAlert('warning', 'Yükləmə üçün giriş etməlisiniz');
            return;
        }

        const files = document.getElementById('fileInput').files;
        if (files.length === 0) {
            this.showAlert('warning', 'Zəhmət olmasa fayl seçin');
            return;
        }

        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }

        this.showUploadProgress();

        try {
            const response = await fetch(`${this.baseURL}/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            this.hideUploadProgress();

            if (response.ok) {
                const result = await response.json();
                this.displayUploadResults(result);
                this.showAlert('success', `Yükləmə tamamlandı: ${result.processed} uğurlu, ${result.failed} uğursuz`);
            } else {
                const error = await response.json();
                this.showAlert('danger', error.message || 'Yükləmə uğursuz oldu');
            }
        } catch (error) {
            this.hideUploadProgress();
            console.error('Upload error:', error);
            this.showAlert('danger', 'Yükləmə zamanı xəta baş verdi');
        }
    }

    showUploadProgress() {
        const progressContainer = document.getElementById('uploadProgress');
        const progressBar = progressContainer.querySelector('.progress-bar');
        const statusDiv = document.getElementById('uploadStatus');

        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';
        statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Yüklənir...';

        // Simulate progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;

            progressBar.style.width = progress + '%';

            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 200);
    }

    hideUploadProgress() {
        document.getElementById('uploadProgress').style.display = 'none';
    }

    displayUploadResults(result) {
        const resultsDiv = document.getElementById('uploadResults');
        let html = '<h6>Yükləmə Nəticələri:</h6>';

        if (result.processed_documents && result.processed_documents.length > 0) {
            html += '<div class="mb-2"><strong>Uğurlu:</strong></div>';
            result.processed_documents.forEach(doc => {
                html += `<div class="upload-result success"><i class="fas fa-check"></i> ${doc.filename}</div>`;
            });
        }

        if (result.failed_documents && result.failed_documents.length > 0) {
            html += '<div class="mb-2"><strong>Uğursuz:</strong></div>';
            result.failed_documents.forEach(doc => {
                html += `<div class="upload-result error"><i class="fas fa-times"></i> ${doc}</div>`;
            });
        }

        resultsDiv.innerHTML = html;
        resultsDiv.style.display = 'block';
    }

    async performSearch() {
        if (!this.token) {
            this.showAlert('warning', 'Axtarış üçün giriş etməlisiniz');
            return;
        }

        const query = document.getElementById('searchQuery').value.trim();
        if (!query) {
            this.showAlert('warning', 'Axtarış sorğusu daxil edin');
            return;
        }

        this.showLoading('searchResults');

        try {
            const response = await fetch(`${this.baseURL}/search?query=${encodeURIComponent(query)}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            this.hideLoading('searchResults');

            if (response.ok) {
                const results = await response.json();
                this.displaySearchResults(results.results);
            } else {
                const error = await response.json();
                this.showAlert('danger', error.message || 'Axtarış uğursuz oldu');
            }
        } catch (error) {
            this.hideLoading('searchResults');
            console.error('Search error:', error);
            this.showAlert('danger', 'Axtarış zamanı xəta baş verdi');
        }
    }

    displaySearchResults(results) {
        const resultsDiv = document.getElementById('searchResults');

        if (!results || results.length === 0) {
            resultsDiv.innerHTML = '<div class="alert alert-info">Nəticə tapılmadı</div>';
            return;
        }

        let html = `<div class="alert alert-success">${results.length} nəticə tapıldı</div>`;

        results.forEach((result, index) => {
            const metadata = result.metadata || {};
            html += `
                <div class="search-result">
                    <h6>${metadata.case_number || `Sənəd ${index + 1}`}</h6>
                    <div class="metadata">
                        <span><i class="fas fa-gavel"></i> ${metadata.court_name || 'Naməlum Məhkəmə'}</span>
                        <span><i class="fas fa-user"></i> ${metadata.judge || 'Naməlum Hakim'}</span>
                        <span><i class="fas fa-calendar"></i> ${metadata.year || 'Naməlum İl'}</span>
                    </div>
                    <div class="content">
                        ${metadata.decision_type ? `<strong>${metadata.decision_type}</strong><br/>` : ''}
                        ${result.content ? result.content.substring(0, 200) + '...' : 'Məzmun mövcud deyil'}
                    </div>
                    <button class="btn btn-sm btn-outline-primary mt-2 view-document"
                            data-doc-id="${result.id || result.document_id}">
                        <i class="fas fa-eye"></i> Detalları Göstər
                    </button>
                </div>
            `;
        });

        resultsDiv.innerHTML = html;
    }

    async loadFilterOptions() {
        if (!this.token) return;

        try {
            const response = await fetch(`${this.baseURL}/filters`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                this.filterOptions = await response.json();
                this.createFilterControls();
            }
        } catch (error) {
            console.error('Error loading filter options:', error);
        }
    }

    createFilterControls() {
        const container = document.getElementById('filterControls');
        container.innerHTML = '';

        Object.entries(this.filterOptions).forEach(([filterType, options]) => {
            if (options && options.length > 0) {
                const filterDiv = document.createElement('div');
                filterDiv.className = 'col-md-6 col-lg-4 filter-control';

                const label = this.getFilterLabel(filterType);
                filterDiv.innerHTML = `
                    <label for="filter-${filterType}">${label}</label>
                    <select class="form-select" id="filter-${filterType}">
                        <option value="">Hamısı</option>
                        ${options.map(option => `<option value="${option}">${option}</option>`).join('')}
                    </select>
                `;

                container.appendChild(filterDiv);
            }
        });
    }

    getFilterLabel(filterType) {
        const labels = {
            'judge': 'Hakim',
            'court': 'Məhkəmə',
            'case_type': 'İşin Növü',
            'district': 'Rayon',
            'year': 'İl',
            'decision_type': 'Qərar Növü'
        };
        return labels[filterType] || filterType;
    }

    applyFilters() {
        if (!this.token) {
            this.showAlert('warning', 'Filtrləmə üçün giriş etməlisiniz');
            return;
        }

        // Collect selected filters
        this.selectedFilters = {};
        Object.keys(this.filterOptions).forEach(filterType => {
            const select = document.getElementById(`filter-${filterType}`);
            if (select && select.value) {
                this.selectedFilters[filterType] = select.value;
            }
        });

        if (Object.keys(this.selectedFilters).length === 0) {
            this.showAlert('warning', 'Ən azı bir filtr seçin');
            return;
        }

        this.showLoading('filterResults');

        // Build query string
        const params = new URLSearchParams();
        Object.entries(this.selectedFilters).forEach(([key, value]) => {
            params.append(key, value);
        });

        fetch(`${this.baseURL}/search?${params}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        })
        .then(response => response.json())
        .then(data => {
            this.hideLoading('filterResults');
            this.displaySearchResults(data.results);
        })
        .catch(error => {
            this.hideLoading('filterResults');
            console.error('Filter error:', error);
            this.showAlert('danger', 'Filtrləmə zamanı xəta baş verdi');
        });
    }

    clearFilters() {
        Object.keys(this.filterOptions).forEach(filterType => {
            const select = document.getElementById(`filter-${filterType}`);
            if (select) {
                select.value = '';
            }
        });
        this.selectedFilters = {};
        document.getElementById('filterResults').innerHTML = '';
    }

    initializeChat() {
        this.addChatMessage('bot', 'Salam! Məhkəmə sənədləri ilə bağlı suallarınızı verə bilərsiniz.');
    }

    async handleChat(e) {
        e.preventDefault();

        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();

        if (!message) return;

        // Add user message
        this.addChatMessage('user', message);
        chatInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch(`${this.baseURL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': `Bearer ${this.token}`
                },
                body: `message=${encodeURIComponent(message)}`
            });

            this.hideTypingIndicator();

            if (response.ok) {
                const data = await response.json();
                this.addChatMessage('bot', data.response);
            } else {
                this.addChatMessage('bot', 'Bağışlayın, cavab verə bilmirəm. Yenidən cəhd edin.');
            }
        } catch (error) {
            this.hideTypingIndicator();
            console.error('Chat error:', error);
            this.addChatMessage('bot', 'Xəta baş verdi. Yenidən cəhd edin.');
        }
    }

    addChatMessage(sender, message) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;

        const timestamp = new Date().toLocaleTimeString('az-AZ', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <small class="text-muted">${timestamp}</small><br/>
            ${message}
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = '<i class="fas fa-ellipsis-h"></i> Yazır...';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async showDocumentDetails(docId) {
        try {
            const response = await fetch(`${this.baseURL}/document/${docId}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const document = await response.json();
                this.displayDocumentModal(document);
            } else {
                this.showAlert('danger', 'Sənəd detallarını yükləmək mümkün olmadı');
            }
        } catch (error) {
            console.error('Error loading document details:', error);
            this.showAlert('danger', 'Sənəd detallarını yükləmək zamanı xəta baş verdi');
        }
    }

    displayDocumentModal(document) {
        const modal = new bootstrap.Modal(document.getElementById('documentModal'));
        const detailsDiv = document.getElementById('documentDetails');

        const metadata = document.metadata || {};

        detailsDiv.innerHTML = `
            <div class="document-detail">
                <label>Fayl adı:</label>
                <div class="value">${document.filename || 'Naməlum'}</div>
            </div>
            <div class="document-detail">
                <label>Məhkəmə:</label>
                <div class="value">${metadata.court_name || 'Naməlum'}</div>
            </div>
            <div class="document-detail">
                <label>İş nömrəsi:</label>
                <div class="value">${metadata.case_number || 'Naməlum'}</div>
            </div>
            <div class="document-detail">
                <label>Hakim:</label>
                <div class="value">${metadata.judge || 'Naməlum'}</div>
            </div>
            <div class="document-detail">
                <label>İşin növü:</label>
                <div class="value">${metadata.case_type || 'Naməlum'}</div>
            </div>
            <div class="document-detail">
                <label>Rayon:</label>
                <div class="value">${metadata.district || 'Naməlum'}</div>
            </div>
            <div class="document-detail">
                <label>Qərar növü:</label>
                <div class="value">${metadata.decision_type || 'Naməlum'}</div>
            </div>
            <div class="document-detail">
                <label>İl:</label>
                <div class="value">${metadata.year || 'Naməlum'}</div>
            </div>
            ${metadata.parties ? `
                <div class="document-detail">
                    <label>Tərəflər:</label>
                    <div class="value">${metadata.parties.join(', ')}</div>
                </div>
            ` : ''}
            <div class="document-detail">
                <label>Məzmun:</label>
                <div class="value" style="max-height: 300px; overflow-y: auto;">${document.text_content || 'Məzmun mövcud deyil'}</div>
            </div>
        `;

        modal.show();
    }

    async loadSystemStats() {
        if (!this.token) return;

        try {
            const response = await fetch(`${this.baseURL}/stats`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const stats = await response.json();
                this.displaySystemStats(stats);
            }
        } catch (error) {
            console.error('Error loading system stats:', error);
        }
    }

    displaySystemStats(stats) {
        const statsDiv = document.getElementById('systemStats');

        statsDiv.innerHTML = `
            <div class="row">
                <div class="col-6">
                    <div class="stat-item">
                        <div class="stat-number">${stats.total_documents || 0}</div>
                        <div class="stat-label">Ümumi Sənəd</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="stat-item">
                        <div class="stat-number">${stats.processed_documents || 0}</div>
                        <div class="stat-label">Emal Edilmiş</div>
                    </div>
                </div>
            </div>
        `;
    }

    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add('loading');
            element.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Yüklənir...</div>';
        }
    }

    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('loading');
        }
    }

    showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of the main container
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CourtCaseApp();
});

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('az-AZ');
}

function truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
