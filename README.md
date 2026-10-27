# CodeAlpha_ShopSphere

## ShopSphere — Simple E-Commerce Store

A full-stack e-commerce web application developed as part of my Python Development Internship at CodeAlpha.

The project demonstrates product browsing, user authentication, shopping cart management, Cash on Delivery (COD) checkout, order processing, and inventory management.

### Internship Details
- **Organization:** CodeAlpha
- **Domain:** Python Development
- **Project:** Task 1 — Simple E-commerce Store
- **Backend:** Django (Python)
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript, Tailwind CSS

---

## Live Demo & Repository

- **Live Website:** [https://shopsphere-jwqn.onrender.com](https://shopsphere-jwqn.onrender.com)
- **GitHub Repository:** [https://github.com/shivangsaxena1011/ShopSphere](https://github.com/shivangsaxena1011/ShopSphere)

---

## Project Objective

The objective of this project is to apply full-stack development concepts by building a functional e-commerce application with database-backed product listings, secure user authentication, shopping cart functionality, and order processing.

This project is part of the practical assignments provided during my CodeAlpha internship.

---

## Features

### Customer Features
- **Product Discovery & Search:** Live keyword search across product titles and descriptions.
- **Category & Price Filtering:** Filter products across multi-tier categories (Electronics, Fashion, Home & Living, Books) and price brackets with custom sorting (Featured, Price: Low-to-High, High-to-Low, Newest).
- **Product Detail Pages:** High-resolution product images, technical specifications, stock counters, and customer ratings.
- **User Authentication & Profile:** Secure account registration, login (username or email), session persistence, and profile address management.
- **Shopping Cart Management:** Session-backed cart for both guest visitors and authenticated users with real-time quantity controls, stock limits, and coupon discount support (`SHOPSPHERE10`, `FIRSTBUY`).
- **Cash on Delivery (COD) Checkout:** Streamlined multi-step checkout flow with saved address pre-fill and doorstep verification policy.
- **Order History & Tracking:** Visual order timeline (Placed ➔ Processing ➔ Shipped ➔ Delivered), itemized line totals, print-ready receipts, and IDOR ownership access protection.

### Order and Inventory Management
- **Atomic Order Processing:** Concurrency-safe transactions utilizing Django's `transaction.atomic()` and `select_for_update()` to prevent race conditions during checkout.
- **Server-Side Validation:** Enforces strict server-side stock and price verification before order confirmation.
- **Price Snapshots:** Captures exact purchase price and product state at checkout time in `OrderItem` to maintain permanent billing audit accuracy.
- **Inventory Updates:** Automatic stock decrements upon successful order placement, with full transaction rollback if inventory is insufficient.

### Administrative Features
- **Product & Category Administration:** Create, edit, and deactivate catalog entries with auto-generated slugs.
- **Inventory Control:** Live stock monitoring and bulk inventory updates directly via Django Admin.
- **Order Fulfillment Workflow:** Manage order statuses (Placed, Processing, Shipped, Delivered, Cancelled) and track payment confirmation states.
- **Customer Oversight:** View registered user accounts and associated order records.

---

## Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript, Tailwind CSS (via CDN)
- **Backend:** Python 3.12, Django 5+
- **Database:** SQLite
- **WSGI Web Server:** Gunicorn
- **Static Assets:** WhiteNoise (compressed & cached)
- **Authentication:** Django Authentication Framework
- **ORM:** Django Object-Relational Mapping (ORM)
- **Deployment Platform:** Render
- **Version Control:** Git & GitHub

---

## System Architecture

```text
ShopSphere/
├── manage.py
├── requirements.txt
├── Procfile
├── build.sh
├── .env.example
├── .gitignore
├── README.md
├── docs/
│   └── TESTING.md
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── store/
│   ├── models.py              # UserProfile, Category, Product, Cart, CartItem, Order, OrderItem
│   ├── views.py               # Storefront, Catalog, Cart, Checkout, Profile, and Orders
│   ├── services.py            # Atomic transaction & order creation services
│   ├── cart.py                # Session & DB hybrid shopping cart manager
│   ├── forms.py               # Registration, Login, Checkout, and Profile forms
│   ├── admin.py               # Customized Django Admin configurations
│   ├── signals.py             # Automatic UserProfile creation on signup
│   ├── urls.py                # Store URL routing
│   ├── tests.py               # 13 automated unit tests
│   ├── migrations/            # Database schema and data migrations
│   └── templates/             # Semantic HTML templates
└── static/
    ├── css/style.css
    ├── js/main.js
    └── images/placeholder.svg
```

---

## Local Setup & Quickstart

### 1. Prerequisites
- Python 3.11 or 3.12 installed
- Git installed

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/shivangsaxena1011/ShopSphere.git
cd ShopSphere
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Seed Data
```bash
python manage.py migrate
```
*(Database migrations automatically seed the initial catalog and categories).*

### 5. Create an Administrator Account
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

Open your browser:
- **Storefront:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Panel:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Automated Testing

The project includes an automated test suite verifying model constraints, slug collision resolution, cart math, atomic checkout concurrency, IDOR protection, and promotional coupons:

```bash
python manage.py test store
```

**Test Suite Coverage:**
- 13 comprehensive unit tests
- 100% pass rate
- Tested against Django 5+ test runner

---

## Learning Outcomes

Through this project, I practiced:
- Building full-stack web applications with Django and Python
- Designing relational database schemas and managing migrations
- Implementing secure user authentication and profile workflows
- Developing session-based shopping cart operations for guest and authenticated sessions
- Enforcing concurrency safety and atomic stock management using `transaction.atomic()` and `select_for_update()`
- Writing automated unit tests to guarantee security and business logic integrity
- Configuring production WSGI servers (Gunicorn) and static file pipelines (WhiteNoise)
- Deploying a live web application to cloud hosting (Render)
- Utilizing Git and GitHub for version control and collaborative workflows

---

## Internship Acknowledgement

This project was developed as part of my internship at CodeAlpha to gain practical experience in Python development and full-stack web application development.

The assignment provided an opportunity to work with Django, database models, authentication, shopping cart workflows, order processing, and inventory management.

I am grateful to CodeAlpha for providing this learning opportunity.

---

## License

This project is open-source under the [MIT License](LICENSE).
