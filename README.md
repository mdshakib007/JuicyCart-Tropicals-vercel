# 🥭 JuicyCart-Tropicals - A Mango Marketplace  

🚀 **JuicyCart-Tropicals** is an API-based mango marketplace where sellers can list mangoes, manage orders, and customers can browse, filter, and track their purchases.  

📌 **It's Live Now!**: [JuicyCart-Tropicals (Live)](https://juicycart-tropicals.vercel.app/)  

---

## 🔥 Key Features  

### 🔐 Authentication & User Management  
- **Token-based authentication** for secure API access.  
- **Email verification required** to activate accounts.  

### 🛍️ Seller Features  
- **Dedicated Seller Dashboard** – Manage a single shop.  
- **Add, edit, and delete products**.  
- **Update order status & send email notifications**.  

### 📦 Order Management  
- Customers can **place orders** & **cancel pending orders**.  
- Sellers can **update order status**.  
- **Email notifications** for order updates.  

### 💳 Payment Integration  
- **SSLCommerz** is used for secure online purchases.  

### 🔎 Product Filtering & Search  
- Search by **name, category, and price range**.  

### 🔐 Security  
- Used **Token Authentication**, but still exploring better security practices.  

---

## 📜 API Documentation  

### 1️⃣ **User**  
- **User List**: [`/user/list/`](https://juicy-cart-tropicals-backend.vercel.app/user/list/)  
- **Seller List**: [`/user/seller/list/`](https://juicy-cart-tropicals-backend.vercel.app/user/seller/list/)  
- **Customer List**: [`/user/customer/list/`](https://juicy-cart-tropicals-backend.vercel.app/user/customer/list/)  
- **Filtering**:  
  - By User ID: [`/user/list/?user_id=2`](https://juicy-cart-tropicals-backend.vercel.app/user/list/?user_id=2)  
  - By Seller ID: [`/user/seller/list/?user_id=3`](https://juicy-cart-tropicals-backend.vercel.app/user/seller/list/?user_id=3)  
  - By Customer ID: [`/user/customer/list/?user_id=3`](https://juicy-cart-tropicals-backend.vercel.app/user/customer/list/?user_id=3)  

### 2️⃣ **Authentication**  
- **Seller Registration**: [`/user/register/seller/`](https://juicy-cart-tropicals-backend.vercel.app/user/register/seller/)  
  - **POST**: `username`, `first_name`, `last_name`, `email`, `mobile_no`, `full_address`, `password`  
- **Customer Registration**: [`/user/register/customer/`](https://juicy-cart-tropicals-backend.vercel.app/user/register/customer/)  
  - **POST**: `username`, `first_name`, `last_name`, `email`, `full_address`, `password`  
- **Login**: [`/user/login/`](https://juicy-cart-tropicals-backend.vercel.app/user/login/)  
  - **POST**: `username`, `password`  
- **Logout**: [`/user/logout/`](https://juicy-cart-tropicals-backend.vercel.app/user/logout/)  
  - **POST**: `token`, `user_id`  

### 3️⃣ **Shop**  
- **Shop List**: [`/shop/list/`](https://juicy-cart-tropicals-backend.vercel.app/shop/list/)  
- **Filtering**:  
  - By Shop ID: [`/shop/list/?shop_id=1`](https://juicy-cart-tropicals-backend.vercel.app/shop/list/?shop_id=1)  
  - By Owner ID: [`/shop/list/?user_id=4`](https://juicy-cart-tropicals-backend.vercel.app/shop/list/?user_id=4)  
- **Create Shop**: [`/shop/create/`](https://juicy-cart-tropicals-backend.vercel.app/shop/create/)  
  - **POST**: `owner`, `name`, `image`, `hotline`, `description`, `location`  

### 4️⃣ **Product Listing**  
- **Categories**: [`/listing/categories/`](https://juicy-cart-tropicals-backend.vercel.app/listing/categories/)  
- **Products**: [`/listing/products/`](https://juicy-cart-tropicals-backend.vercel.app/listing/products/)  
- **Filtering**:  
  - By Category ID: [`/listing/categories/?category_id=3`](https://juicy-cart-tropicals-backend.vercel.app/listing/categories/?category_id=3)  
  - By Shop ID: [`/listing/products/?shop_id=1`](https://juicy-cart-tropicals-backend.vercel.app/listing/products/?shop_id=1)  
  - By Product Name: [`/listing/products/?name=string`](https://juicy-cart-tropicals-backend.vercel.app/listing/products/?name=string)  
  - By Price Range:  
    - Min: [`/listing/products/?min_price=100`](https://juicy-cart-tropicals-backend.vercel.app/listing/products/?min_price=100)  
    - Max: [`/listing/products/?max_price=200`](https://juicy-cart-tropicals-backend.vercel.app/listing/products/?max_price=200)  
- **Add Product**: [`/listing/product/add/`](https://juicy-cart-tropicals-backend.vercel.app/listing/product/add/)  
  - **POST**: `name`, `price`, `image`, `category`, `available`, `about`  
- **Edit Product**: [`/listing/product/edit/`](https://juicy-cart-tropicals-backend.vercel.app/listing/product/edit/)  
  - **POST**:  
    - Required: `user_id`, `product_id`  
    - Optional: Other product data  
- **Delete Product**: [`/listing/product/delete/`](https://juicy-cart-tropicals-backend.vercel.app/listing/product/delete/)  
  - **POST**: `user_id`, `product_id`  

### 5️⃣ **Order Management**  
- **Order List**: [`/order/list/`](https://juicy-cart-tropicals-backend.vercel.app/order/list/)  
- **Filtering**:  
  - By Order ID: [`/order/list/?order_id=4`](https://juicy-cart-tropicals-backend.vercel.app/order/list/?order_id=4)  
  - By Customer ID: [`/order/list/?customer_id=2`](https://juicy-cart-tropicals-backend.vercel.app/order/list/?customer_id=2)  
  - By Shop ID: [`/order/list/?shop_id=2`](https://juicy-cart-tropicals-backend.vercel.app/order/list/?shop_id=2)  
- **Place Order**: [`/order/place/`](https://juicy-cart-tropicals-backend.vercel.app/order/place/)  
  - **POST**: `product_id`, `user_id`, `order_id`  
- **Cancel Order**: [`/order/cancel/`](https://juicy-cart-tropicals-backend.vercel.app/order/cancel/)  
  - **POST**: `user_id`, `order_id`  
- **Change Order Status**: [`/order/change/`](https://juicy-cart-tropicals-backend.vercel.app/order/change/)  
  - **POST**: `user_id`, `customer_id`, `order_id`, `order_status`  

---

## 💡 Future Enhancements  
✅ **React.js frontend** for a better user experience.  
✅ **Improve API security** with JWT & permissions.  
✅ **Advanced analytics for sellers**.  

---

## 🎯 Connect with Me  
📧 **Email**: shakibahmed.528874@gmail.com  
🔗 **LinkedIn**: [MD Shakib Ahmed](https://www.linkedin.com/in/mdshakib00777)  
📺 **YouTube**: [AlgoAspire](https://youtube.com/@algoaspire/)
