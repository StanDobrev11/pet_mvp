const coverElement = document.getElementById('cover')
document.addEventListener('DOMContentLoaded', () => {
    displayPassportSection()
    coverElement.addEventListener('click', populateCoverPage)
})

function populateTables(sectionName, tableProps, nestedProps, doctor=true) {
    const divElement = document.querySelector(`div.${sectionName}.page`)
    const tbody = divElement.querySelector('tbody')
    tbody.innerHTML = ''
    const data = createPageTitle(sectionName)

    data.forEach(nestedData => {
        const tr = document.createElement('tr')

        tableProps.forEach(prop => {
            const td = document.createElement('td')
            td.textContent = nestedData[prop]
            tr.appendChild(td)
        })
        

        if (nestedProps.length !== 0) {
            const tdDiv = document.createElement('td')
            const rowDiv = document.createElement('div')
            rowDiv.classList.add('multi-row-header')
            nestedProps.forEach(prop => {
                const div = document.createElement('div')
                const span = document.createElement('span')
                div.append(span)
                span.textContent = nestedData[prop]
                rowDiv.append(div)
            })
            tdDiv.append(rowDiv)
            tr.appendChild(tdDiv)
        }

        async function getDoctorName() {
            const resp = await fetchDoctorData(nestedData['doctor'])
            const doctorData = await resp.json()

            const tdDocName = document.createElement('td')
            tdDocName.textContent = `Dr. ${doctorData['first_name']} ${doctorData['last_name']}`

            tr.append(tdDocName)
        }
        tbody.append(tr)
        if (doctor) {
            getDoctorName()
        }
        
    })

    pageFooterSection(divElement)
}

function populateOthersSection() {
    const tableProps = [
        "text_field"
    ]

    const nestedProps = [
    ]

    populateTables('other', tableProps, nestedProps, false)
}

function populateLegalisation() {
    const tableProps = [
        "legalising_body",
        "date_of_entry"
    ]

    const nestedProps = [
    ]

    populateTables('legalisation', tableProps, nestedProps)
}

function populateClinicalExaminationSection() {
    const tableProps = [
        "declaration",
        "date_of_entry"
    ]

    const nestedProps = [
    ]

    populateTables('clinical-examination', tableProps, nestedProps)
}

function populateOtherVaccinationSection() {
    const tableProps = [
        "manufacturer_and_name",
        "batch_number",
    ]

    const nestedProps = [
        "date_of_vaccination",
        "valid_until",
    ]

    populateTables('other-vaccination', tableProps, nestedProps)
}

function populateOtherParaisteTreatmentSection() {

    const tableProps = [
        "manufacturer_and_name",
    ]

    const nestedProps = [
        "date",
        "time",
    ]

    populateTables('other-parasites-treatment', tableProps, nestedProps)

}


function populateEchinococcusSection() {

    const tableProps = [
        "manufacturer_and_name",
    ]

    const nestedProps = [
        "date",
        "time",
    ]

    populateTables('antiechinococcus-treatment', tableProps, nestedProps)

}

function populateRabiesTestSection() {
    const divElement = document.querySelector('div.rabies-antibody-test.page')
    const sectionMain = document.querySelector(`.main.rabies-antibody-test.page`)
    sectionMain.innerHTML = ''
    const data = createPageTitle('rabies-antibody-test')

    function declaration(sectionName, record) {
        const divItem = document.createElement('div')
        divItem.classList.add(`${sectionName}-info-group`)
        const spanValue = document.createElement('span')
        spanValue.classList.add(`${sectionName}-value`)

        const text = `${record['translation']['declaration']}`

        spanValue.textContent = text
        divItem.append(spanValue)
        return divItem
    }

    const recordProps = [
        'sample_collected_on',
        'date_of_entry',
    ]


    data.forEach(record => {

        createMainSection(recordProps, 'rabies-antibody-test', record, false)
        sectionMain.prepend(declaration('rabies-antibody-test', record))

        async function getDoctorData() {
            const resp = await fetchDoctorData(record['doctor'])
            const doctorData = await resp.json()

            const doctorNameDiv = createDoctorName('rabies-antibody-test', doctorData)

            const doctorProps = [
                'address',
                'email',
            ]

            sectionMain.append(doctorNameDiv)
            doctorProps.forEach(prop => {
                const divItem = createSingleDiv(prop, 'rabies-antibody-test', doctorData)
                sectionMain.append(divItem)
            })

        }
        getDoctorData()
    })

    pageFooterSection(divElement)
}

function populateRabiesSection() {

    const tableProps = [
        "manufacturer_and_name",
        "batch_number",
    ]

    const nestedProps = [
        "date_of_vaccination",
        "valid_until",
        "valid_from",
    ]

    populateTables('rabies-vaccination', tableProps, nestedProps)
}

function populateIssuingSection() {
    const divElement = document.querySelector(`div.issuing.page`)
    const data = createPageTitle('issuing')

    const propsArray = [
        'address',
        'postal_code',
        'city',
        'country',
        'phone_number',
        'email',
    ]

    const sectionMain = createMainSection(propsArray, 'issuing', data)
    sectionMain.prepend(createDoctorName('issuing', data))
    sectionMain.append(createSingleDiv('date_of_issue', 'issuing', data))
    pageFooterSection(divElement)
}

function populateMarkingSection() {
    const divElement = document.querySelector('div.marking.page')

    const markingProps = [
        'code',
        'date_of_application',
        'location'
    ]
    const data = createPageTitle('marking')
    createMainSection(markingProps, 'marking', data)
    pageFooterSection(divElement)
}


function populateAnimalSection() {

    function createPhotoDiv(photo) {
        const divPhoto = document.createElement('div')
        divPhoto.classList.add('pet-photo')

        const imgEl = document.createElement('img')
        const hIntEl = document.createElement('h6')
        hIntEl.textContent = 'PICTURE OF THE ANIMAL (optional)'
        const hNatEl = document.createElement('h6')
        hNatEl.textContent = gettext('PICTURE OF THE ANIMAL (optional)')

        if (photo) {
            imgEl.setAttribute('src', photo)
            divPhoto.append(imgEl)
        } else {
            divPhoto.append(hNatEl, hIntEl)
        }

        return divPhoto
    }

    const divAnimal = document.querySelector('div.pet.page')
    const sectionMainAnimal = document.querySelector('.main.pet.page')
    const petSectionData = window.passportData['animal_section']
    const translated = petSectionData['translation']

    const secNum = petSectionData['section_number']
    const secTitleInt = petSectionData['section_title'].toUpperCase()
    const secTitleNat = translated['section_title'].toUpperCase()

    const titleNat = document.querySelector('.header.pet.page h6#national')
    titleNat.textContent = `${secNum}. ${secTitleNat}`
    const titleInter = document.querySelector('.header.pet.page h6#inter')
    titleInter.textContent = secTitleInt

    const petProps = [
        'name',
        'species',
        'breed',
        'sex',
        'date_of_birth',
        'color',
        'features',
    ]

    const sectionFrag = document.createDocumentFragment()
    sectionMainAnimal.innerHTML = ''

    const petData = petSectionData.pet

    const divPhoto = createPhotoDiv(petData.photo)
    sectionMainAnimal.append(divPhoto)

    petProps.forEach(prop => {
        const divItem = document.createElement('div')
        divItem.classList.add('pet-info-group')
        const spanLabel = document.createElement('span')
        spanLabel.classList.add('pet-label')
        const spanValue = document.createElement('span')
        spanValue.classList.add('pet-value')

        spanLabel.textContent = `${petData['translation'][prop]} / ${parseProperty(prop)}: `

        spanValue.textContent = petData[prop]

        divItem.append(spanLabel, spanValue)
        sectionFrag.append(divItem)
    })

    sectionMainAnimal.append(sectionFrag)
    pageFooterSection(divAnimal)
}

function populateOwnerSection() {
    const divOwnerPage = document.querySelector('div.owner.page')
    const sectionMainOwner = document.querySelector('.main.owner.page')
    const ownersData = window.passportData['owners_section']
    const translated = ownersData['translation']

    const secNum = ownersData['section_number']
    const secTitleInt = ownersData['section_title'].toUpperCase()
    const secTitleNat = translated['section_title'].toUpperCase()

    const titleNat = document.querySelector('.header.owner.page h6#national')
    titleNat.textContent = `${secNum}. ${secTitleNat}`
    const titleInter = document.querySelector('.header.owner.page h6#inter')
    titleInter.textContent = secTitleInt

    const owners = ownersData['owners']
    const ownerProps = [
        'first_name',
        'last_name',
        'address',
        'postal_code',
        'city',
        'country',
        'phone_number',
    ]

    const sectionFrag = document.createDocumentFragment()
    sectionMainOwner.innerHTML = ''
    owners.forEach(owner => {
        ownerProps
            .forEach(prop => {
                const divItem = document.createElement('div')
                divItem.classList.add('owner-info-group')
                const spanLabel = document.createElement('span')
                spanLabel.classList.add('owner-label')
                const spanValue = document.createElement('span')
                spanValue.classList.add('owner-value')

                spanLabel.textContent = `${owner['translation'][prop]} / ${parseProperty(prop)}: `

                spanValue.textContent = owner[prop]

                divItem.append(spanLabel, spanValue)
                sectionFrag.append(divItem)
            })
    })

    sectionMainOwner.append(sectionFrag)
    pageFooterSection(divOwnerPage)

}

function pageFooterSection(divElement) {

    function splitPassportNumber(num) {
        const transformed = num.replace(/^(\w{2})(\d{2}\w{2})(\d{6})$/, '$1 $2 $3');
        return transformed
    }

    const passportNum = splitPassportNumber(window.passportData['passport_number'])

    const footerSection = document.createElement('section')
    footerSection.classList.add('page-footer')
    const hElement = document.createElement('h5')
    hElement.classList.add('passport-number')
    hElement.setAttribute('id', 'passport-number')

    hElement.textContent = passportNum
    footerSection.appendChild(hElement)

    if (!divElement.lastElementChild.classList.contains('page-footer')) {
        divElement.append(footerSection)
    }

}

function populateNotesPage() {
    const divNotesPage = document.querySelector('div.notes.page')
    const notesData = window.passportData['notes_section']
    const translated = notesData['translation']

    const titleNat = document.querySelector('.header.notes.page h6#national')
    titleNat.textContent = translated['section_title']
    const titleInter = document.querySelector('.header.notes.page h6#inter')
    titleInter.textContent = notesData['section_title']

    const textElement = document.querySelector('.main.notes.page pre')
    textElement.innerHTML = ''
    const contentInt = notesData['content'].split('**')

    const contentNat = translated['content'].split('**')
    const ulElement = document.createElement('ul')

    for (let i = 0; i < contentNat.length; i++) {
        brEl = document.createElement('br')
        const liNatElement = document.createElement('li')
        const liIntElement = document.createElement('li')
        liNatElement.textContent = contentNat[i].trim()
        liIntElement.textContent = contentInt[i].trim()
        ulElement.append(liNatElement, liIntElement, brEl)

    }
    textElement.append(ulElement)

    pageFooterSection(divNotesPage)

}

async function populateCoverPage(passportNum) {
    try {
        const divCoverPage = document.querySelector('div.cover.page')
        const profileData = window.profileData
        const countries = window.countryChoices
        const lang = getCookie('lang')

        const interCountryCover = document.getElementById('inter-country-cover')
        const nationalCountryCover = document.getElementById('national-country-cover')

        let ownerCountry = profileData['country']
        const country = countries
            .find(pair => pair['value'] === ownerCountry)['label']

        let text = gettext("European Union")
        nationalCountryCover.textContent = text + `\n${country}`

        if (lang !== 'en') {
            const countryChoices = await fetchCountryChoices('en');
            const country = getCountryFullName(ownerCountry)
            const text = `European Union \n${country}`
            interCountryCover.textContent = text
        }

        const footerSection = pageFooterSection(divCoverPage)

    } catch (error) {
        console.log(error.message);
    }
}


async function viewPassport(passportNumber) {
    const domain = window.getDomain()
    const passportsUri = 'api/passports'
    try {
        const resp = await fetch(`${domain}/${passportsUri}/${passportNumber}`)


        if (!resp.ok) {
            const errorData = await resp.json()
            throw new Error(errorData.details)
        }

        const passportData = await resp.json()

        displayElement('container', 'passport')
        displayElement('section', 'cover')
        window.passportData = passportData
        highlightContentsElement('cover')
        populateCoverPage(passportData['passport_number'])
        populateNotesPage()
        populateOwnerSection()
        populateAnimalSection()
        populateMarkingSection()
        populateIssuingSection()
        populateRabiesSection()
        populateRabiesTestSection()
        populateEchinococcusSection()
        populateOtherParaisteTreatmentSection()
        populateOtherVaccinationSection()
        populateClinicalExaminationSection()
        populateLegalisation()
        populateOthersSection()

    } catch (err) { console.log(err.message); }
}

function displayPassportSection() {
    const ulContents = document.getElementById('contents')
    Array.from(ulContents.children)
        .forEach(section => {
            const aElementId = section.querySelector('a')
            const sectionName = aElementId.getAttribute('id')
            section.addEventListener('click', () => {
                displayElement('section', sectionName)
                highlightContentsElement(sectionName)
            })
        }
        )
}

function highlightContentsElement(targetElementName) {
    // will highlight clicked contents section

    const parentContainer = document.querySelector('ul.passport-contents')

    Array.from(parentContainer.children)
        .forEach(child => {
            child.classList.remove('highlight')
        })

    const target = parentContainer.querySelector(`#${targetElementName}`)
    target.parentElement.classList.add('highlight')

}

function createPageTitle(sectionName) {

    let parsedName = parseToSnakeCase(sectionName)

    const sectionData = window.passportData[`${parsedName}_section`]
    const translated = sectionData['translation']

    const secNum = sectionData['section_number']
    const secTitleInt = sectionData['section_title'].toUpperCase()
    const secTitleNat = translated['section_title'].toUpperCase()

    const titleNat = document.querySelector(`.header.${sectionName}.page h6#national`)
    titleNat.textContent = `${secNum}. ${secTitleNat}`
    const titleInter = document.querySelector(`.header.${sectionName}.page h6#inter`)
    titleInter.textContent = secTitleInt

    if (parsedName === 'issuing') {
        parsedName = 'doctor'
    } else if (parsedName === 'rabies_vaccination') {
        parsedName = 'rabies_vaccines'
    } else if (parsedName === 'rabies_antibody_test') {
        parsedName = 'rabies_antibody_tests'
    } else if (parsedName === 'antiechinococcus_treatment') {
        parsedName = 'echinococcus_treatment'
    } else if (parsedName === 'other_parasites_treatment') {
        parsedName = 'anti_parasite_treatment'
    } else if (parsedName === 'other_vaccination') {
        parsedName = 'other_vaccines'
    } else if (parsedName === 'clinical_examination') {
        parsedName = 'clinical_examinations'
    } else if (parsedName === 'other') {
        parsedName = 'other_records'
    }

    return sectionData[parsedName]

}

function createMainSection(array, sectionName, data, clearMainSec = true) {

    const sectionMain = document.querySelector(`.main.${sectionName}.page`)
    if (clearMainSec) {
        sectionMain.innerHTML = ''
    }

    const sectionFrag = document.createDocumentFragment()
    array.forEach(prop => {
        const divItem = document.createElement('div')
        divItem.classList.add(`${sectionName}-info-group`)
        const spanLabel = document.createElement('span')
        spanLabel.classList.add(`${sectionName}-label`)
        const spanValue = document.createElement('span')
        spanValue.classList.add(`${sectionName}-value`)


        spanLabel.textContent = `${data['translation'][prop]} / ${parseProperty(prop)}: `

        spanValue.textContent = data[prop]
        if (prop === 'country') {
            spanValue.textContent = getCountryFullName(data[prop])
        }

        divItem.append(spanLabel, spanValue)
        sectionFrag.append(divItem)
    })
    sectionMain.append(sectionFrag)
    return sectionMain

}

function createDoctorName(sectionName, data) {
    const text = `Dr. ${data['first_name']} ${data['last_name']}`
    const nameDiv = document.createElement('div')
    nameDiv.classList.add(`${sectionName}-info-group`)
    const spanLabel = document.createElement('span')
    spanLabel.classList.add(`${sectionName}-label`)
    const spanValue = document.createElement('span')
    spanValue.classList.add(`${sectionName}-value`)

    spanLabel.textContent = `${gettext('Name of authorized veterinarian')} / Name of authorized veterinarian: `
    spanValue.textContent = text

    nameDiv.append(spanLabel, spanValue)

    return nameDiv
}

function createSingleDiv(prop, sectionName, sectionData) {
    const divItem = document.createElement('div')
    divItem.classList.add(`${sectionName}-info-group`)
    const spanLabel = document.createElement('span')
    spanLabel.classList.add(`${sectionName}-label`)
    const spanValue = document.createElement('span')
    spanValue.classList.add(`${sectionName}-value`)

    spanLabel.textContent = `${sectionData['translation'][prop]} / ${parseProperty(prop)}: `
    spanValue.textContent = sectionData[prop]
    divItem.append(spanLabel, spanValue)

    return divItem
}