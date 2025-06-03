import os
from datetime import datetime, timedelta

import django
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.timezone import make_aware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_mvp.settings')
django.setup()

from pet_mvp.accounts.models import Clinic
from pet_mvp.records.models import VaccinationRecord, MedicationRecord, MedicalExaminationRecord
from pet_mvp.drugs.models import Vaccine, Drug, BloodTest, UrineTest, FecalTest
from pet_mvp.pets.models import Pet, Transponder, Tattoo

UserModel = get_user_model()


def create_pet_markings():
    max_pet = Pet.objects.get(name_en='Max')
    luna_pet = Pet.objects.get(name_en='Luna')

    # Create a transponder for Max
    try:
        Transponder.objects.create(
            code='123456789012345',
            pet=max_pet,
            date_of_application='2020-01-15',
            date_of_reading='2020-01-15',
            location='Left side of the neck',
            location_en='Left side of the neck',
            location_bg='Лява страна на врата',
        )
        print(f"Transponder created for {max_pet.name}")
    except Exception:
        print(f"Transponder already exists for {max_pet.name}")

    # Create a tattoo for Luna
    try:
        Tattoo.objects.create(
            code='ABC123',
            pet=luna_pet,
            date_of_application='2021-04-01',
            date_of_reading='2021-04-01',
            location='Inside of right ear',
            location_en='Inside of right ear',
            location_bg='Вътрешна страна на дясното ухо',
        )
        print(f"Tattoo created for {luna_pet.name}")
    except Exception:
        print(f"Transponder already exists for {luna_pet.name}")


def create_complete_examination_record_for_max():
    max_pet = Pet.objects.get(name='Max')
    clinic = Clinic.objects.get(email='dianavet@pet-mvp.com')
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

    medication_record = MedicationRecord.objects.filter(pet=max_pet).first()
    vaccination_record = VaccinationRecord.objects.filter(pet=max_pet).first()

    medical_record = MedicalExaminationRecord.objects.get_or_create(
        date_of_entry=make_aware(datetime.strptime('15.03.2025', '%d.%m.%Y')),
        doctor="Dr. John Doe",
        pet=max_pet,
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

    print(f"Medical Examination Record created for {max_pet.name}.")


def create_user(email, password):
    try:
        UserModel.objects.create_owner(
            email=email,
            password=password,
        )
        print('User created')
    except IntegrityError:
        print('User already exists')

    print(f'email: {email}\npassword: {password}')


def create_pets():

    try:
        max_pet = Pet.objects.create(
            name_en='Max',
            name_bg='Макс',
            species='dog',
            breed='German Shepherd',
            color='Black and Tan',
            color_en='Black and Tan',
            color_bg='Черно и кафяво',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number='BG01VP123456',
            features='Friendly, energetic, loyal',
            features_en='Friendly, energetic, loyal',
            features_bg='Приятелски настроен, енергичен, лоялен',
        )
        luna_pet = Pet.objects.create(
            name_en='Luna',
            name_bg='Луна',
            species='cat',
            breed='Persian',
            color='White',
            color_en='White',
            color_bg='Бяла',
            date_of_birth='2021-03-15',
            sex='female',
            current_weight='3.5',
            passport_number='BG01ST765214',
            features='Long hair, calm, independent',
            features_en='Long hair, calm, independent',
            features_bg='Дълга козина, спокойна, независима',
        )

        pets = [max_pet, luna_pet]

        owner = UserModel.objects.get(email__icontains='admin')

        for pet in pets:
            pet.owners.add(owner)
        print('Pets created')
    except IntegrityError:
        print('Pets already exist')


def populate_medication_records():
    pet = Pet.objects.get(name='Max')
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

    print('Medication records for Max populated')


def populate_vaccination_records():
    pet = Pet.objects.get(name='Max')
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

    print('Vaccination records for Max populated')


if __name__ == '__main__':
    create_pets()
    create_pet_markings()
    populate_vaccination_records()
    populate_medication_records()
    create_complete_examination_record_for_max()
