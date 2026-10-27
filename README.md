# ShopSphere - Modern E-Commerce Platform

A production-ready, full-stack e-commerce web application built with **Python 3.11+**, **Django 5+**, **SQLite**, **Tailwind CSS**, and **Cash on Delivery (COD)** checkout flow.

---

## 🌟 Key Features

- **Storefront & Product Discovery**:
  - Hero banner with promotional spotlights and doorstep payment assurance.
  - Multi-department browsing (Electronics, Fashion, Home & Living, Books).
  - Search across names, descriptions, and categories with live keyword matching.
  - Filtering by price ranges (min/max) and sorting (Featured, Price: Low-to-High, High-to-Low, Newest).
  - Detailed product pages with photo galleries, ratings, stock indicators, and specifications tables.

- **Shopping Cart & Inventory Protection**:
  - Session-based shopping cart accessible for both anonymous guests and logged-in customers.
  - Real-time stock availability verification and quantity adjustments.
  - Automatic cart migration from guest session to authenticated account upon login.
  - Coupon discount application.

- **Cash on Delivery (COD) Checkout Flow**:
  - Multi-step visual progress stepper (Cart Review ➔ Delivery & COD ➔ Order Confirmation).
  - Pre-filled shipping address from profile for registered users.
  - Zero prepay requirement with physical doorstep verification policy.
  - **Atomic Transaction Service (`transaction.atomic()` + `select_for_update()`)**: guarantees concurrency safety, accurate stock decrements, and snapshot preservation.

- **Order Management & Tracking**:
  - Order fulfillment logs with filter tabs: All Orders, Pending/Placed, Processing, Shipped, Delivered, Cancelled.
  - Financial metric bento highlights (Active COD amount, Delivered parcels).
  - Interactive status milestone tracking (Placed ➔ Processing ➔ Shipped ➔ Delivered).
  - Comprehensive order detail page with print-ready receipts and **IDOR security protection**.

- **Authentication & User Profiles**:
  - Secure registration, login (email or username), remember-me cookies, and logout.
  - UserProfile management with phone, street address, and postal code.

- **Customized Django Admin Panel**:
  - Pre-populated slugs, stock inline management, colored status badges, and batch actions (Mark as Processing, Shipped, Delivered, Cancelled).

---

## 🏗️ System Architecture & Database Schema

```text
ShopSphere/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── docs/
│   └── TESTING.md
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── cart.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── models.py
│   ├── services.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_products.py
│   ├── migrations/
│   │   └── ...
│   └── templates/
│       ├── base.html
│       ├── store/
│       │   ├── home.html
│       │   ├── product_list.html
│       │   ├── product_detail.html
│       │   ├── cart.html
│       │   ├── checkout.html
│       │   ├── order_success.html
│       │   ├── order_history.html
│       │   ├── order_detail.html
│       │   └── profile.html
│       ├── registration/
│       │   ├── login.html
│       │   └── register.html
│       └── errors/
│           ├── 403.html
│           ├── 404.html
│           └── 500.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.11, 3.12, or higher
- Git

### 2. Installation

Clone and navigate into the repository:
```bash
git clone https://github.com/shivangsaxena1011/ShopSphere.git
cd ShopSphere
```

Install dependencies:
```bash
py -3.12 -m pip install -r requirements.txt
```

### 3. Initialize Database & Seed Sample Products

Run migrations to create the database schema:
```bash
py -3.12 manage.py makemigrations store
py -3.12 manage.py migrate
```

Seed initial catalog with authentic categories, products, and test accounts:
```bash
py -3.12 manage.py seed_products
```

### 4. Run the Development Server

```bash
py -3.12 manage.py runserver
```

Access the application in your browser:
- **Storefront**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🔑 Demo Credentials

| Role | Username / Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Store Admin** | `admin` | `admin123` | Django Admin (`/admin/`) & Storefront |
| **Customer User** | `shivang` | `customer123` | Customer Storefront, Cart, COD Checkout, Orders |

---

## 🧪 Running the Test Suite

Run all automated unit tests:
```bash
py -3.12 manage.py test store
```

See [`docs/TESTING.md`](docs/TESTING.md) for full quality assurance and security testing documentation.

---

## 📄 License
MIT License. Crafted for the ShopSphere E-Commerce Platform.
