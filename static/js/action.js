// API Service للتواصل مع Flask backend
const API = {
    async login(emailOrPhone, password) {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ emailOrPhone, password })
            });
            
            const result = await response.json();
            
            if (result.success) {
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userData', JSON.stringify(result.user));
                
                const users = JSON.parse(localStorage.getItem('users') || '[]');
                const existingIndex = users.findIndex(u => u.id === result.user.id);
                if (existingIndex === -1) {
                    users.push(result.user);
                } else {
                    users[existingIndex] = result.user;
                }
                localStorage.setItem('users', JSON.stringify(users));
            }
            
            return result;
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'خطأ في الاتصال بالخادم' };
        }
    },

    async register(userData) {
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userData', JSON.stringify(result.user));
                
                const users = JSON.parse(localStorage.getItem('users') || '[]');
                users.push(result.user);
                localStorage.setItem('users', JSON.stringify(users));
            }
            
            return result;
        } catch (error) {
            console.error('Register error:', error);
            return { success: false, message: 'خطأ في الاتصال بالخادم' };
        }
    },

    async forgotPassword(emailOrPhone) {
        try {
            const response = await fetch('/api/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ emailOrPhone })
            });
            return await response.json();
        } catch (error) {
            return { success: false, message: 'خطأ في الاتصال بالخادم' };
        }
    },

    async logout() {
        try {
            const response = await fetch('/api/logout', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                localStorage.removeItem('isLoggedIn');
                localStorage.removeItem('userData');
                localStorage.removeItem('cart');
                localStorage.removeItem('tempOrder');
            }
            
            return result;
        } catch (error) {
            return { success: false, message: 'خطأ في تسجيل الخروج' };
        }
    },

    async getUserData() {
        try {
            const response = await fetch('/api/user-data');
            return await response.json();
        } catch (error) {
            return { success: false, message: 'غير مصرح' };
        }
    },

    async createOrder(orderData) {
        try {
            const response = await fetch('/api/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });
            return await response.json();
        } catch (error) {
            return { success: false, message: 'خطأ في إنشاء الطلب' };
        }
    },

    async getOrders() {
        try {
            const response = await fetch('/api/orders');
            return await response.json();
        } catch (error) {
            return { success: false, message: 'خطأ في جلب الطلبات' };
        }
    },

    // Company Product APIs
    async getCompanyProducts() {
        try {
            const response = await fetch('/api/company/products');
            return await response.json();
        } catch (error) {
            return { success: false, message: 'خطأ في جلب المنتجات' };
        }
    },

    async createCompanyProduct(productData) {
        try {
            const response = await fetch('/api/company/products', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(productData)
            });
            return await response.json();
        } catch (error) {
            return { success: false, message: 'خطأ في إضافة المنتج' };
        }
    },

    async updateCompanyProduct(productId, productData) {
        try {
            const response = await fetch(`/api/company/products/${productId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(productData)
            });
            return await response.json();
        } catch (error) {
            return { success: false, message: 'خطأ في تحديث المنتج' };
        }
    },

    async deleteCompanyProduct(productId) {
        try {
            const response = await fetch(`/api/company/products/${productId}`, {
                method: 'DELETE'
            });
            return await response.json();
        } catch (error) {
            return { success: false, message: 'خطأ في حذف المنتج' };
        }
    }
};

// Utility functions
function showMessage(message, type = 'info') {
    const existingMessages = document.querySelectorAll('.fixed.top-4.right-4');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transition-all duration-300 ${
        type === 'success' ? 'bg-green-100 text-green-800 border border-green-300' :
        type === 'error' ? 'bg-red-100 text-red-800 border border-red-300' :
        'bg-blue-100 text-blue-800 border border-blue-300'
    }`;
    
    messageDiv.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${
                type === 'success' ? 'fa-check-circle' :
                type === 'error' ? 'fa-exclamation-circle' :
                'fa-info-circle'
            } ml-3 text-xl"></i>
            <span>${message}</span>
            <button class="mr-auto text-xl mr-4" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        if (messageDiv.parentElement) {
            messageDiv.remove();
        }
    }, 5000);
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^01[0125][0-9]{8}$/;
    return re.test(phone);
}

function formatDate(dateString) {
    if (!dateString) return '--';
    try {
        const date = new Date(dateString);
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('ar-EG', options);
    } catch (e) {
        return '--';
    }
}

function formatDateTime(dateString) {
    if (!dateString) return '--';
    try {
        const date = new Date(dateString);
        const options = { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return date.toLocaleDateString('ar-EG', options);
    } catch (e) {
        return '--';
    }
}

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Eco Paper Recycling Platform loaded');
    
    const protectedPages = ['home.html', 'dashboard.html', 'profile.html', 'orders-history.html', 'order.html', 'payment.html', 'order-tracking.html', 'order-confirm.html', 'company_products.html', 'company_orders.html', 'admin_products.html', 'admin_orders.html'];
    const currentPage = window.location.pathname.split('/').pop();
    
    if (protectedPages.includes(currentPage)) {
        API.getUserData().then(response => {
            if (!response.success) {
                window.location.href = '/login';
            } else {
                localStorage.setItem('userData', JSON.stringify(response.user));
                updateUIForLoggedInUser(response.user);
            }
        }).catch(() => {
            window.location.href = '/login';
        });
    }
    
    initMobileMenu();
    initAuthButtons();
});

function updateUIForLoggedInUser(userData) {
    const userNameElements = document.querySelectorAll('.user-name');
    userNameElements.forEach(el => {
        el.textContent = userData.name || 'المستخدم';
    });
}

function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            const menu = document.getElementById('mobileMenu');
            if (menu) {
                menu.classList.toggle('hidden');
            }
        });
    }
}

function initAuthButtons() {
    const logoutBtns = document.querySelectorAll('#logoutBtn, #logoutBtnMobile');
    logoutBtns.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', async function(e) {
                e.preventDefault();
                if (confirm('هل تريد تسجيل الخروج؟')) {
                    const result = await API.logout();
                    if (result.success) {
                        window.location.href = '/index';
                    }
                }
            });
        }
    });
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        API,
        showMessage,
        validateEmail,
        validatePhone,
        formatDate,
        formatDateTime
    };
}