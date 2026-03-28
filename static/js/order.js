let orders = JSON.parse(localStorage.getItem('userOrders') || '[]');

async function createOrder(orderData) {
    try {
        console.log('Creating order with data:', orderData);
        
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        console.log('Create order response:', result);
        
        if (result.success) {
            // إضافة الطلب إلى localStorage للتوافق
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            const newOrder = {
                id: result.order_number,
                orderId: result.order_id,
                userId: userData.id,
                customerName: userData.name,
                customerPhone: userData.phone,
                customerEmail: userData.email,
                customerType: userData.type || 'individual',
                products: orderData.products || [],
                quantity: orderData.quantity || 0,
                subtotal: orderData.subtotal || 0,
                deliveryFee: orderData.delivery_fee || 0,
                total: orderData.total || 0,
                paymentMethod: orderData.payment_method || 'cash_on_delivery',
                status: 'قيد المراجعة',
                deliveryDate: orderData.delivery_date,
                deliveryTime: orderData.delivery_time,
                notes: orderData.notes || '',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            
            orders.unshift(newOrder);
            saveOrdersToStorage();
            
            return newOrder;
        } else {
            console.error('Error creating order:', result.message);
            return null;
        }
    } catch (error) {
        console.error('Error creating order:', error);
        return null;
    }
}

async function getUserOrders(userId) {
    try {
        // جلب الطلبات من API
        const response = await fetch('/api/orders');
        const result = await response.json();
        
        if (result.success && result.orders) {
            if (userId) {
                return result.orders.filter(order => order.user_id == userId);
            }
            return result.orders;
        }
        return [];
    } catch (error) {
        console.error('Error fetching orders:', error);
        // Fallback to localStorage
        if (userId) {
            return orders.filter(order => order.userId === userId);
        }
        return orders;
    }
}

async function getOrderById(orderId) {
    try {
        // محاولة جلب الطلب من API
        const response = await fetch('/api/orders');
        const result = await response.json();
        
        if (result.success && result.orders) {
            const order = result.orders.find(o => o.order_number === orderId || o.id == orderId);
            if (order) return order;
        }
        
        // Fallback to localStorage
        return orders.find(order => order.id === orderId);
    } catch (error) {
        console.error('Error fetching order:', error);
        return orders.find(order => order.id === orderId);
    }
}

async function updateOrderStatus(orderId, newStatus) {
    try {
        const response = await fetch(`/admin/order/${orderId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // تحديث في localStorage للتوافق
            const order = orders.find(o => o.id === orderId);
            if (order) {
                order.status = newStatus;
                order.updatedAt = new Date().toISOString();
                saveOrdersToStorage();
            }
            return order;
        }
        return null;
    } catch (error) {
        console.error('Error updating order status:', error);
        // Fallback to localStorage
        const order = orders.find(o => o.id === orderId);
        if (order) {
            order.status = newStatus;
            order.updatedAt = new Date().toISOString();
            saveOrdersToStorage();
            return order;
        }
        return null;
    }
}

function deleteOrder(orderId) {
    const index = orders.findIndex(order => order.id === orderId);
    
    if (index !== -1) {
        const deletedOrder = orders.splice(index, 1);
        saveOrdersToStorage();
        return deletedOrder[0];
    }
    
    return null;
}

function saveOrdersToStorage() {
    localStorage.setItem('userOrders', JSON.stringify(orders));
}

function calculateOrderTotal(products, deliveryFee = 0) {
    const subtotal = products.reduce((total, item) => {
        return total + (item.price * item.quantity);
    }, 0);
    
    const total = subtotal + deliveryFee;
    
    return { subtotal, total };
}

function generateInvoice(order) {
    const invoice = {
        invoiceNumber: 'INV' + (order.id || order.order_number || '').slice(-6),
        orderId: order.order_number || order.id,
        customerName: order.customer_name || order.customerName,
        customerPhone: order.customer_phone || order.customerPhone,
        customerEmail: order.customer_email || order.customerEmail,
        date: order.created_at || order.createdAt,
        items: order.products,
        subtotal: order.subtotal,
        deliveryFee: order.delivery_fee || order.deliveryFee,
        total: order.total,
        paymentMethod: order.payment_method === 'cash_on_delivery' ? 'الدفع عند الاستلام' : 'الدفع الإلكتروني',
        status: order.status
    };
    
    return invoice;
}

function getOrderStep(status) {
    switch(status) {
        case 'قيد المراجعة': return 1;
        case 'في الطريق': return 2;
        case 'تم الاستلام': return 3;
        case 'مكتمل': return 4;
        default: return 1;
    }
}

// تصدير الدوال للاستخدام
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createOrder,
        getUserOrders,
        getOrderById,
        updateOrderStatus,
        deleteOrder,
        calculateOrderTotal,
        generateInvoice,
        getOrderStep,
        orders
    };
}