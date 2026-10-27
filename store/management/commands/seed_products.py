from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, UserProfile

class Command(BaseCommand):
    help = "Seed database with realistic initial categories, products, and admin user"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding ShopSphere database..."))

        # 1. Create or get admin superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@shopsphere.local',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'ShopSphere',
                'last_name': 'Admin',
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123"))

        # 2. Create demo customer user
        demo_user, created = User.objects.get_or_create(
            username='shivang',
            defaults={
                'email': 'shivang@shopsphere.local',
                'first_name': 'Shivang',
                'last_name': 'Saxena',
            }
        )
        if created:
            demo_user.set_password('customer123')
            demo_user.save()
            profile, _ = UserProfile.objects.get_or_create(user=demo_user)
            profile.phone = '+91 9876543210'
            profile.address = '123, ABC Colony, Arera Hills'
            profile.city = 'Bhopal'
            profile.state = 'Madhya Pradesh'
            profile.postal_code = '462001'
            profile.save()
            self.stdout.write(self.style.SUCCESS("Created customer user: shivang / customer123"))

        # 3. Create Categories
        categories_data = [
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'icon_name': 'headphones',
                'description': 'Smart gadgets, computers, audio equipment, and wireless devices with manufacturer warranty.'
            },
            {
                'name': 'Fashion',
                'slug': 'fashion',
                'icon_name': 'checkroom',
                'description': 'Contemporary apparel, footwear, and accessories tailored for daily comfort and executive presence.'
            },
            {
                'name': 'Home & Living',
                'slug': 'home-and-living',
                'icon_name': 'chair',
                'description': 'Ergonomic furnishings, atmospheric lighting, and ambient essentials for modern spaces.'
            },
            {
                'name': 'Books',
                'slug': 'books',
                'icon_name': 'menu_book',
                'description': 'Bestsellers, technical architecture references, productivity guides, and timeless literature.'
            },
        ]

        category_objs = {}
        for cat_info in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=cat_info['slug'],
                defaults=cat_info
            )
            category_objs[cat.slug] = cat
            self.stdout.write(f"Category ready: {cat.name}")

        # 4. Products Data
        products_data = [
            {
                'category': category_objs['electronics'],
                'name': 'Wireless Noise-Canceling Headphones',
                'slug': 'wireless-noise-canceling-headphones',
                'description': 'Studio-grade over-ear wireless headphones with active hybrid noise cancellation, 40mm titanium drivers, and 30-hour battery life on a single charge.',
                'price': Decimal('2999.00'),
                'original_price': Decimal('4999.00'),
                'stock': 45,
                'is_featured': True,
                'rating': Decimal('4.5'),
                'reviews_count': 120,
                'image_url': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCHEfqpWusBPWAr__qrc_ZIUEN37ec0el8nkbaqIiy7lNslpw3lUUvswkYfjJRZgPUgKjLwa6xwxvSBJCUrv-m8HPbLcmNrcVR-ChfCf4w6_IE3p5aZ_4_ndEB6-49lxZBbRdwKe0GVMmxXe9YGSzDKbwmmojWKT2nz4hN7En33FQqvPOvsaOK-Zz0h929QIr1dDimiijdysaQ9bcCAqLfHGFbQlsPS0tVvTui4o_LUSCGje-r4yp7c',
                'specifications': "Hybrid Active Noise Cancellation (ANC)\nBluetooth 5.3 Low Latency\n30 Hours Ultra-long Battery Life\n1 Year Replacement Guarantee\nType-C Fast Charging (10m charge = 3hr playback)"
            },
            {
                'category': category_objs['electronics'],
                'name': 'Smart Fitness Watch Ultra',
                'slug': 'smart-fitness-watch-ultra',
                'description': 'Next-generation smartwatch featuring AMOLED 1.96-inch high-definition curved display, continuous SpO2 and heart-rate telemetry, and 5ATM water resistance.',
                'price': Decimal('4999.00'),
                'original_price': Decimal('7999.00'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'reviews_count': 215,
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80',
                'specifications': "1.96-inch Always-on AMOLED Display\nBuilt-in Precision Dual-band GPS\nContinuous Heart Rate & SpO2 Tracking\n12 Days Typical Battery Life\n5ATM Water Resistance rating"
            },
            {
                'category': category_objs['electronics'],
                'name': 'Pro Ultrabook 14-inch Laptop',
                'slug': 'pro-ultrabook-14-inch-laptop',
                'description': 'Lightweight feather-thin aluminum chassis equipped with high-speed 16GB LPDDR5 RAM, 1TB NVMe PCIe 4.0 SSD, and 2.8K 120Hz OLED edge-to-edge display.',
                'price': Decimal('64999.00'),
                'original_price': Decimal('79999.00'),
                'stock': 15,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'reviews_count': 88,
                'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=80',
                'specifications': "14.0-inch 2.8K 120Hz OLED Display\n16GB LPDDR5X Dual-channel RAM\n1TB Ultra-fast NVMe PCIe 4.0 SSD\nBacklit Ergonomic Keyboard\nFingerprint biometric scanner"
            },
            {
                'category': category_objs['electronics'],
                'name': 'True Wireless Studio Earbuds',
                'slug': 'true-wireless-studio-earbuds',
                'description': 'Ultra-compact IPX5 water-resistant in-ear headphones with quad ENC microphones for crystal-clear calls and deep bass sound profile.',
                'price': Decimal('1999.00'),
                'original_price': Decimal('2999.00'),
                'stock': 60,
                'is_featured': False,
                'rating': Decimal('4.6'),
                'reviews_count': 142,
                'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80',
                'specifications': "Quad Environmental Noise Cancelling Mics\nIPX5 Splash & Sweat Resistance\n36 Hours Playtime with Case\nInstant Auto-Pairing Bluetooth 5.3"
            },
            {
                'category': category_objs['electronics'],
                'name': 'Portable 360 Bluetooth Speaker',
                'slug': 'portable-360-bluetooth-speaker',
                'description': 'Rich 360-degree acoustic dispersion with dual passive radiators, robust silicone shock protection, and 18-hour continuous battery playback.',
                'price': Decimal('2499.00'),
                'original_price': Decimal('3499.00'),
                'stock': 25,
                'is_featured': False,
                'rating': Decimal('4.4'),
                'reviews_count': 96,
                'image_url': 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop&q=80',
                'specifications': "20W RMS Dynamic 360 Degree Sound\nIP67 Waterproof & Dustproof\n18 Hours Continuous Battery Life\nTWS Wireless Dual-speaker Pairing"
            },
            {
                'category': category_objs['fashion'],
                'name': 'Classic Oxford Cotton Shirt',
                'slug': 'classic-oxford-cotton-shirt',
                'description': '100% breathable organic combed long-staple cotton shirt tailored with button-down collar, mother-of-pearl buttons, and refined single chest pocket.',
                'price': Decimal('1499.00'),
                'original_price': Decimal('2499.00'),
                'stock': 50,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'reviews_count': 110,
                'image_url': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&auto=format&fit=crop&q=80',
                'specifications': "100% Organic Combed Long-Staple Cotton\nTailored Modern Slim Fit\nReinforced Seams & Button-down Collar\nWrinkle-resistant easy care weave"
            },
            {
                'category': category_objs['fashion'],
                'name': 'Tailored Slim Fit Denim Jeans',
                'slug': 'tailored-slim-fit-denim-jeans',
                'description': 'Premium 12.5oz ring-spun denim with 2% elastane flex stretch. Pre-washed for a vintage indigo patina and all-day movement comfort.',
                'price': Decimal('1999.00'),
                'original_price': Decimal('2999.00'),
                'stock': 40,
                'is_featured': False,
                'rating': Decimal('4.5'),
                'reviews_count': 75,
                'image_url': 'https://images.unsplash.com/photo-1542272604-780c96856592?w=800&auto=format&fit=crop&q=80',
                'specifications': "12.5oz Japanese Ring-spun Cotton Denim\n2% Elastane Flexible Active Stretch\nClassic 5-Pocket Construction\nHeavy-duty YKK Brass Zipper"
            },
            {
                'category': category_objs['fashion'],
                'name': 'Premium Urban Minimalist Sneakers',
                'slug': 'premium-urban-minimalist-sneakers',
                'description': 'Handcrafted genuine top-grain leather sneakers with vulcanized rubber sole and memory foam cushioned antibacterial footbed.',
                'price': Decimal('3499.00'),
                'original_price': Decimal('5499.00'),
                'stock': 20,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'reviews_count': 130,
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80',
                'specifications': "Top-Grain Supple White Nappa Leather\nVulcanized Non-Slip Gum Rubber Sole\nOrtholite Shock-Absorbing Memory Insole\nWaxed Cotton Flat Athletic Laces"
            },
            {
                'category': category_objs['home-and-living'],
                'name': 'Ergonomic Mesh Office Chair',
                'slug': 'ergonomic-mesh-office-chair',
                'description': 'Engineered lumbar contour support, multi-angle synchro-tilt mechanism, 3D adjustable armrests, and high-tensile breathable Korean mesh.',
                'price': Decimal('8999.00'),
                'original_price': Decimal('12999.00'),
                'stock': 12,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'reviews_count': 64,
                'image_url': 'https://images.unsplash.com/photo-1580481077195-c3a821a501e2?w=800&auto=format&fit=crop&q=80',
                'specifications': "Class 4 Heavy-duty BIFMA Gas Lift\n3D Multi-directional Armrest Adjustment\nDynamic Lumbar Contour Cushioning\nHigh-Tensile Breathable Korean Mesh"
            },
            {
                'category': category_objs['home-and-living'],
                'name': 'Aroma Ceramic Ultrasonic Diffuser',
                'slug': 'aroma-ceramic-ultrasonic-diffuser',
                'description': 'Matte porcelain stone ceramic diffuser with whisper-quiet ultrasonic atomization and soft ambient warm LED ring for relaxing home atmospheres.',
                'price': Decimal('1299.00'),
                'original_price': Decimal('1999.00'),
                'stock': 35,
                'is_featured': False,
                'rating': Decimal('4.3'),
                'reviews_count': 58,
                'image_url': 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=800&auto=format&fit=crop&q=80',
                'specifications': "Handmade Matte Ceramic Cladding\n2.4MHz High-Frequency Ultrasonic Vibration\n300ml Water Capacity (8-10h run)\nAuto Safety Shutoff When Empty"
            },
            {
                'category': category_objs['books'],
                'name': 'Designing Data-Intensive Applications',
                'slug': 'designing-data-intensive-applications',
                'description': 'The definitive industry guide to the principles and practicalities of distributed systems, databases, storage engines, and stream processing.',
                'price': Decimal('899.00'),
                'original_price': Decimal('1299.00'),
                'stock': 80,
                'is_featured': True,
                'rating': Decimal('5.0'),
                'reviews_count': 320,
                'image_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop&q=80',
                'specifications': "Author: Martin Kleppmann\nFormat: Paperback, 616 pages\nPublisher: O'Reilly Media\nSubject: Distributed Architecture & DBs"
            },
            {
                'category': category_objs['books'],
                'name': 'Atomic Habits: Proven Framework',
                'slug': 'atomic-habits-proven-framework',
                'description': 'The landmark million-copy international bestseller on how tiny daily behavioral adjustments generate monumental, life-changing compound results.',
                'price': Decimal('499.00'),
                'original_price': Decimal('799.00'),
                'stock': 100,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'reviews_count': 540,
                'image_url': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800&auto=format&fit=crop&q=80',
                'specifications': "Author: James Clear\nFormat: Paperback, 320 pages\nPublisher: Penguin Random House\nSubject: Psychology & Habit Formation"
            },
        ]

        for p_info in products_data:
            Product.objects.update_or_create(
                slug=p_info['slug'],
                defaults=p_info
            )
            self.stdout.write(f"Product ready: {p_info['name']}")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
