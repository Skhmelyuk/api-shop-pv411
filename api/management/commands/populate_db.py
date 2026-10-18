from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import User, Category, Product, ProductSpecification, Order, OrderItem


# (назва, slug, [(назва підкатегорії, slug), ...])
CATEGORY_TREE = [
    ("Велика побутова техніка", "major-appliances", [
        ("Варочні панелі", "hobs"),
        ("Витяжки", "cooker-hoods"),
        ("Посудомийні машини", "dishwashers"),
        ("Духовки", "ovens"),
        ("Морозильні скрині", "chest-freezers"),
        ("Холодильники", "refrigerators"),
        ("Пральні машини", "washing-machines"),
        ("Мікрохвильові печі", "microwaves"),
        ("Пральні машини (напівавтомат)", "semi-automatic-washing-machines"),
        ("Духовки електричні", "electric-ovens"),
        ("Морозильні камери", "upright-freezers"),
        ("Пилососи", "vacuum-cleaners"),
        ("Плити", "cookers"),
    ]),
    ("Дрібна побутова техніка", "small-appliances", [
        ("Сушка для фруктів", "food-dehydrators"),
        ("Кухонні комбайни", "food-processors"),
        ("Блендери", "blenders"),
        ("М'ясорубки", "meat-grinders"),
        ("Мультипечі", "air-fryers"),
        ("Мультиварки", "multicookers"),
        ("Чайники", "kettles"),
        ("Соковитискачі", "juicers"),
    ]),
    ("Електроскутери", "electric-scooters", []),
    ("Телевізори", "tvs", []),
]

COMMON_SPECS = [
    ("Бренд", "Liberty"),
    ("Країна реєстрації бренду", "Україна"),
    ("Країна виробник", "Китай"),
    ("Гарантія", "12 місяців"),
]

PRODUCTS_DATA = [
    {
        "category": "electric-scooters",
        "name": "Електроскутер Liberty Moto Brisk",
        "description": (
            "Електроскутер Liberty Moto Brisk — двомісна модель для щоденних міських поїздок і пересування "
            "на середні дистанції. Безщітковий двигун потужністю 2000 Вт дозволяє розвивати швидкість до 43 км/год, "
            "а акумулятор 72 В / 20 А·год забезпечує запас ходу до 80 км на одному заряді залежно від навантаження, "
            "рельєфу та стилю їзди.\n\n"
            "Модель має 3 швидкісні режими та задню передачу, що робить керування зручнішим у місті та під час "
            "паркування. Передні гідравлічні дискові й задні дискові гальма забезпечують ефективне гальмування, "
            "а передній і задній амортизатори допомагають комфортніше долати нерівності дороги. 12-дюймові колеса "
            "додають стійкості та впевненості під час руху.\n\n"
            "Для щоденного використання Liberty Moto Brisk оснащений LED-освітленням, багажником, дзеркалами заднього "
            "виду, паркувальною ніжкою та USB-роз'ємом для заряджання телефона. Максимальне навантаження становить "
            "120 кг, а повна зарядка акумулятора займає близько 8 годин."
        ),
        "price": Decimal("52999.00"),
        "stock": 5,
        "is_new": True,
        "specs": [
            ("Тип транспорту", "Електроскутер"),
            ("Кількість місць", "2"),
            ("Максимальна швидкість", "43 км/год"),
            ("Задня передача", "Так"),
            ("Дальність ходу на одному заряді", "до 80 км"),
            ("Кількість швидкостей", "3"),
            ("Тип двигуна", "Безщітковий"),
            ("Потужність двигуна", "2000 W"),
            ("Ємність акумулятора", "20 А/год"),
            ("Напруга акумулятора", "72 В"),
            ("Час зарядки акумулятора", "8 год"),
            ("Максимальне навантаження", "120 кг"),
            ("Світлове обладнання", "Передня LED фара / Задня LED фара"),
            ("Передні гальма", "Дискові (гідравлічні)"),
            ("Задні гальма", "Дискові"),
            ("Діаметр коліс", "12”"),
            ("Додаткові функції", "Багажник / Задній амортизатор / Дзеркало заднього виду / Ніжка для парковки / "
                                  "Передній амортизатор / USB зарядка для телефона"),
            ("Комплектація", "Електроскутер / Зарядний пристрій / Документація / Гарантійний талон"),
            ("Примітка", "Не потребує реєстрації та наявності посвідчення водія"),
            ("Колір", "Синій"),
            ("Габарити (ДхШхВ)", "187 × 50 × 116 см"),
            ("Габарити упаковки (ДхШхВ)", "188 × 57 × 83 см"),
        ],
    },
    {
        "category": "refrigerators",
        "name": "Холодильник Liberty DRF-310 NX",
        "description": "Двокамерний холодильник з нижньою морозильною камерою та системою No Frost.",
        "price": Decimal("18999.00"),
        "stock": 7,
        "specs": [("Тип", "Двокамерний"), ("Система розморожування", "No Frost"), ("Колір", "Нержавіюча сталь")],
    },
    {
        "category": "washing-machines",
        "name": "Пральна машина Liberty WM-8014",
        "description": "Пральна машина з фронтальним завантаженням на 8 кг та інверторним двигуном.",
        "price": Decimal("14499.00"),
        "stock": 4,
        "specs": [("Максимальне завантаження", "8 кг"), ("Швидкість віджиму", "1400 об/хв"), ("Колір", "Білий")],
    },
    {
        "category": "kettles",
        "name": "Електрочайник Liberty KE-1720",
        "description": "Пластиковий електрочайник об'ємом 1,7 л з прихованим нагрівальним елементом.",
        "price": Decimal("899.00"),
        "stock": 30,
        "specs": [("Об'єм", "1,7 л"), ("Потужність", "2200 W"), ("Колір", "Білий")],
    },
    {
        "category": "air-fryers",
        "name": "Мультипіч Liberty AF-5500",
        "description": "Мультипіч (аерофритюрниця) об'ємом 5,5 л для приготування з мінімумом олії.",
        "price": Decimal("2799.00"),
        "stock": 12,
        "is_new": True,
        "specs": [("Об'єм", "5,5 л"), ("Потужність", "1700 W"), ("Колір", "Чорний")],
    },
    {
        "category": "tvs",
        "name": "Телевізор Liberty LD-4359",
        "description": "43-дюймовий Smart TV з роздільною здатністю 4K UHD.",
        "price": Decimal("11999.00"),
        "stock": 0,
        "specs": [("Діагональ", "43\""), ("Роздільна здатність", "3840 × 2160 (4K UHD)"), ("Smart TV", "Так")],
    },
]


class Command(BaseCommand):
    help = "Заповнює базу даних тестовими даними"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Тестовий користувач
        user, _ = User.objects.get_or_create(username="skhmelyuk", email="skhmelyuk@example.com")
        user.set_password("qwerty_1985")
        user.save()

        # Дерево категорій
        categories = {}
        for group_order, (group_name, group_slug, children) in enumerate(CATEGORY_TREE):
            group = Category.objects.create(name=group_name, slug=group_slug, order=group_order)
            categories[group_slug] = group
            for child_order, (child_name, child_slug) in enumerate(children):
                categories[child_slug] = Category.objects.create(
                    name=child_name, slug=child_slug, parent=group, order=child_order
                )

        # Товари з характеристиками
        products = []
        for item in PRODUCTS_DATA:
            item = dict(item)
            specs = item.pop("specs") + COMMON_SPECS
            category = categories[item.pop("category")]
            product = Product.objects.create(category=category, brand="Liberty", **item)
            ProductSpecification.objects.bulk_create(
                ProductSpecification(product=product, name=name, value=value, order=index)
                for index, (name, value) in enumerate(specs)
            )
            products.append(product)

        # Замовлення 1 (Підтверджено)
        order1 = Order.objects.create(user=user, status=Order.StatusChoices.CONFIRMED)
        OrderItem.objects.create(order=order1, product=products[0], quantity=1)
        OrderItem.objects.create(order=order1, product=products[3], quantity=2)

        # Замовлення 2 (Очікує обробки)
        order2 = Order.objects.create(user=user, status=Order.StatusChoices.PENDING)
        OrderItem.objects.create(order=order2, product=products[1], quantity=1)
        OrderItem.objects.create(order=order2, product=products[4], quantity=1)

        # Замовлення 3 (Скасовано)
        order3 = Order.objects.create(user=user, status=Order.StatusChoices.CANCELLED)
        OrderItem.objects.create(order=order3, product=products[2], quantity=1)
        OrderItem.objects.create(order=order3, product=products[5], quantity=1)

        self.stdout.write(self.style.SUCCESS(
            f"✅ БД заповнено: {Category.objects.count()} категорій, {Product.objects.count()} продуктів, "
            f"{Order.objects.count()} замовлень, {OrderItem.objects.count()} позицій."
        ))
