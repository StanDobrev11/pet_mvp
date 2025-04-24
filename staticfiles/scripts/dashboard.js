const apiPetsUri = 'api/pets'

document.addEventListener('DOMContentLoaded', async () => {
    loadAllPets()
    
    document.getElementById('dashboard').addEventListener('click', function (e) {
        e.preventDefault()
        displayElement('container', 'dashboard')
    });
})

const setLanguage = getCookie('lang')

async function loadAllPets() {
    const domain = window.getDomain()
    const apiPetsUri = 'api/pets'
    
    try {
        const resp = await fetch(`${domain}/${apiPetsUri}`, {
            headers: {
                'Accept-Language': setLanguage
            }
        });

        const petsData = await resp.json();

        if (!resp.ok) {
            throw new Error('Failed to fetch pets\n' + petsData.detail);
        }
      
        Object.values(petsData)
            .forEach(pet => {
                displayPetCard(pet);
        });

    } catch (err) {
        console.log(err);
    }
}


function displayPetCard(pet) {

    const translation = pet['translation']
    const overviewProps = ['name', 'breed', 'age', 'photo', 'current_weight']

    const petListEl = document.getElementById('pet-list')

    const divPetCard = document.createElement('div')
    divPetCard.classList.add('pet-card')
    divPetCard.setAttribute('id', 'pet-card')

    const imgDiv = document.createElement('div')
    imgDiv.classList.add('pet-img')
    imgDiv.setAttribute('id', 'pet-img')

    const detailsDiv = document.createElement('div')
    detailsDiv.classList.add('pet-details')
    detailsDiv.setAttribute('id', 'pet-details')

    const detailsList = []

    overviewProps.forEach(prop => {

        let translatedProp
        if (prop === 'age' && setLanguage !== 'en') {
            translatedProp = gettext('Age')
        } else if (translation[prop]) {
            translatedProp = translation[prop]
        } else {
            translatedProp = prop
        }

        if (prop === 'name') {
            const nameElement = document.createElement('h2')
            nameElement.textContent = `${translatedProp}: ${pet.name}`
            detailsList.push(nameElement)

        } else if (prop === 'photo') {
            const imgElement = document.createElement('img')

            !pet.photo
                ? imgElement.setAttribute('src', '../../static/imgs/pet_profile.jfif')
                : imgElement.setAttribute('src', pet.photo)
            imgDiv.append(imgElement)

        } else {
            const pElement = document.createElement('p')
            const firstLetterCaps = parseProperty(translatedProp)
            if (prop.includes('weight')) {
                const spanElement = document.createElement('span')
                spanElement.setAttribute('id', 'current-weight')
                pElement.textContent = `${firstLetterCaps}: `
                spanElement.textContent = `${pet[prop]} `
                pElement.append(spanElement)
                pElement.append(gettext('kgs'))

                const editButton = document.createElement('span')
                editButton.classList.add('edit-button')
                editButton.setAttribute('id', 'edit-weight-button')
                editButton.textContent = gettext('Update')

                editButton.addEventListener('click', async (e) => {

                    const currentWeight = spanElement.textContent
                    const newWeight = prompt(gettext("Enter new weight:"), currentWeight)

                    if (newWeight !== null && !isNaN(newWeight) && newWeight.trim() !== "") {
                        const response = await patchObjectProperty(pet, apiPetsUri, prop, newWeight)
                        if (!response.ok) {
                            const errorData = await response.json()
                            const errorMessage = errorData[prop][0]
                            alert(errorMessage)
                        } else {
                            spanElement.textContent = Number(newWeight).toFixed(1)
                        }
                    } else if (newWeight !== null) {
                        alert(gettext("Please enter a valid weight."))
                    }
                })
                pElement.append(editButton)
            } else {
                pElement.textContent = `${firstLetterCaps}: ${pet[prop]}`
            }
            detailsList.push(pElement)
        }
    })

    const divPassport = document.createElement('div')
    divPassport.setAttribute('id', 'passport-button')
    const pPassport = document.createElement('p')
    const aPassport = document.createElement('a')
    aPassport.setAttribute('id', 'view-passport')
    aPassport.textContent = gettext('View Passport')
    aPassport.addEventListener('click', async () => {
        const passport_number = pet['passport_number']
        await viewPassport(passport_number)
        divPassport.setAttribute('number', passport_number)
    })
    
    pPassport.appendChild(aPassport)
    divPassport.appendChild(pPassport)
    detailsList.push(divPassport)
    
    const divViewPet = document.createElement('div')
    divViewPet.setAttribute('id', 'view-pet-button')
    const pViewPet = document.createElement('p')
    const aViewPet = document.createElement('a')
    aViewPet.setAttribute('id', 'view-pet')
    aViewPet.textContent = gettext('View Pet')
    aViewPet.addEventListener('click', () => {
        viewPet(pet)
        divViewPet.setAttribute('number', pet.id)
    })

    pViewPet.appendChild(aViewPet)
    divViewPet.appendChild(pViewPet)
    detailsList.push(divViewPet)
    
    detailsDiv.append(...detailsList)
    divPetCard.append(imgDiv, detailsDiv)
    petListEl.append(divPetCard)
}
