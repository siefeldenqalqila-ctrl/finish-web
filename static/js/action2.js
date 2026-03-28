// Sync users from localStorage to server
async function syncUsers() {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const userData = JSON.parse(localStorage.getItem('userData') || 'null');
    
    if (userData && !users.find(u => u.id === userData.id)) {
        users.push(userData);
        localStorage.setItem('users', JSON.stringify(users));
    }
}

syncUsers();

const users = JSON.parse(localStorage.getItem('users') || '[]');

function login(emailOrPhone, password) {
    if (!emailOrPhone || !password) {
        return { success: false, message: 'يرجى ملء جميع الحقول' };
    }
    
    const user = users.find(u => 
        (u.email === emailOrPhone || u.phone === emailOrPhone) && 
        u.password === password
    );
    
    if (user) {
        const userData = {
            id: user.id,
            name: user.name,
            email: user.email,
            phone: user.phone,
            type: user.type || 'individual',
            role: user.role || 'customer'
        };
        
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('userData', JSON.stringify(userData));
        
        return { 
            success: true, 
            message: 'تم تسجيل الدخول بنجاح',
            user: userData
        };
    } else {
        return { 
            success: false, 
            message: 'البريد الإلكتروني/الهاتف أو كلمة المرور غير صحيحة' 
        };
    }
}

function register(userData) {
    const requiredFields = ['name', 'email', 'phone', 'password', 'confirmPassword'];
    for (const field of requiredFields) {
        if (!userData[field]) {
            return { success: false, message: `يرجى ملء حقل ${field}` };
        }
    }
    
    if (userData.password !== userData.confirmPassword) {
        return { success: false, message: 'كلمتا المرور غير متطابقتين' };
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(userData.email)) {
        return { success: false, message: 'البريد الإلكتروني غير صالح' };
    }
    
    const phoneRegex = /^01[0125][0-9]{8}$/;
    if (!phoneRegex.test(userData.phone)) {
        return { success: false, message: 'رقم الهاتف غير صالح' };
    }
    
    const existingUser = users.find(u => u.email === userData.email);
    if (existingUser) {
        return { success: false, message: 'البريد الإلكتروني مسجل مسبقاً' };
    }
    
    const newUser = {
        id: Date.now().toString(),
        name: userData.name,
        email: userData.email,
        phone: userData.phone,
        password: userData.password,
        type: userData.userType || 'individual',
        role: userData.userType === 'company' ? 'company' : 'customer',
        companyName: userData.companyName || '',
        governorate: userData.governorate || '',
        address: userData.address || '',
        createdAt: new Date().toISOString()
    };
    
    users.push(newUser);
    localStorage.setItem('users', JSON.stringify(users));
    
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('userData', JSON.stringify({
        id: newUser.id,
        name: newUser.name,
        email: newUser.email,
        phone: newUser.phone,
        type: newUser.type,
        role: newUser.role
    }));
    
    return { 
        success: true, 
        message: 'تم إنشاء الحساب بنجاح',
        user: newUser
    };
}

function forgotPassword(emailOrPhone) {
    if (!emailOrPhone) {
        return { success: false, message: 'يرجى إدخال البريد الإلكتروني أو رقم الهاتف' };
    }
    
    const user = users.find(u => u.email === emailOrPhone || u.phone === emailOrPhone);
    
    if (user) {
        return { 
            success: true, 
            message: 'تم إرسال رابط استعادة كلمة المرور إلى بريدك الإلكتروني' 
        };
    } else {
        return { 
            success: false, 
            message: 'لم يتم العثور على حساب مرتبط بهذا البريد الإلكتروني أو رقم الهاتف' 
        };
    }
}

function resetPassword(token, newPassword, confirmPassword) {
    if (!newPassword || !confirmPassword) {
        return { success: false, message: 'يرجى ملء جميع الحقول' };
    }
    
    if (newPassword !== confirmPassword) {
        return { success: false, message: 'كلمتا المرور غير متطابقتين' };
    }
    
    if (users.length > 0) {
        users[0].password = newPassword;
        localStorage.setItem('users', JSON.stringify(users));
        
        return { 
            success: true, 
            message: 'تم تحديث كلمة المرور بنجاح' 
        };
    }
    
    return { 
        success: false, 
        message: 'حدث خطأ أثناء تحديث كلمة المرور' 
    };
}

function updateProfile(userId, updatedData) {
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex !== -1) {
        users[userIndex] = { ...users[userIndex], ...updatedData };
        localStorage.setItem('users', JSON.stringify(users));
        
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        localStorage.setItem('userData', JSON.stringify({
            ...userData,
            ...updatedData
        }));
        
        return { 
            success: true, 
            message: 'تم تحديث البيانات بنجاح',
            user: users[userIndex]
        };
    }
    
    return { 
        success: false, 
        message: 'لم يتم العثور على المستخدم' 
    };
}

function getUserData(userId) {
    return users.find(u => u.id === userId) || null;
}

function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userData');
    
    return { success: true, message: 'تم تسجيل الخروج بنجاح' };
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        login,
        register,
        forgotPassword,
        resetPassword,
        updateProfile,
        getUserData,
        logout
    };
}