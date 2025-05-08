import os
from datetime import datetime, timedelta

import django
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.timezone import make_aware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_mvp.settings')
django.setup()

from pet_mvp.pets.models import Pet
from pet_mvp.drugs.models import Vaccine, Drug, BloodTest, UrineTest, FecalTest
from pet_mvp.records.models import VaccinationRecord, MedicationRecord, MedicalExaminationRecord

UserModel = get_user_model()


def create_complete_examination_record_for_max():
    max_pet = Pet.objects.get(name='Max')

    blood_test = BloodTest.objects.get_or_create(
        name="Complete Blood Count",
        result="WBC and RBC levels normal, low platelets detected",
        white_blood_cells=10.2,
        red_blood_cells=4.8,
        hemoglobin=12.5,
        platelets=150.0
    )
    urine_test = UrineTest.objects.get_or_create(
        name="Routine Urinalysis",
        result="Clear urine, neutral pH",
        color="Yellow",
        clarity="Clear",
        ph=7.0,
        specific_gravity=1.015
    )
    fecal_test = FecalTest.objects.get_or_create(
        name="Parasite Check",
        result="Parasites detected, blood in sample found",
        consistency="Watery",
        parasites_detected=True,
        parasite_type="Roundworms",
        blood_presence=True
    )

    medication_record = MedicationRecord.objects.filter(pet=max_pet).first()
    vaccination_record = VaccinationRecord.objects.filter(pet=max_pet).first()

    medical_record = MedicalExaminationRecord.objects.get_or_create(
        date_of_entry=make_aware(datetime.strptime('15.03.2025', '%d.%m.%Y')),
        doctor="Dr. John Doe",
        pet=max_pet,
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
        blood_test=blood_test[0],
        urine_test=urine_test[0],
        fecal_test=fecal_test[0],
        treatment_performed="Applied anti-inflammatory ointment",
        diagnosis="Mild swelling due to recent injury",
        follow_up=True,
        notes="Owner advised to return in 2 weeks for follow-up."
    )
    medical_record[0].vaccinations.add(vaccination_record)
    medical_record[0].medications.add(medication_record)
    print(f"Medical Examination Record created for {max_pet.name}.")


def create_superuser(email='admin@pet-mvp.com', password='1234'):
    try:
        UserModel.objects.create_superuser(
            email=email,
            password=password,
            first_name='Admin',
            last_name='Superuser',
            city='Varna',
            country='Bulgaria',
            phone_number='0887888888',
        )
        print('Superuser created')
    except IntegrityError:
        print('Superuser already exists')
    except ValidationError:
        print('Superuser already exists')

    print(f'email: {email}\npassword: {password}')


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
            name='Max',
            species='Dog',
            breed='German Shepherd',
            color='Black and Tan',
            date_of_birth='2020-01-01',
            sex='male',
            current_weight='28',
            passport_number='BG01VP123456',
        )
        luna_pet = Pet.objects.create(
            name='Luna',
            species='Cat',
            breed='Persian',
            color='White',
            date_of_birth='2021-03-15',
            sex='female',
            current_weight='3.5',
            passport_number='BG01ST765214',
        )
        pets = [max_pet, luna_pet]

        owner = UserModel.objects.first()

        for pet in pets:
            pet.owners.add(owner)
        print('Pets created')
    except IntegrityError:
        print('Pets already exist')


def populate_drugs():
    treatment_data = [
        # Internal Parasites
        dict(
            name='Drontal Puppy',
            notes='Targets roundworms, hookworms, and whipworms. Keeps puppy and family safe from internal parasites.',
        ),
        dict(
            name='Panacur',
            notes='Effective against roundworms, hookworms, tapeworms, and whipworms in dogs and puppies.',
        ),
        dict(
            name='Interceptor Plus',
            notes='Protects against heartworms, tapeworms, hookworms, and roundworms. A monthly chewable tablet for dogs.',
        ),
        # External Parasites
        dict(
            name='Frontline Plus',
            notes='Topical treatment protecting dogs from fleas, ticks, and lice. Apply monthly for prevention.',
        ),
        dict(
            name='Advantix',
            notes='Protects against fleas, ticks, mosquitoes, and biting flies. External spot-on treatment for dogs.',
        ),
        dict(
            name='NexGard',
            notes='Chewable tablet for dogs that kills fleas and ticks. Monthly dosage recommended.',
        ),
        # Regular Medication
        dict(
            name='Thyro-Tabs',
            notes='Used for treating hypothyroidism in dogs. Provides levothyroxine replacement therapy.',
        ),
        dict(
            name='Vetoryl',
            notes='Used for treating hyperadrenocorticism (Cushing’s disease) in dogs.',
        ),
        dict(
            name='Carprofen (Rimadyl)',
            notes='Commonly used as an anti-inflammatory and pain-relief medication for dogs with arthritis or after surgery.',
        ),
        dict(
            name='Apoquel',
            notes='Provides relief for dogs from itching and inflammation associated with allergies.',
        ),
    ]

    for data in treatment_data:
        # Use get_or_create by specifying explicit fields for safety
        Drug.objects.get_or_create(**data)

    print('Drugs populated')


def populate_vaccines():
    vaccines = [
        # Core Vaccines
        dict(
            name='Canine Distemper',
            core=True,
            notes='This core vaccine protects against the highly contagious and potentially deadly distemper virus.',
        ),
        dict(
            name='Rabies',
            core=True,
            notes='Rabies is a fatal, viral disease that attacks the central nervous system and usually is transmitted through the bite of an infected animal.',
        ),
        dict(
            name='Parvoviridae',
            core=True,
            notes='The vaccine guards against the highly contagious parvovirus, which causes life-threatening gastrointestinal illness.',
        ),
        dict(
            name='Leptospirosis',
            core=True,
            notes='The vaccine protects against leptospirosis, a bacterial infection that can cause kidney and liver failures, bleeding disorders, etc.',
        ),
        dict(
            name='Adenovirus (Infectious Hepatitis)',
            core=True,
            notes='Protects against canine adenovirus type 1, causing infectious hepatitis, and type 2, a respiratory illness.',
        ),
        dict(
            name='Parainfluenza',
            core=True,
            notes='Parainfluenza is part of the core combination vaccine and protects against a virus causing upper respiratory illness.',
        ),
        # Non-Core Vaccines
        dict(
            name='Bordetella (Kennel Cough)',
            core=False,
            notes='This non-core vaccine protects against Bordetella bronchiseptica, a leading cause of kennel cough in dogs.',
        ),
        dict(
            name='Lyme Disease (Borrelia Burgdorferi)',
            core=False,
            notes='This non-core vaccine is recommended for dogs at risk of exposure to ticks that carry Lyme disease.',
        ),
        dict(
            name='Canine Influenza',
            core=False,
            notes='Canine influenza vaccine helps protect dogs against highly contagious respiratory viruses (H3N8 and H3N2).',
        ),
        dict(
            name='Corona Virus (Canine)',
            core=False,
            notes='The canine coronavirus vaccine protects against intestinal upset caused by this specific type of virus. It is non-core and rarely recommended.',
        ),
        dict(
            name='Rattlesnake Vaccine',
            core=False,
            notes='An optional vaccine that may help dogs in high-risk areas produce antibodies against rattlesnake venom.',
        )
    ]

    for data in vaccines:
        Vaccine.objects.get_or_create(**data)

    print('Vaccines populated')


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
            valid_until=make_aware(datetime.strptime('14.04.2025', '%d.%m.%Y')),
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
            valid_until=make_aware(datetime.strptime('12.04.2025', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            medication=Drug.objects.get(name='Apoquel'),
            date=make_aware(datetime.strptime('20.03.2025', '%d.%m.%Y')),
            time='07:30',
            dosage='1 tablet (16 mg)',
            valid_until=make_aware(datetime.strptime('27.03.2025', '%d.%m.%Y')),
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
            manufacture_date=make_aware(datetime.strptime('18.05.2024', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('22.03.2025', '%d.%m.%Y')),
            valid_until=make_aware(datetime.strptime('22.03.2026', '%d.%m.%Y')),
        ),
        # Rabies
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Rabies'),
            batch_number='R222B12',
            manufacturer='Pfizer',
            manufacture_date=make_aware(datetime.strptime('01.04.2024', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('15.03.2025', '%d.%m.%Y')),
            valid_from=make_aware(datetime.strptime('15.03.2025', '%d.%m.%Y') + timedelta(days=7)),
            # 7 days after vaccination
            valid_until=make_aware(datetime.strptime('15.03.2026', '%d.%m.%Y')),
        ),
        # Parvoviridae
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Parvoviridae'),
            batch_number='P874C09',
            manufacturer='Zoetis',
            manufacture_date=make_aware(datetime.strptime('10.06.2023', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('20.01.2025', '%d.%m.%Y')),
            valid_until=make_aware(datetime.strptime('20.01.2026', '%d.%m.%Y')),
        ),
        # Leptospirosis
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Leptospirosis'),
            batch_number='L390D08',
            manufacturer='Merial',
            manufacture_date=make_aware(datetime.strptime('12.05.2023', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('25.08.2025', '%d.%m.%Y')),
            valid_until=make_aware(datetime.strptime('25.08.2026', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Canine Distemper'),
            batch_number='D123P01',
            manufacturer='Zoetis',
            manufacture_date=make_aware(datetime.strptime('01.12.2019', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('01.02.2020', '%d.%m.%Y')),  # 6 weeks old
            valid_until=make_aware(datetime.strptime('01.02.2021', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Parvoviridae'),
            batch_number='P456B01',
            manufacturer='Merial',
            manufacture_date=make_aware(datetime.strptime('15.12.2019', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('01.03.2020', '%d.%m.%Y')),  # 8 weeks old
            valid_until=make_aware(datetime.strptime('01.03.2021', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Leptospirosis'),
            batch_number='L789C02',
            manufacturer='Nobivac',
            manufacture_date=make_aware(datetime.strptime('20.12.2019', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('01.05.2020', '%d.%m.%Y')),  # 16 weeks old
            valid_until=make_aware(datetime.strptime('01.05.2021', '%d.%m.%Y')),
        ),
        # Rabies Vaccine (required yearly in many regions)
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Rabies'),
            batch_number='R222B01',
            manufacturer='Pfizer',
            manufacture_date=make_aware(datetime.strptime('01.01.2020', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('01.06.2020', '%d.%m.%Y')),  # First rabies shot
            valid_from=make_aware(datetime.strptime('01.06.2020', '%d.%m.%Y') + timedelta(days=7)),  # After 7 days
            valid_until=make_aware(datetime.strptime('01.06.2021', '%d.%m.%Y')),
        ),
        # Adult Booster Shots (Subsequent Years)
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Canine Distemper'),
            batch_number='D123B02',
            manufacturer='Zoetis',
            manufacture_date=make_aware(datetime.strptime('10.12.2020', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('01.06.2021', '%d.%m.%Y')),  # Booster shot
            valid_until=make_aware(datetime.strptime('01.06.2022', '%d.%m.%Y')),
        ),
        dict(
            pet=pet,
            vaccine=Vaccine.objects.get(name='Rabies'),
            batch_number='R456B02',
            manufacturer='Pfizer',
            manufacture_date=make_aware(datetime.strptime('15.03.2021', '%d.%m.%Y')),
            date_of_vaccination=make_aware(datetime.strptime('01.06.2021', '%d.%m.%Y')),  # Yearly Rabies booster
            valid_from=make_aware(datetime.strptime('01.06.2021', '%d.%m.%Y') + timedelta(days=7)),
            valid_until=make_aware(datetime.strptime('01.06.2022', '%d.%m.%Y')),
        ),

    ]

    for data in vaccines_data:
        # Use get_or_create with unpacked data to ensure no duplicates
        VaccinationRecord.objects.get_or_create(**data)

    print('Vaccination records for Max populated')


if __name__ == '__main__':
    create_superuser()
    create_pets()
    populate_vaccines()
    populate_vaccination_records()
    populate_drugs()
    populate_medication_records()
    create_complete_examination_record_for_max()