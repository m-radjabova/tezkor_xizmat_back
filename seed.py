import random
import uuid
from datetime import time

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.business import Business
from app.models.category import Category
from app.models.enums import UserRole
from app.models.review import Review
from app.models.user import User

ADMIN_EMAIL = "admin@tezkorxizmat.uz"
ADMIN_PASSWORD = "admin12345"
PROVIDER_EMAIL = "provider@tezkorxizmat.uz"
PROVIDER_PASSWORD = "provider12345"
CUSTOMER_EMAIL = "customer@tezkorxizmat.uz"
CUSTOMER_PASSWORD = "customer12345"


def clear_database(db):
    """Oldin qo'shilgan barcha ma'lumotlarni o'chirish"""
    db.execute(delete(Review))
    db.execute(delete(Business))
    db.execute(delete(User))
    db.execute(delete(Category))
    db.commit()


def seed_categories(db):
    items = [
        ("Dorixona", "pill"),
        ("Go'zallik", "sparkles"),
        ("Tibbiyot", "heart-pulse"),
        ("Ta'lim", "graduation-cap"),
        ("Do'kon", "store"),
        ("Usta xizmati", "wrench"),
        ("Restoran va Kafe", "utensils"),
        ("Avto servis", "car"),
        ("Mebellar", "couch"),
        ("Kiyim va Poyabzal", "shirt"),
        ("Kuryerlik va Logistika", "truck"),
        ("Sport va Fitnes", "dumbbell"),
        ("Mehmonxonalar", "hotel"),
        ("Qurilish va Ta'mirlash", "hammer"),
        ("IT va Dasturlash", "code"),
        ("Foto va Video", "camera"),
        ("Ximchistka va Kiyim yuvish", "washing-machine"),
        ("Moliya va Bank", "wallet"),
        ("Yuridik xizmatlar", "scale"),
        ("Bolalar markazi", "baby"),
        ("Tadbirlar va To'ylar", "party-popper"),
        ("Uy hayvonlari (Zoo)", "dog"),
        ("Konsultatsiya", "briefcase"),
        ("O'yin va Ko'ngilochar", "gamepad-2"),
        ("Turizm va Sayohat", "plane"),
    ]
    categories = []
    for name, icon in items:
        category = Category(id=uuid.uuid4(), name=name, icon=icon)
        db.add(category)
        categories.append(category)
    db.commit()
    for cat in categories:
        db.refresh(cat)
    return categories


def upsert_user(db, *, email, full_name, password, role, phone=None, **extra):
    user = User(
        id=uuid.uuid4(),
        email=email,
        full_name=full_name,
        phone=phone,
        hashed_password=hash_password(password),
        role=role,
    )
    for field, value in extra.items():
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_users(db, categories):
    admin = upsert_user(
        db,
        email=ADMIN_EMAIL,
        full_name="Tezkor Xizmat Admin",
        password=ADMIN_PASSWORD,
        role=UserRole.ADMIN,
        phone="+998901112233",
    )
    provider = upsert_user(
        db,
        email=PROVIDER_EMAIL,
        full_name="Ali Valiyev",
        password=PROVIDER_PASSWORD,
        role=UserRole.PROVIDER,
        phone="+998901234567",
        organization_name="Shifo Pharm",
        responsible_person="Ali Valiyev",
        provider_category_ids=[str(cat.id) for cat in categories[:3]],
    )
    customer = upsert_user(
        db,
        email=CUSTOMER_EMAIL,
        full_name="Demo Mijoz",
        password=CUSTOMER_PASSWORD,
        role=UserRole.CUSTOMER,
        phone="+998909998877",
    )
    
    extra_customers = []
    for i in range(1, 6):
        c = upsert_user(
            db,
            email=f"customer{i}@tezkorxizmat.uz",
            full_name=f"Mijoz {i}",
            password="password123",
            role=UserRole.CUSTOMER,
            phone=f"+99890100200{i}",
        )
        extra_customers.append(c)

    return admin, provider, [customer] + extra_customers


def seed_businesses_and_reviews(db, categories, provider, customers):
    # Har bir biznes uchun Buxoroga mos manzillar, geolokatsiyalar hamda real Unsplash rasmlari
    businesses_data = [
        (
            "Shifo Pharm", "Dorixona", "Buxoro sh., Naqshbandiy ko'chasi 18", 39.7747, 64.4286, "08:00", "22:00", 
            "Dori-darmonlar va tezkor maslahat.",
            "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?w=300",
            ["https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=900", "https://images.unsplash.com/photo-1576602976047-174e57a47881?w=900"]
        ),
        (
            "Grand Medical", "Tibbiyot", "Buxoro sh., M. Iqbol ko'chasi 45", 39.7681, 64.4320, "09:00", "18:00", 
            "Zamonaviy ko'p tarmoqli klinika va laboratoriya.",
            "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=300",
            ["https://images.unsplash.com/photo-1586773860418-d37222d8fce3?w=900", "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=900"]
        ),
        (
            "G'uncha Beauty", "Go'zallik", "Buxoro sh., B. Naqshbandiy ko'chasi 8", 39.7752, 64.4231, "10:00", "20:00", 
            "Soch, parvarish va makiyaj xizmatlari.",
            "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=300",
            ["https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=900", "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=900"]
        ),
        (
            "IT Park Bukhara Academy", "Ta'lim", "Buxoro sh., Piridastgir ko'chasi 13", 39.7621, 64.4412, "09:00", "21:00", 
            "Dasturlash va zamonaviy kasblar o'quv markazi.",
            "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=300",
            ["https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=900", "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=900"]
        ),
        (
            "Korzinka Supermarket", "Do'kon", "Buxoro sh., Navoiy shoh ko'chasi 10", 39.7695, 64.4210, "08:00", "23:00", 
            "Oziq-ovqat va maishiy mahsulotlar supermarketi.",
            "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=300",
            ["https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=900", "https://images.unsplash.com/photo-1542838132-92c53300491e?w=900"]
        ),
        (
            "Usta Alisher", "Usta xizmati", "Buxoro sh., Sharq mikrorayoni 5-uy", 39.7588, 64.4480, "08:00", "19:00", 
            "Santehnika, elektrik va maishiy texnika ta'mirlash.",
            "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=300",
            ["https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=900", "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=900"]
        ),
        (
            "Caravan Restoran", "Restoran va Kafe", "Buxoro sh., Hakikat ko'chasi 22 (Labi Hovuz yaqinida)", 39.7731, 64.4185, "11:00", "23:00", 
            "Milliy Buxoro palovi va Yevropa taomlari.",
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=300",
            ["https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=900", "https://images.unsplash.com/photo-1544025162-d76694265947?w=900"]
        ),
        (
            "AvtoTek Servis", "Avto servis", "Buxoro sh., Sanoatchilar ko'chasi 4", 39.7420, 64.4510, "09:00", "19:00", 
            "Moy almashtirish, diagnostika va dvigatel ta'miri.",
            "https://images.unsplash.com/photo-1486006920555-c77dce18193b?w=300",
            ["https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=900", "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=900"]
        ),
        (
            "Mebel House Bukhara", "Mebellar", "Buxoro sh., Gijduvon ko'chasi 15", 39.7810, 64.4150, "09:00", "19:00", 
            "Sifatli va qulay uy va ofis mebellari to'plami.",
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=300",
            ["https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=900", "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=900"]
        ),
        (
            "Trendy Style", "Kiyim va Poyabzal", "Buxoro sh., Buxoro Mall, 2-qavat", 39.7650, 64.4280, "10:00", "22:00", 
            "Zamonaviy erkaklar va ayollar kiyimlari.",
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300",
            ["https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?w=900", "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=900"]
        ),
        (
            "Express Courier Bukhara", "Kuryerlik va Logistika", "Buxoro sh., Ibn Sino ko'chasi 88", 39.7712, 64.4255, "08:00", "20:00", 
            "Buxoro shahrida tezkor va ishonchli yetkazib berish.",
            "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=300",
            ["https://images.unsplash.com/photo-1580674684081-7617fbf3d745?w=900", "https://images.unsplash.com/photo-1526367790999-0150786686a2?w=900"]
        ),
        (
            "FitLife Gym Bukhara", "Sport va Fitnes", "Buxoro sh., Alpomish ko'chasi 30", 39.7610, 64.4380, "07:00", "23:00", 
            "Zamonaviy trenajyor zali, krossfit va basseyn.",
            "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=300",
            ["https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=900", "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=900"]
        ),
        (
            "Bukhara Palace Hotel", "Mehmonxonalar", "Buxoro sh., Samarqand ko'chasi 2", 39.7725, 64.4290, "00:00", "23:59", 
            "Tarixiy markaz yaqinida joylashgan shinam mehmonxona.",
            "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=300",
            ["https://images.unsplash.com/photo-1582719508461-905c673771fd?w=900", "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=900"]
        ),
        (
            "Stroy Mir Bukhara", "Qurilish va Ta'mirlash", "Buxoro sh., Gazli shoh ko'chasi 4", 39.7890, 64.4010, "08:30", "18:30", 
            "Sifatli qurilish mollari va ta'mirlash brigadalari.",
            "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=300",
            ["https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=900", "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=900"]
        ),
        (
            "SoftDev Solutions", "IT va Dasturlash", "Buxoro sh., K. Murtazoyev ko'chasi 16", 39.7645, 64.4350, "09:00", "18:00", 
            "Veb-saytlar va mobil ilovalar ishlab chiqish.",
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=300",
            ["https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=900"]
        ),
        (
            "Studio Pro Photo Bukhara", "Foto va Video", "Buxoro sh., Mehtar Anbar ko'chasi 5", 39.7740, 64.4215, "09:00", "20:00", 
            "Professional fotosessiya va videotasvir xizmatlari.",
            "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=300",
            ["https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=900", "https://images.unsplash.com/photo-1520854221256-17451cc331bf?w=900"]
        ),
        (
            "CleanExpress Bukhara", "Ximchistka va Kiyim yuvish", "Buxoro sh., Mustaqillik ko'chasi 12", 39.7670, 64.4310, "08:00", "20:00", 
            "Kiyim va gilamlarni kimyoviy tozalash.",
            "https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?w=300",
            ["https://images.unsplash.com/photo-1545173168-9f1947eebb7f?w=900", "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?w=900"]
        ),
        (
            "Kapitalbank Buxoro Filiali", "Moliya va Bank", "Buxoro sh., M. Tarobiy ko'chasi 7", 39.7710, 64.4230, "09:00", "17:00", 
            "Valyuta ayriboshlash, kreditlar va bank xizmatlari.",
            "https://images.unsplash.com/photo-1501167786227-4cba60f6d58f?w=300",
            ["https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=900", "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=900"]
        ),
        (
            "Lex Consulting", "Yuridik xizmatlar", "Buxoro sh., Naqshbandiy ko'chasi 21", 39.7735, 64.4270, "09:00", "18:00", 
            "Huquqiy maslahat va shartnomalarni rasmiylashtirish.",
            "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=300",
            ["https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=900", "https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=900"]
        ),
        (
            "Kelajak Bolalar Bog'chasi", "Bolalar markazi", "Buxoro sh., Koshona ko'chasi 11", 39.7600, 64.4430, "08:00", "18:30", 
            "Rivojlantiruvchi o'yinlar va chet tili kurslari.",
            "https://images.unsplash.com/photo-1502086223501-7ea6ecd79368?w=300",
            ["https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=900", "https://images.unsplash.com/photo-1567057419565-4349c49d8a04?w=900"]
        ),
        (
            "Visol To'yxonasi", "Tadbirlar va To'ylar", "Buxoro sh., Sitorai Mokhi-Khosa yo'li 3", 39.8110, 64.4390, "10:00", "23:00", 
            "To'ylar va tantanali marosimlarni o'tkazish saroyi.",
            "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300",
            ["https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?w=900", "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=900"]
        ),
        (
            "VetCare Klinikasi", "Uy hayvonlari (Zoo)", "Buxoro sh., Hamza ko'chasi 40", 39.7660, 64.4370, "09:00", "20:00", 
            "Uy hayvonlarini davolash, vaksina va parvarishlash.",
            "https://images.unsplash.com/photo-1532712938310-34cb3982ef74?w=300",
            ["https://images.unsplash.com/photo-1628009368231-7bb7cfcb0def?w=900", "https://images.unsplash.com/photo-1576201836106-db1758fd1c97?w=900"]
        ),
        (
            "Business Growth Bukhara", "Konsultatsiya", "Buxoro sh., Ibn Sino shoh ko'chasi 12", 39.7715, 64.4265, "09:00", "18:00", 
            "Biznes strategiyasi va moliyaviy konsalting.",
            "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=300",
            ["https://images.unsplash.com/photo-1552664730-d307ca884978?w=900", "https://images.unsplash.com/photo-1531497865144-0464ef8fb9a9?w=900"]
        ),
        (
            "VR Zone Game Club", "O'yin va Ko'ngilochar", "Buxoro sh., Buxoro Arena yaqinida", 39.7630, 64.4390, "10:00", "23:00", 
            "Virtual reallik, PlayStation 5 va kompyuter o'yinlari.",
            "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=300",
            ["https://images.unsplash.com/photo-1511512578047-dfb367046420?w=900", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=900"]
        ),
        (
            "Silk Road Travel Bukhara", "Turizm va Sayohat", "Buxoro sh., Samonidlar parki yonida 10", 39.7760, 64.4120, "09:00", "19:00", 
            "Buxoro bo'ylab ekskursiyalar va aviachiptalar.",
            "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=300",
            ["https://images.unsplash.com/photo-1503220317375-aaad61436b1b?w=900", "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=900"]
        ),
        (
            "Shifo Pharm 24/7", "Dorixona", "Buxoro sh., Markaziy Bozor yaqinida 1", 39.7780, 64.4220, "00:00", "23:59", 
            "24/7 ishlaydigan markaziy dorixona.",
            "https://images.unsplash.com/photo-1576602976047-174e57a47881?w=300",
            ["https://images.unsplash.com/photo-1586015555751-63bb77f4322a?w=900", "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=900"]
        ),
        (
            "Eco Fit Center", "Sport va Fitnes", "Buxoro sh., Gazli shoh ko'chasi 9", 39.7820, 64.4110, "08:00", "22:00", 
            "Fitness, yoga, sauna va basseyn xizmatlari.",
            "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=300",
            ["https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=900", "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=900"]
        ),
        (
            "Master Burger Bukhara", "Restoran va Kafe", "Buxoro sh., B. Naqshbandiy ko'chasi 14", 39.7742, 64.4260, "10:00", "02:00", 
            "Mazali burgerlar, fri va salqin ichimliklar.",
            "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300",
            ["https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=900", "https://images.unsplash.com/photo-1550547660-d9450f859349?w=900"]
        ),
        (
            "Auto Wash Premium", "Avto servis", "Buxoro sh., Navoiy shoh ko'chasi 5", 39.7705, 64.4200, "08:00", "22:00", 
            "Avtomobillarni kontaktsiz yuvish va ximchistka.",
            "https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?w=300",
            ["https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=900", "https://images.unsplash.com/photo-1507136566006-cfc505b114fc?w=900"]
        ),
        (
            "Smart Kids Zone", "Bolalar markazi", "Buxoro sh., K. Murtazoyev ko'chasi 44", 39.7655, 64.4360, "09:00", "20:00", 
            "Bolalar uchun intellektual va ko'ngilochar o'yinlar.",
            "https://images.unsplash.com/photo-1566454825481-4e48f80aa4d7?w=300",
            ["https://images.unsplash.com/photo-1516627145497-ae6968895b74?w=900", "https://images.unsplash.com/photo-1596464716127-f2a82984de30?w=900"]
        ),
    ]

    cat_map = {cat.name: cat.id for cat in categories}
    created_businesses = []

    for name, cat_name, address, lat, lon, open_s, close_s, desc, logo, imgs in businesses_data:
        open_h, open_m = map(int, open_s.split(":"))
        close_h, close_m = map(int, close_s.split(":"))

        biz = Business(
            id=uuid.uuid4(),
            owner_id=provider.id,
            category_id=cat_map[cat_name],
            name=name,
            description=desc,
            phone="+998901234567",
            logo_url=logo,
            address=address,
            latitude=lat,
            longitude=lon,
            open_time=time(open_h, open_m),
            close_time=time(close_h, close_m),
            images=imgs,
            is_verified=True,
        )
        db.add(biz)
        created_businesses.append(biz)

    db.commit()
    for biz in created_businesses:
        db.refresh(biz)

    # 30 ta sharh (Review) generatsiya qilish
    comments = [
        "Juda yaxshi xizmat, tavsiya qilaman!",
        "Xodimlar xushmuomala, narxlar ham hamyonbop.",
        "Ajoyib joy, menga juda yoqdi.",
        "Xizmat ko'rsatish sifati a'lo darajada.",
        "Tez va sifatli, rahmat sizlarga!",
        "Kutganimdan ham yaxshiroq chiqdi.",
        "Hammasi joyida, yana kelaman.",
        "Unchalik yomon emas, lekin yaxshilasa bo'ladi.",
        "Juda qulay joylashuv va zo'r servis.",
        "A'lo sifat, hammaga maslahat beraman!",
    ]

    for i in range(30):
        target_business = created_businesses[i % len(created_businesses)]
        random_customer = random.choice(customers)
        rating = random.choice([4, 5, 5, 5, 3])

        review = Review(
            id=uuid.uuid4(),
            business_id=target_business.id,
            user_id=random_customer.id,
            rating=rating,
            comment=f"{random.choice(comments)} ({target_business.name} uchun)",
            is_approved=True,
        )
        db.add(review)

    db.commit()


def main():
    db = SessionLocal()
    try:
        print("Eski ma'lumotlar o'chirilmoqda...")
        clear_database(db)

        print("Yangi ma'lumotlar qo'shilmoqda...")
        categories = seed_categories(db)
        admin, provider, customers = seed_users(db, categories)
        seed_businesses_and_reviews(db, categories, provider, customers)

        print("\n--- MUVAFFAQIYATLI YARATILDI ---")
        print(f"Categories: {len(categories)} ta")
        print("Businesses: 30 ta (Buxoro manzillari bilan)")
        print("Reviews: 30 ta")
        print("-------------------------------")
        print(f"Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Provider: {PROVIDER_EMAIL} / {PROVIDER_PASSWORD}")
        print(f"Customer: {CUSTOMER_EMAIL} / {CUSTOMER_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()