const products = [
{
id: 1,
name: "Testliner (ورق تست لاينر)",
description: "يستخدم في صناعة الكرتون المضلع كطبقة خارجية قوية ومتوسطة التحمل.",
price: 7.5,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.48 AM (1).jpeg",
category: "Liner Paper",
available: true,
minQuantity: 10,
company_id: 1,
company_name: "PaperTech Egypt",
features: [
"الوزن: 120 – 200 GSM",
"مقاومة الرطوبة: متوسطة",
"قوة الضغط: متوسطة",
"قابل للطباعة: نعم"
]
},

{
id: 2,
name: "Fluting Paper (ورق فلوتنج)",
description: "يستخدم كطبقة مموجة داخل الكرتون المضلع لتحسين قوة التحمل.",
price: 6.8,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.48 AM.jpeg",
category: "Fluting",
available: true,
minQuantity: 10,
company_id: 1,
company_name: "PaperTech Egypt",
features: [
"الوزن: 90 – 150 GSM",
"مرونة عالية",
"مقاومة ضغط جيدة",
"مقاومة رطوبة متوسطة"
]
},

{
id: 3,
name: "Recycled Kraft Paper (ورق كرافت معاد تدويره)",
description: "يستخدم في تصنيع أكياس التسوق والتغليف بقوة شد عالية.",
price: 8.2,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.50 AM (1).jpeg",
category: "Kraft Paper",
available: true,
minQuantity: 8,
company_id: 2,
company_name: "EcoPack",
features: [
"الوزن: 70 – 200 GSM",
"مقاومة تمزق عالية",
"قوة شد عالية",
"مقاومة رطوبة متوسطة"
]
},

{
id: 4,
name: "Corrugated Cardboard (كرتون مضلع)",
description: "يستخدم في صناديق الشحن والتخزين ويتميز بمقاومة صدمات عالية.",
price: 9.5,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM.jpeg",
category: "Corrugated",
available: true,
minQuantity: 15,
company_id: 2,
company_name: "EcoPack",
features: [
"سمك: 3 – 7 مم",
"قوة تحمل عالية",
"مقاومة صدمات عالية",
"مقاومة رطوبة متوسطة"
]
},

{
id: 5,
name: "Duplex Board – Brown Back (دوبلكس بورد)",
description: "يستخدم في تصنيع علب المنتجات بجودة طباعة ممتازة.",
price: 10.5,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (6).jpeg",
category: "Duplex Board",
available: true,
minQuantity: 12,
company_id: 3,
company_name: "Advanced Recycling Co",
features: [
"الوزن: 200 – 450 GSM",
"صلابة عالية",
"قابل للطباعة ممتاز",
"مقاومة انثناء جيدة"
]
},

{
id: 6,
name: "Chipboard / Grey Board (شيب بورد)",
description: "يستخدم في علب الأحذية والملفات بصلابة وكثافة عالية.",
price: 6.2,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (5).jpeg",
category: "Grey Board",
available: true,
minQuantity: 10,
company_id: 3,
company_name: "Advanced Recycling Co",
features: [
"سمك: 1 – 4 مم",
"كثافة عالية",
"مقاومة ضغط عالية",
"مناسب للعلب الصلبة"
]
},

{
id: 7,
name: "Linerboard (لاينربورد)",
description: "طبقة خارجية قوية لصناعة الكرتون والتغليف.",
price: 8.7,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (4).jpeg",
category: "Linerboard",
available: true,
minQuantity: 12,
company_id: 1,
company_name: "PaperTech Egypt",
features: [
"الوزن: 125 – 300 GSM",
"مقاومة تمزق عالية",
"مقاومة رطوبة متوسطة",
"قوة تحمل عالية"
]
},

{
id: 8,
name: "Brown Wrapping Paper (ورق تغليف بني)",
description: "يستخدم في تغليف المنتجات بتكلفة منخفضة ومرونة عالية.",
price: 5.8,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (3).jpeg",
category: "Wrapping Paper",
available: true,
minQuantity: 5,
company_id: 2,
company_name: "EcoPack",
features: [
"الوزن: 60 – 120 GSM",
"مرونة عالية",
"تكلفة منخفضة",
"مقاومة تمزق متوسطة"
]
},

{
id: 9,
name: "Paper Core Board (ورق بكر وأنابيب)",
description: "يستخدم في تصنيع بكر الورق والأنابيب الكرتونية بقوة ضغط عالية.",
price: 9.2,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (2).jpeg",
category: "Core Board",
available: true,
minQuantity: 15,
company_id: 3,
company_name: "Advanced Recycling Co",
features: [
"سماكة عالية",
"مقاومة ضغط عالية",
"عمر افتراضي طويل",
"مناسب للبكر الصناعية"
]
},

{
id: 10,
name: "Recycled Carton Board (كرتون معاد تدويره)",
description: "يستخدم في تصنيع علب التعبئة بجودة متوسطة وقابلية طباعة جيدة.",
price: 7.9,
unit: "كجم",
image: "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (1).jpeg",
category: "Carton Board",
available: true,
minQuantity: 10,
company_id: 2,
company_name: "EcoPack",
features: [
"الوزن: 180 – 350 GSM",
"صلابة متوسطة",
"قابل للطباعة",
"مقاومة انثناء جيدة"
]
}
];

function getAllProducts() {
    return products;
}

function getProductById(id) {
    return products.find(product => product.id === id);
}

function getProductsByCategory(category) {
    return products.filter(product => product.category === category);
}

function getProductsByCompany(companyId) {
    return products.filter(product => product.company_id === companyId);
}

function searchProducts(query) {
    const searchTerm = query.toLowerCase();
    return products.filter(product => 
        product.name.toLowerCase().includes(searchTerm) ||
        product.description.toLowerCase().includes(searchTerm) ||
        product.category.toLowerCase().includes(searchTerm)
    );
}

function createProduct(productData) {
    const newProduct = {
        id: products.length + 1,
        ...productData,
        created_at: new Date().toISOString()
    };
    
    products.push(newProduct);
    saveProductsToStorage();
    return newProduct;
}

function updateProduct(id, updatedData) {
    const index = products.findIndex(product => product.id === id);
    
    if (index !== -1) {
        products[index] = { ...products[index], ...updatedData };
        saveProductsToStorage();
        return products[index];
    }
    
    return null;
}

function deleteProduct(id) {
    const index = products.findIndex(product => product.id === id);
    
    if (index !== -1) {
        const deletedProduct = products.splice(index, 1);
        saveProductsToStorage();
        return deletedProduct[0];
    }
    
    return null;
}

function saveProductsToStorage() {
    localStorage.setItem('products', JSON.stringify(products));
}

function loadProductsFromStorage() {
    const storedProducts = JSON.parse(localStorage.getItem('products') || 'null');
    
    if (storedProducts) {
        products.length = 0;
        products.push(...storedProducts);
    }
}

// Load products from storage on initialization
loadProductsFromStorage();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getAllProducts,
        getProductById,
        getProductsByCategory,
        getProductsByCompany,
        searchProducts,
        createProduct,
        updateProduct,
        deleteProduct,
        products
    };
}