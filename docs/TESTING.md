# ShopSphere Test Suite & Quality Assurance Guide

This document describes the automated test suite and verification procedures for the **ShopSphere** E-commerce platform.

---

## 1. Automated Test Architecture

The test suite in [`store/tests.py`](../store/tests.py) covers critical e-commerce workflows:

1. **Model & Slugs Validation**
   - Automatic slug generation on category and product save.
   - Initial strikethrough original price calculation.
   - `in_stock` property checks.

2. **Session Cart Operations**
   - Adding items anonymously and checking session dictionary.
   - Dynamic quantity updates.
   - Product removal and session cleanup.
   - Stock limit capping.

3. **Atomic Checkout & Inventory Management**
   - Successful order placement using `select_for_update()` inside `transaction.atomic()`.
   - Inventory decrements correctly.
   - Historical snapshots preserved in `OrderItem`.
   - Rollback verification: orders with requested quantities exceeding stock fail safely with `ValidationError` and do not alter inventory.

4. **IDOR & Security Access Control**
   - Insecure Direct Object Reference (IDOR) tests: User B cannot view User A's orders by guessing order IDs or numbers (`404 Not Found` returned).
   - Checkout requires authentication.
   - CSRF protection enforced across all POST forms.

5. **Search & Catalog Filtering**
   - Case-insensitive search across title, description, and category.
   - Category slug routing and product count aggregation.
   - Sorting by price, newest, and popularity.

---

## 2. Running Automated Tests

Run the test suite using Python:

```bash
python manage.py test store
```

Expected output:
```text
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......
----------------------------------------------------------------------
Ran 7 tests in 0.420s

OK
Destroying test database for alias 'default'...
```

---

## 3. Manual Testing Walkthrough

1. **Run Database Migrations and Seed Data**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py seed_products
   ```

2. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/` in your browser.

3. **Demo Credentials**:
   - **Admin Superuser**: `admin` / `admin123` (Admin panel at `http://127.0.0.1:8000/admin/`)
   - **Customer User**: `shivang` / `customer123`

4. **Verify Cash on Delivery Flow**:
   - Browse catalog at `/products/`.
   - Add "Wireless Noise-Canceling Headphones" to cart.
   - Navigate to `/cart/`, review items, click "Proceed to Checkout".
   - Confirm pre-filled shipping address and "Cash on Delivery (COD)" payment method.
   - Click "Place Order (Cash on Delivery)".
   - Verify order confirmation screen and tracking status at `/orders/`.
