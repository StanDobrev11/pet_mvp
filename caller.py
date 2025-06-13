import os
from datetime import datetime, timedelta

import django
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.timezone import make_aware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_mvp.settings')
django.setup()

from pet_mvp.records.models import VaccinationRecord, MedicationRecord, MedicalExaminationRecord
from pet_mvp.drugs.models import Vaccine, Drug, BloodTest, UrineTest, FecalTest
from pet_mvp.pets.models import Pet, Transponder, Tattoo

from django.utils.dateparse import parse_datetime
from pet_mvp.accounts.models import AppUser, Groomer

UserModel = get_user_model()


def create_pet_markings():
    dog_pet = Pet.objects.get(name_en='Test Dog')
    cat_pet = Pet.objects.get(name_en='Test Cat')

    # Create a transponder for Test Dog
    try:
        Transponder.objects.create(
            code='123456789012345',
            pet=dog_pet,
            date_of_application='2020-01-15',
            date_of_reading='2020-01-15',
            location='Left side of the neck',
            location_en='Left side of the neck',
            location_bg='Лява страна на врата',
        )
        print(f"Transponder created for {dog_pet.name}")
    except Exception:
        print(f"Transponder already exists for {dog_pet.name}")

    # Create a tattoo for Test Cat
    try:
        Tattoo.objects.create(
            code='ABC123',
            pet=cat_pet,
            date_of_application='2021-04-01',
            date_of_reading='2021-04-01',
            location='Inside of right ear',
            location_en='Inside of right ear',
            location_bg='Вътрешна страна на дясното ухо',
        )
        print(f"Tattoo created for {cat_pet.name}")
    except Exception:
        print(f"Transponder already exists for {cat_pet.name}")


def create_complete_examination_record_for_test_dog():
    dog_pet = Pet.objects.get(name_en='Test Dog')
    clinic = UserModel.objects.get(email='dianavet@pet-mvp.com')
    try:
        blood_test = BloodTest.objects.create(
            result="WBC and RBC levels normal, low platelets detected",
            white_blood_cells=10.2,
            red_blood_cells=4.8,
            hemoglobin=12.5,
            platelets=150.0
        )
        urine_test = UrineTest.objects.create(
            result="Clear urine, neutral pH",
            color="Yellow",
            clarity="Clear",
            ph=7.0,
            specific_gravity=1.015
        )
        fecal_test = FecalTest.objects.create(
            result="Parasites detected, blood in sample found",
            consistency="Watery",
            parasites_detected=True,
            parasite_type="Roundworms",
            blood_presence=True
        )
    except IntegrityError:
        blood_test = BloodTest.objects.get(
            result="WBC and RBC levels normal, low platelets detected")
        urine_test = UrineTest.objects.get(result="Clear urine, neutral pH")
        fecal_test = FecalTest.objects.get(
            result="Parasites detected, blood in sample found")

    medication_record = MedicationRecord.objects.filter(pet=dog_pet).first()
    vaccination_record = VaccinationRecord.objects.filter(pet=dog_pet).first()

    medical_record = MedicalExaminationRecord.objects.get_or_create(
        date_of_entry=make_aware(datetime.strptime('15.03.2025', '%d.%m.%Y')),
        doctor="Dr.John Doe",
        pet=dog_pet,
        clinic=clinic,
        reason_for_visit="Routine checkup and swelling on left leg",
        general_health="Good overall health",
        body_condition_score=5,
        temperature=38.5,
        heart_rate=80,
        respiratory_rate=18,
        mucous_membrane_color="Pink",
        hydration_status="Well hydrated",
        skin_and_coat_condition="Shiny and smooth",
        teeth_and_gums="Clean with no signs of tartar",
        eyes_ears_nose="Clear and healthy",
        blood_test=blood_test,
        urine_test=urine_test,
        fecal_test=fecal_test,
        treatment_performed="Applied anti-inflammatory ointment",
        diagnosis="Mild swelling due to recent injury",
        follow_up=True,
        notes="Owner advised to return in 2 weeks for follow-up."
    )
    medical_record[0].vaccinations.add(vaccination_record)
    medical_record[0].medications.add(medication_record)

    print(f"Medical Examination Record created for {dog_pet.name}.")


def create_user(email, password):
    try:
        UserModel.objects.create_owner(
            email=email,
            password=password,
        )
        print('User created')
    except IntegrityError:
        print('User already exists')

    print(f'email: {email}\npassword: {"*" * len(password)}')


def create_pets():
    try:
        dog_pet = Pet.objects.create(
            name_en='Test Dog',
            name_bg='Тест Куче',
            species='dog',
            breed='German Shepherd',
            color='Black and Tan',
            color_en='Black and Tan',
            color_bg='Черно и кафяво',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number='BG01VP111111',
            features='Friendly, energetic, loyal',
            features_en='Friendly, energetic, loyal',
            features_bg='Приятелски настроен, енергичен, лоялен',
        )
        cat_pet = Pet.objects.create(
            name_en='Test Cat',
            name_bg='Тест Коте',
            species='cat',
            breed='Persian',
            color='White',
            color_en='White',
            color_bg='Бяла',
            date_of_birth='2021-03-15',
            sex='female',
            current_weight='3.5',
            passport_number='BG01VP222222',
            features='Long hair, calm, independent',
            features_en='Long hair, calm, independent',
            features_bg='Дълга козина, спокойна, независима',
        )

        pets = [dog_pet, cat_pet]

        owner = UserModel.objects.get(email__icontains='admin')

        for pet in pets:
            pet.owners.add(owner)
        print('Pets created')
    except IntegrityError:
        print('Pets already exist')


def populate_medication_records():
    pet = Pet.objects.get(name_en='Test Dog')
    medication_data = [
        # Medication already given
        dict(
            pet=pet,
            medication=Drug.objects.get(name='Drontal Puppy'),
            date=make_aware(datetime.strptime('15.03.2025', '%d.%m.%Y')),
            time='08:00',
            dosage='1 tablet',
            valid_until=make_aware(
                datetime.strptime('14.04.2025', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            medication=Drug.objects.get(name='NexGard'),
            date=make_aware(datetime.strptime('01.03.2025', '%d.%m.%Y')),
            time='09:30',
            dosage='1 chewable',
            valid_until=make_aware(datetime.strptime('01.04.2025', '%d.%m.%Y'))
        ),
        # Medication to be given
        dict(
            pet=pet,
            medication=Drug.objects.get(name='Interceptor Plus'),
            date=make_aware(datetime.strptime('01.04.2025', '%d.%m.%Y')),
            time='10:00',
            dosage='1 tablet',
            valid_until=make_aware(
                datetime.strptime('12.04.2025', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            medication=Drug.objects.get(name='Apoquel'),
            date=make_aware(datetime.strptime('20.03.2025', '%d.%m.%Y')),
            time='07:30',
            dosage='1 tablet (16 mg)',
            valid_until=make_aware(
                datetime.strptime('27.03.2025', '%d.%m.%Y')),
        )
    ]

    for data in medication_data:
        # Ensure unique records using get_or_create
        MedicationRecord.objects.get_or_create(**data)

    print('Medication records for Test Dog populated')


def populate_vaccination_records():
    pet = Pet.objects.get(name_en='Test Dog')
    vaccines_data = [
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Canine Distemper'),
            batch_number='A130D01',
            manufacturer='Nobivac',
            manufacture_date=make_aware(
                datetime.strptime('18.05.2024', '%d.%m.%Y')),
            date_of_vaccination=make_aware(
                datetime.strptime('22.03.2025', '%d.%m.%Y')),
            valid_until=make_aware(
                datetime.strptime('22.03.2026', '%d.%m.%Y')),
        ),
        # Rabies
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Rabies'),
            batch_number='R222B12',
            manufacturer='Pfizer',
            manufacture_date=make_aware(
                datetime.strptime('01.04.2024', '%d.%m.%Y')),
            date_of_vaccination=make_aware(
                datetime.strptime('15.03.2025', '%d.%m.%Y')),
            valid_from=make_aware(datetime.strptime(
                '15.03.2025', '%d.%m.%Y') + timedelta(days=7)),
            # 7 days after vaccination
            valid_until=make_aware(
                datetime.strptime('15.03.2026', '%d.%m.%Y')),
        ),
        # Parvoviridae
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Parvoviridae'),
            batch_number='P874C09',
            manufacturer='Zoetis',
            manufacture_date=make_aware(
                datetime.strptime('10.06.2023', '%d.%m.%Y')),
            date_of_vaccination=make_aware(
                datetime.strptime('20.01.2025', '%d.%m.%Y')),
            valid_until=make_aware(
                datetime.strptime('20.01.2026', '%d.%m.%Y')),
        ),
        # Leptospirosis
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Leptospirosis'),
            batch_number='L390D08',
            manufacturer='Merial',
            manufacture_date=make_aware(
                datetime.strptime('12.05.2023', '%d.%m.%Y')),
            date_of_vaccination=make_aware(
                datetime.strptime('25.08.2025', '%d.%m.%Y')),
            valid_until=make_aware(
                datetime.strptime('25.08.2026', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Canine Distemper'),
            batch_number='D123P01',
            manufacturer='Zoetis',
            manufacture_date=make_aware(
                datetime.strptime('01.12.2019', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime(
                '01.02.2020', '%d.%m.%Y')),  # 6 weeks old
            valid_until=make_aware(
                datetime.strptime('01.02.2021', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Parvoviridae'),
            batch_number='P456B01',
            manufacturer='Merial',
            manufacture_date=make_aware(
                datetime.strptime('15.12.2019', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime(
                '01.03.2020', '%d.%m.%Y')),  # 8 weeks old
            valid_until=make_aware(
                datetime.strptime('01.03.2021', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Leptospirosis'),
            batch_number='L789C02',
            manufacturer='Nobivac',
            manufacture_date=make_aware(
                datetime.strptime('20.12.2019', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime(
                '01.05.2020', '%d.%m.%Y')),  # 16 weeks old
            valid_until=make_aware(
                datetime.strptime('01.05.2021', '%d.%m.%Y')),
        ),
        # Rabies Vaccine (required yearly in many regions)
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Rabies'),
            batch_number='R222B01',
            manufacturer='Pfizer',
            manufacture_date=make_aware(
                datetime.strptime('01.01.2020', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime(
                '01.06.2020', '%d.%m.%Y')),  # First rabies shot
            valid_from=make_aware(datetime.strptime(
                '01.06.2020', '%d.%m.%Y') + timedelta(days=7)),  # After 7 days
            valid_until=make_aware(
                datetime.strptime('01.06.2021', '%d.%m.%Y')),
        ),
        # Adult Booster Shots (Subsequent Years)
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Canine Distemper'),
            batch_number='D123B02',
            manufacturer='Zoetis',
            manufacture_date=make_aware(
                datetime.strptime('10.12.2020', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime(
                '01.06.2021', '%d.%m.%Y')),  # Booster shot
            valid_until=make_aware(
                datetime.strptime('01.06.2022', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Rabies'),
            batch_number='R456B02',
            manufacturer='Pfizer',
            manufacture_date=make_aware(
                datetime.strptime('15.03.2021', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime(
                '01.06.2021', '%d.%m.%Y')),  # Yearly Rabies booster
            valid_from=make_aware(datetime.strptime(
                '01.06.2021', '%d.%m.%Y') + timedelta(days=7)),
            valid_until=make_aware(
                datetime.strptime('01.06.2022', '%d.%m.%Y')),
        ),

    ]

    for data in vaccines_data:
        # Use get_or_create with unpacked data to ensure no duplicates
        VaccinationRecord.objects.get_or_create(**data)

    print('Vaccination records for Test Dog populated')


def set_site_domain():
    from django.contrib.sites.models import Site

    DEBUG = os.getenv("DEBUG", "False") == "True"
    base_url = os.environ.get('BASE_URL', 'localhost')

    if DEBUG:
        domain = f'{base_url}:8000'
    else:
        domain = base_url

    Site.objects.update_or_create(id=1, defaults={
        'domain': domain,
        'name': 'PetMedical'
    })

    print('Site domain updated to {}'.format(domain))


def create_clinics():
    fixtures = [
        {
            "user": {
                "email": "zoovet@pet-mvp.com",
                "password": "pbkdf2_sha256$1000000$1F6RG951sX7uL9jjSs5lyO$L3oHgT+oj872IR9T791TdSKGVBjH3gDH296dkljoVlw=",
                "is_owner": False,
                "is_clinic": True,
                "is_active": True,
                "is_staff": False,
                "phone_number": "887877746",
                "city": "Варна",
                "country": "Българиа",
                "default_language": "bg",
                "date_joined": "2024-01-01T00:00:00Z",
            },
            "clinic": {
                "clinic_name": "Зоо-Вет",
                "clinic_address": "кв.Галата, ул.Панорамна 24",
                "is_approved": True,
                "additional_services": ["store"],
                "website": "https://www.facebook.com/p/%D0%92%D0%B5%D1%82%D0%B5%D1%80%D0%B8%D0%BD%D0%B0%D1%80%D0%BD%D0%B0-%D0%9A%D0%BB%D0%B8%D0%BD%D0%B8%D0%BA%D0%B0-%D0%97%D0%BE%D0%BE-%D0%92%D0%B5%D1%82-%D0%BA%D0%B2-%D0%93%D0%B0%D0%BB%D0%B0%D1%82%D0%B0-100063558821449/"
            },
        },
        {
            "user": {
                "email": "dianavet@pet-mvp.com",
                "password": "pbkdf2_sha256$1000000$h1g5uBeTnqCaqPxcJbN4Gc$pUrd9oM5X7uu8Y/Y59pl9wtfawVOQFZOR0EakBgtKrM=",
                "is_owner": False,
                "is_clinic": True,
                "is_active": False,
                "is_staff": False,
                "phone_number": "0884672308",
                "city": "Варна",
                "country": "Българиа",
                "default_language": "bg",
                "date_joined": "2024-01-01T00:00:00Z",
            },
            "clinic": {
                "clinic_name": "Дианавет",
                "clinic_address": "кв.Аспарухово, ул.Моряшка 19",
                "is_approved": True,
                "additional_services": ["store"],
                "website": "http://dianavet.com/"
            },
        },
        {
            "user": {
                "email": "ovk@pet-mvp.com",
                "password": "pbkdf2_sha256$1000000$aNfD4HIXOm0a68RIPlrDde$ixQwfRXLQBRBGY11UUzgBn+Duj1uVJyzkj/nSxDMsl4=",
                "is_owner": False,
                "is_clinic": True,
                "is_active": False,
                "is_staff": False,
                "phone_number": "",
                "city": "Варна",
                "country": "Българиа",
                "default_language": "bg",
                "date_joined": "2024-01-01T00:00:00Z",
            },
            "clinic": {
                "clinic_name": "Обединена Ветеринарна Клиника",
                "clinic_address": "ул. Царевец 34",
                "is_approved": True,
                "website": "https://ovk-varna.com/"
            },
        },
        {
            "user": {
                "email": "elpida@pet-mvp.com",
                "password": "pbkdf2_sha256$1000000$pwdAuZNc2NZjgxMet1VCbQ$4Ol3BaJMmgrana82lSIbb2nmJnzpuLLnTMTQS7VD1pE=",
                "is_owner": False,
                "is_clinic": True,
                "is_active": False,
                "is_staff": False,
                "phone_number": "0899694299",
                "city": "Варна",
                "country": "Българиа",
                "default_language": "bg",
                "date_joined": "2024-01-01T00:00:00Z",
            },
            "clinic": {
                "clinic_name": "Елпида",
                "clinic_address": "ул. Цанко Церковски 5",
                "is_approved": True,
                "additional_services": ["store"],
                "website": "https://elpida-varna.bg/"
            },
        },
    ]

    for entry in fixtures:
        user_data = entry["user"]
        clinic_data = entry["clinic"]

        email = user_data.pop("email")
        password = user_data.pop("password")
        city = user_data.pop("city")
        country = user_data.pop("country")
        phone_number = user_data.pop("phone_number")

        existing_user = UserModel.objects.filter(email=email).first()
        if existing_user:
            print(f"✅ Skipping: User '{email}' already exists.")
            continue

        user = UserModel.objects.create_clinic(
            email=email,
            password=password,
            phone_number=phone_number,
            country=country,
            city=city,
            name=clinic_data["clinic_name"],
            address=clinic_data["clinic_address"],
            is_approved=clinic_data.get("is_approved", False),
            **user_data
        )

        clinic = user.clinic
        clinic.additional_services = clinic_data.get("additional_services", [])
        clinic.save()

        print(f"🆕 Created clinic '{clinic.name}' for user '{user.email}'")



def create_groomers():
    fixtures = [
        {
            "user": {
                "email": "lapichka@pet-mvp.com",
                "password": "pbkdf2_sha256$1000000$6Fo177TLJ3M4XcmiBHuq22$R0uFk/tgUExLe7asVIFifEbuM949XicOkNZ1HkKoPRA=",
                "is_owner": False,
                "is_groomer": True,
                "is_active": True,
                "is_staff": False,
                "phone_number": "+359896857522",
                "city": "Варна",
                "country": "Българиа",
                "default_language": "bg",
                "date_joined": "2024-01-01T00:00:00Z",
            },
            "clinic": {
                "name": "Лапичка",
                "address": "ул. „Генерал Гурко“ 78",
                "is_approved": True,
                "website": "https://www.facebook.com/%D0%97%D0%BE%D0%BE%D1%86%D0%B5%D0%BD%D1%82%D1%8A%D1%80-%D0%9B%D0%B0%D0%BF%D0%B8%D1%87%D0%BA%D0%B0-Grooming-Studio-996140623737127/"
            },
        },
        {
            "user": {
                "email": "tedigroomer@pet-mvp.com",
                "password": "pbkdf2_sha256$1000000$whS5caq9BQLAnEb0JjNrMo$gU/7mViNenrdJHeNZJiP/f37OhLLjHLw4IhwNEsQkOA=",
                "is_owner": False,
                "is_groomer": True,
                "is_active": True,
                "is_staff": False,
                "phone_number": "+359889316673",
                "city": "Варна",
                "country": "Българиа",
                "default_language": "bg",
                "date_joined": "2024-01-01T00:00:00Z",
            },
            "clinic": {
                "name": "Зоо център 'Теди'",
                "address": "кв. Аспарухово, ул. „Свети Свети Кирил и Методий“ 39",
                "is_approved": True,
                "website": ""
            },
        },
    ]

    for entry in fixtures:
        user_data = entry["user"]
        groomer_data = entry["clinic"]

        email = user_data["email"]

        if AppUser.objects.filter(email=email).exists():
            print(f"⏭ User already exists: {email}")
            continue

        user = AppUser.objects.create(
            email=email,
            password=user_data["password"],  # Already hashed
            is_owner=user_data["is_owner"],
            is_groomer=user_data["is_groomer"],
            is_active=user_data["is_active"],
            is_staff=user_data["is_staff"],
            phone_number=user_data["phone_number"],
            city=user_data["city"],
            country=user_data["country"],
            default_language=user_data["default_language"],
            date_joined=parse_datetime(user_data["date_joined"])
        )

        groomer = Groomer.objects.create(
            user=user,
            name=groomer_data["name"],
            address=groomer_data["address"],
            website=groomer_data["website"],
            is_approved=groomer_data["is_approved"]
        )

        print(f"✅ Created groomer: {groomer.name} ({email})")


from django.utils.dateparse import parse_datetime
from pet_mvp.accounts.models import AppUser, Store  # assuming you have a Store model

def create_stores():
    fixtures = [
        {
            "user": {
                "email": "alfapet@pet-mvp.com",
                "password": "pbkdf2_sha256$1000000$pkOFe9pfSEIgqsvWzZeonF$kgAx4rzg+EpgTLn39WODEbdVVAy9ejEucLZJ/4s+558=",
                "is_owner": False,
                "is_store": True,
                "is_active": True,
                "is_staff": False,
                "phone_number": "+359879888375",
                "city": "Варна",
                "country": "Българиа",
                "default_language": "bg",
                "date_joined": "2024-01-01T00:00:00Z",
            },
            "clinic": {
                "name": "Алфа Пет",
                "address": "кв. Аспарухово, ул. „Моряшка“ 19",
                "is_approved": True,
                "website": ""
            },
        },
        {
            "user": {
                "email": "zooland@pet-mvp.com",
                "password": "pbkdf2_sha256$1000000$UOcEHzxPGsybUO9BHiWg7x$SI90UG5dEtAfdyWhxq1u2lK3UoX5gkYALcVMBg6jRuY=",
                "is_owner": False,
                "is_store": True,
                "is_active": True,
                "is_staff": False,
                "phone_number": "+359877965422",
                "city": "Варна",
                "country": "Българиа",
                "default_language": "bg",
                "date_joined": "2024-01-01T00:00:00Z",
            },
            "clinic": {
                "name": "Зооборса Зооланд",
                "address": "Централна Жп Гара Одесос, ул. „Девня“ 17",
                "is_approved": True,
                "website": ""
            },
        },
    ]

    for entry in fixtures:
        user_data = entry["user"]
        store_data = entry["clinic"]

        email = user_data["email"]

        if AppUser.objects.filter(email=email).exists():
            print(f"⏭ User already exists: {email}")
            continue

        user = AppUser.objects.create(
            email=email,
            password=user_data["password"],  # already hashed
            is_owner=user_data["is_owner"],
            is_store=user_data["is_store"],
            is_active=user_data["is_active"],
            is_staff=user_data["is_staff"],
            phone_number=user_data["phone_number"],
            city=user_data["city"],
            country=user_data["country"],
            default_language=user_data["default_language"],
            date_joined=parse_datetime(user_data["date_joined"])
        )

        store = Store.objects.create(
            user=user,
            name=store_data["name"],
            address=store_data["address"],
            website=store_data["website"],
            is_approved=store_data["is_approved"]
        )

        print(f"✅ Created store: {store.name} ({email})")


def set_coordinates():
    from pet_mvp.common.tasks import geocode_venues_coordinates_task

    try:
        result = geocode_venues_coordinates_task()
        print(f'Coordinates fetched {result}')
    except Exception as e:
        print(f'Run geocode fetch manually. {e}')


if __name__ == '__main__':
    set_site_domain()
    create_pets()
    create_pet_markings()
    create_clinics()
    create_groomers()
    create_stores()
    populate_vaccination_records()
    populate_medication_records()
    create_complete_examination_record_for_test_dog()
    set_coordinates()
