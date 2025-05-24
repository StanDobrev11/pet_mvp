import os
from datetime import datetime, timedelta

import django
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.timezone import make_aware



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_mvp.settings')
django.setup()

from pet_mvp.pets.models import Pet, Transponder, Tattoo
from pet_mvp.drugs.models import Vaccine, Drug, BloodTest, UrineTest, FecalTest
from pet_mvp.records.models import VaccinationRecord, MedicationRecord, MedicalExaminationRecord
from pet_mvp.accounts.models import Clinic

UserModel = get_user_model()

def create_clinic():

    clinic = Clinic.objects.get_or_create(
        email='dyana.vet@abv.bg',
        password='1234',
        clinic_name='Diana Vet',
        is_owner=False,
        phone_number='0887142536',
        clinic_address='123 Some Address',
        city='Varna',
        country='Bulgaria',
    )

    if clinic[1]:
        print('Clinic created')
    else:
        print('Clinic already exists')


def create_pet_markings():
    max_pet = Pet.objects.get(name='Max')
    luna_pet = Pet.objects.get(name='Luna')

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
    except Exception as e:
        print(f"Error creating transponder for {max_pet.name}: {e}")

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
    except Exception as e:
        print(f"Error creating tattoo for {luna_pet.name}: {e}")


def create_complete_examination_record_for_max():
    max_pet = Pet.objects.get(name='Max')
    clinic = Clinic.objects.get(clinic_name='Diana Vet')
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
        blood_test = BloodTest.objects.get(result="WBC and RBC levels normal, low platelets detected")
        urine_test = UrineTest.objects.get(result="Clear urine, neutral pH")
        fecal_test = FecalTest.objects.get(result="Parasites detected, blood in sample found")

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


def create_superuser(email='admin@petpal.cloudmachine.uk', password='1234'):
    try:
        UserModel.objects.create_superuser(
            email=email,
            password=password,
            first_name='Admin',
            last_name='Superuser',
            city='Varna',
            country='Bulgaria',
            phone_number='0887888888',
            is_owner=True,
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
            name_en='Max',
            name_bg='Макс',
            species='Dog',
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
            species='Cat',
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


def populate_drugs():
    treatment_data = [
        # Internal Parasites
        dict(
            name='Drontal Puppy',
            name_en='Drontal Puppy',
            name_bg='Дронтал Пъпи',
            notes='Targets roundworms, hookworms, and whipworms. Keeps puppy and family safe from internal parasites.',
            notes_en='Targets roundworms, hookworms, and whipworms. Keeps puppy and family safe from internal parasites.',
            notes_bg='Действа срещу кръгли червеи, анкилостоми и камшичести червеи. Предпазва кученцето и семейството от вътрешни паразити.',
        ),
        dict(
            name='Panacur',
            name_en='Panacur',
            name_bg='Панакур',
            notes='Effective against roundworms, hookworms, tapeworms, and whipworms in dogs and puppies.',
            notes_en='Effective against roundworms, hookworms, tapeworms, and whipworms in dogs and puppies.',
            notes_bg='Ефективен срещу кръгли червеи, анкилостоми, тении и камшичести червеи при кучета и кученца.',
        ),
        dict(
            name='Interceptor Plus',
            name_en='Interceptor Plus',
            name_bg='Интерцептор Плюс',
            notes='Protects against heartworms, tapeworms, hookworms, and roundworms. A monthly chewable tablet for dogs.',
            notes_en='Protects against heartworms, tapeworms, hookworms, and roundworms. A monthly chewable tablet for dogs.',
            notes_bg='Предпазва от сърдечни червеи, тении, анкилостоми и кръгли червеи. Месечна дъвчаща таблетка за кучета.',
        ),
        # External Parasites
        dict(
            name='Frontline Plus',
            name_en='Frontline Plus',
            name_bg='Фронтлайн Плюс',
            notes='Topical treatment protecting dogs from fleas, ticks, and lice. Apply monthly for prevention.',
            notes_en='Topical treatment protecting dogs from fleas, ticks, and lice. Apply monthly for prevention.',
            notes_bg='Локално лечение, предпазващо кучетата от бълхи, кърлежи и въшки. Прилагайте месечно за превенция.',
        ),
        dict(
            name='Advantix',
            name_en='Advantix',
            name_bg='Адвантикс',
            notes='Protects against fleas, ticks, mosquitoes, and biting flies. External spot-on treatment for dogs.',
            notes_en='Protects against fleas, ticks, mosquitoes, and biting flies. External spot-on treatment for dogs.',
            notes_bg='Предпазва от бълхи, кърлежи, комари и хапещи мухи. Външно локално лечение за кучета.',
        ),
        dict(
            name='NexGard',
            name_en='NexGard',
            name_bg='НексГард',
            notes='Chewable tablet for dogs that kills fleas and ticks. Monthly dosage recommended.',
            notes_en='Chewable tablet for dogs that kills fleas and ticks. Monthly dosage recommended.',
            notes_bg='Дъвчаща таблетка за кучета, която убива бълхи и кърлежи. Препоръчва се месечна доза.',
        ),
        # Regular Medication
        dict(
            name='Thyro-Tabs',
            name_en='Thyro-Tabs',
            name_bg='Тиро-Табс',
            notes='Used for treating hypothyroidism in dogs. Provides levothyroxine replacement therapy.',
            notes_en='Used for treating hypothyroidism in dogs. Provides levothyroxine replacement therapy.',
            notes_bg='Използва се за лечение на хипотиреоидизъм при кучета. Осигурява заместителна терапия с левотироксин.',
        ),
        dict(
            name='Vetoryl',
            name_en='Vetoryl',
            name_bg='Веторил',
            notes="Used for treating hyperadrenocorticism (Cushing's disease) in dogs.",
            notes_en="Used for treating hyperadrenocorticism (Cushing's disease) in dogs.",
            notes_bg="Използва се за лечение на хиперадренокортицизъм (болест на Кушинг) при кучета.",
        ),
        dict(
            name='Carprofen (Rimadyl)',
            name_en='Carprofen (Rimadyl)',
            name_bg='Карпрофен (Римадил)',
            notes='Commonly used as an anti-inflammatory and pain-relief medication for dogs with arthritis or after surgery.',
            notes_en='Commonly used as an anti-inflammatory and pain-relief medication for dogs with arthritis or after surgery.',
            notes_bg='Често се използва като противовъзпалително и обезболяващо лекарство за кучета с артрит или след операция.',
        ),
        dict(
            name='Apoquel',
            name_en='Apoquel',
            name_bg='Апоквел',
            notes='Provides relief for dogs from itching and inflammation associated with allergies.',
            notes_en='Provides relief for dogs from itching and inflammation associated with allergies.',
            notes_bg='Осигурява облекчение за кучета от сърбеж и възпаление, свързани с алергии.',
        ),
    ]

    for data in treatment_data:
        try:
            # Try to get the existing drug
            drug = Drug.objects.get(name=data['name'])
            # Update the translation fields
            drug.name_en = data['name_en']
            drug.name_bg = data['name_bg']
            drug.notes_en = data['notes_en']
            drug.notes_bg = data['notes_bg']
            drug.save()
        except Drug.DoesNotExist:
            # If it doesn't exist, create a new one
            Drug.objects.create(**data)

    print('Drugs populated with translations')


def populate_vaccines():
    # First, let's get all existing vaccines
    existing_vaccines = {v.name.lower().strip(): v for v in Vaccine.objects.all()}

    vaccines = [
        # Core Vaccines
        dict(
            name='Canine Distemper',
            name_en='Canine Distemper',
            name_bg='Кучешка чума',
            core=True,
            notes='This core vaccine protects against the highly contagious and potentially deadly distemper virus.',
            notes_en='This core vaccine protects against the highly contagious and potentially deadly distemper virus.',
            notes_bg='Тази основна ваксина предпазва от силно заразния и потенциално смъртоносен вирус на чумата.',
        ),
        dict(
            name='Rabies',
            name_en='Rabies',
            name_bg='Бяс',
            core=True,
            notes='Rabies is a fatal, viral disease that attacks the central nervous system and usually is transmitted through the bite of an infected animal.',
            notes_en='Rabies is a fatal, viral disease that attacks the central nervous system and usually is transmitted through the bite of an infected animal.',
            notes_bg='Бясът е фатално вирусно заболяване, което атакува централната нервна система и обикновено се предава чрез ухапване от заразено животно.',
        ),
        dict(
            name='Parvoviridae',
            name_en='Parvoviridae',
            name_bg='Парвовироза',
            core=True,
            notes='The vaccine guards against the highly contagious parvovirus, which causes life-threatening gastrointestinal illness.',
            notes_en='The vaccine guards against the highly contagious parvovirus, which causes life-threatening gastrointestinal illness.',
            notes_bg='Ваксината предпазва от силно заразния парвовирус, който причинява животозастрашаващо стомашно-чревно заболяване.',
        ),
        dict(
            name='Leptospirosis',
            name_en='Leptospirosis',
            name_bg='Лептоспироза',
            core=True,
            notes='The vaccine protects against leptospirosis, a bacterial infection that can cause kidney and liver failures, bleeding disorders, etc.',
            notes_en='The vaccine protects against leptospirosis, a bacterial infection that can cause kidney and liver failures, bleeding disorders, etc.',
            notes_bg='Ваксината предпазва от лептоспироза, бактериална инфекция, която може да причини бъбречна и чернодробна недостатъчност, нарушения в кръвосъсирването и др.',
        ),
        dict(
            name='Adenovirus (Infectious Hepatitis)',
            name_en='Adenovirus (Infectious Hepatitis)',
            name_bg='Аденовирус (Инфекциозен хепатит)',
            core=True,
            notes='Protects against canine adenovirus type 1, causing infectious hepatitis, and type 2, a respiratory illness.',
            notes_en='Protects against canine adenovirus type 1, causing infectious hepatitis, and type 2, a respiratory illness.',
            notes_bg='Предпазва от кучешки аденовирус тип 1, причиняващ инфекциозен хепатит, и тип 2, респираторно заболяване.',
        ),
        dict(
            name='Parainfluenza',
            name_en='Parainfluenza',
            name_bg='Парагрип',
            core=True,
            notes='Parainfluenza is part of the core combination vaccine and protects against a virus causing upper respiratory illness.',
            notes_en='Parainfluenza is part of the core combination vaccine and protects against a virus causing upper respiratory illness.',
            notes_bg='Парагрипът е част от основната комбинирана ваксина и предпазва от вирус, причиняващ заболяване на горните дихателни пътища.',
        ),
        # Non-Core Vaccines
        dict(
            name='Bordetella (Kennel Cough)',
            name_en='Bordetella (Kennel Cough)',
            name_bg='Бордетела (Кучешка кашлица)',
            core=False,
            notes='This non-core vaccine protects against Bordetella bronchiseptica, a leading cause of kennel cough in dogs.',
            notes_en='This non-core vaccine protects against Bordetella bronchiseptica, a leading cause of kennel cough in dogs.',
            notes_bg='Тази неосновна ваксина предпазва от Bordetella bronchiseptica, водеща причина за кучешка кашлица при кучетата.',
        ),
        dict(
            name='Lyme Disease (Borrelia Burgdorferi)',
            name_en='Lyme Disease (Borrelia Burgdorferi)',
            name_bg='Лаймска болест (Борелия Бургдорфери)',
            core=False,
            notes='This non-core vaccine is recommended for dogs at risk of exposure to ticks that carry Lyme disease.',
            notes_en='This non-core vaccine is recommended for dogs at risk of exposure to ticks that carry Lyme disease.',
            notes_bg='Тази неосновна ваксина се препоръчва за кучета с риск от излагане на кърлежи, които пренасят Лаймска болест.',
        ),
        dict(
            name='Canine Influenza',
            name_en='Canine Influenza',
            name_bg='Кучешки грип',
            core=False,
            notes='Canine influenza vaccine helps protect dogs against highly contagious respiratory viruses (H3N8 and H3N2).',
            notes_en='Canine influenza vaccine helps protect dogs against highly contagious respiratory viruses (H3N8 and H3N2).',
            notes_bg='Ваксината срещу кучешки грип помага за защита на кучетата от силно заразни респираторни вируси (H3N8 и H3N2).',
        ),
        dict(
            name='Corona Virus (Canine)',
            name_en='Corona Virus (Canine)',
            name_bg='Коронавирус (Кучешки)',
            core=False,
            notes='The canine coronavirus vaccine protects against intestinal upset caused by this specific type of virus. It is non-core and rarely recommended.',
            notes_en='The canine coronavirus vaccine protects against intestinal upset caused by this specific type of virus. It is non-core and rarely recommended.',
            notes_bg='Ваксината срещу кучешки коронавирус предпазва от стомашно-чревно разстройство, причинено от този специфичен тип вирус. Тя е неосновна и рядко се препоръчва.',
        ),
        dict(
            name='Rattlesnake Vaccine',
            name_en='Rattlesnake Vaccine',
            name_bg='Ваксина срещу ухапване от гърмяща змия',
            core=False,
            notes='An optional vaccine that may help dogs in high-risk areas produce antibodies against rattlesnake venom.',
            notes_en='An optional vaccine that may help dogs in high-risk areas produce antibodies against rattlesnake venom.',
            notes_bg='Незадължителна ваксина, която може да помогне на кучетата във високорискови райони да произвеждат антитела срещу отровата на гърмящата змия.',
        )
    ]

    for data in vaccines:
        # Check if a vaccine with this name (case-insensitive) already exists
        normalized_name = data['name'].lower().strip()
        if normalized_name in existing_vaccines:
            # Update the existing vaccine
            vaccine = existing_vaccines[normalized_name]
            vaccine.name_en = data['name_en']
            vaccine.name_bg = data['name_bg']
            vaccine.notes_en = data['notes_en']
            vaccine.notes_bg = data['notes_bg']
            vaccine.core = data['core']
            vaccine.save()
        else:
            # Create a new vaccine
            try:
                Vaccine.objects.create(**data)
            except Exception as e:
                print(f"Error creating vaccine {data['name']}: {e}")

    print('Vaccines populated with translations')


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
    create_clinic()
    create_pet_markings()
    populate_vaccines()
    populate_vaccination_records()
    populate_drugs()
    populate_medication_records()
    create_complete_examination_record_for_max()
    