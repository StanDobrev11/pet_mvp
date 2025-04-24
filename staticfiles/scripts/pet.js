const petContainer = document.querySelector('.div.pet-container')
const petsUri = 'api/pets'

document.addEventListener('DOMContentLoaded', () => {
    
    fetchObjTranslatedFields('pet', petsUri);

    document.getElementById('add-pet').addEventListener('click', (e) => {
        e.preventDefault
        addPetClick()
        
    })
})


async function generateAccessCode() {
    const domain = window.getDomain();
    const petId = document.getElementById('view-pet-button').getAttribute('number')
    
    try {
        const res =  await fetch(`${domain}/api/access-codes/${petId}/`)
        const data = await res.json()
        
        const generatedCode = document.getElementById('generated-code')
        generatedCode.textContent = data.access_code       
    
    } catch (err) {
        console.log(err);
    }
       
}


function addPetClick() {

    if (!window.profileData) {
        return alert('Please add your profile data first!')
    }

}

function addPet() {

}

function viewPet(petData) {
    
    const petProps = [
        "name",
        "species",
        "breed",
        "sex",
        "date_of_birth",
        "color",
        "features",
    ]

    createImageOnCard(
        'pet', 
        '../../static/imgs/pet_profile.jfif',
        petData,
        petsUri,
    )


    if (petData) {
        displayObjData(petData, petProps, 'pet', petsUri)
    }


}


function getCardElements(containerName) {
    
    const container = document.querySelector(`.${containerName}-container`)
    const titleElement = container.querySelector(`#${containerName}-container-title`)
    const divElement = container.querySelector('div#form')
    const formElement = container.querySelector('form')
    const personalDiv = container.querySelector(`div#${containerName}-personal`)
    
    return [container, titleElement, divElement, formElement, personalDiv]
}

function displayObjData(objData, propList, containerName, objUri) {
    const titleMapper = {
        'profile': gettext('Profile'),
        'pet': gettext('Pet')
    }

    const translationMapper = {
        'profile': window.ownersTranslatedFieldsData,
        'pet': window.petTranslatedFieldsData
    }

    const [container, titleElement, divElement, formElement, personalDiv] = [...getCardElements(containerName)]
           
    displayElement('container', containerName)
    titleElement.textContent = titleMapper.containerName
    const translation = translationMapper[containerName]

    personalDiv.innerHTML = ''
    Object.keys(objData)
            .forEach(prop => {
                const value = objData[prop]

                const formWrapDiv = document.createElement('div')
                formWrapDiv.className = 'form-wrap'

                const propAsTag = parseProperty(prop)
                const propAsId = parseToKebapCase(prop)
                const label = document.createElement('label')
                label.setAttribute('for', propAsId)
                label.textContent = `${propAsTag}: `

                if (translation[prop]) {
                    label.textContent = `${translation[prop]}: `
                } 

                let select = document.createElement('select')
                const input = document.createElement('input')
                const span = document.createElement('span')
                span.classList.add('readonly')

                if (prop === 'country') {
                    select = createCountryDropdown(select, value)
                    select.setAttribute('disabled', '')
                    formWrapDiv.append(label, select, span)
                } else {

                    input.setAttribute('type', 'text')
                    input.setAttribute('id', propAsId)
                    input.setAttribute('name', propAsTag)
                    input.value = value
                    input.setAttribute('readonly', '')

                    formWrapDiv.append(...[label, input, span])
                }
                                
                input.addEventListener('keydown', (event) => {
                    if (!input.classList.contains('readonly') && event.key === 'Enter') {
                        span.click()
                    }
                })

                span.addEventListener('click', async (e) => {

                    if (span.classList.contains('readonly')) {
                        input.removeAttribute('readonly')
                        span.classList.remove('readonly')
                        select.removeAttribute('disabled')
                        select.focus()
                        input.focus()
                        input.select()
                        label.textContent += ' *'
                    } else {
    
                        let newValue = input.value
                        
                        if (e.target.previousSibling.tagName === 'SELECT') {
                            newValue = select.value
                        }
                        
                        if (newValue !== value) {
                            try {
                                const response = await patchObjectProperty(
                                    objData,
                                    objUri,
                                    prop, newValue
                                )

                                if (!response.ok) {
                                    const errorData = await response.json()

                                    for (const key in errorData) {
                                        if (errorData.hasOwnProperty(key)) {
                                            const errorMessages = `${propAsTag} -> ${errorData[key]}`
                                            alert(errorMessages)
                                        }
                                    }
                                    e.target.previousSibling.tagName === 'SELECT'
                                        ?select.value = value
                                        :input.value = value

                                    throw new Error(JSON.stringify(errorData))
                                }

                                input.setAttribute('readonly', '')
                                span.classList.add('readonly')
                                select.setAttribute('disabled', '')
                                label.textContent = label.textContent.replace(' *', '')
                                objData[prop] = newValue
                            } catch (err) { console.log(err.message) }

                        } else {
                            input.setAttribute('readonly', '')
                            span.classList.add('readonly')
                            select.setAttribute('disabled', '')
                            label.textContent = label.textContent.replace(' *', '')
                            objData[prop] = newValue
                        }
                    }
                })


                if (propList.includes(prop)) {
                    personalDiv.append(formWrapDiv)
                }
            })

}

function createImageOnCard(containerName, defautImgUrl, objData, objUri) {
    
    const photoDiv = document.querySelector(`div.${containerName}-photo`)
    photoDiv.innerHTML = ''

    const imgElement = document.createElement('img')
    imgElement.setAttribute('src', defautImgUrl)
    const inputFile = document.createElement('input')
    inputFile.setAttribute('type', 'file')
    inputFile.setAttribute('accept', 'image/*')
    inputFile.style.display = 'none'

    const imgSpan = document.createElement('span')
    imgSpan.classList.add('add')
    imgSpan.addEventListener('click', async () => {

        if (imgSpan.classList.contains('add')) {
            inputFile.click()
        } else {
            const response = await deleteObjectPhoto(objData, objUri, 'photo')

            if (!response.ok) {
                const errorData = await response.json()

                for (const key in errorData) {
                    if (errorData.hasOwnProperty(key)) {
                        const errorMessages = `Photo -> ${errorData[key]}`
                        alert(errorMessages)
                    }
                }

                throw new Error(JSON.stringify(errorData))
            }

            imgSpan.classList.add('add')
            imgSpan.classList.remove('delete')
            imgElement.setAttribute('src', defautImgUrl)
            objData['photo'] = null
        }

    })

    inputFile.addEventListener('change', async () => {
        const file = inputFile.files[0]
        if (file) {
            try {
                const response = await patchObjectPhoto(objData, objUri, 'photo', file)

                if (!response.ok) {
                    const errorData = await response.json()

                    for (const key in errorData) {
                        if (errorData.hasOwnProperty(key)) {
                            const errorMessages = `Photo -> ${errorData[key]}`
                            alert(errorMessages)
                        }
                    }

                    throw new Error(JSON.stringify(errorData))
                }

                const result = await response.json();
                imgElement.setAttribute('src', URL.createObjectURL(file));
                objData['photo'] = result.photo;
                imgSpan.classList.add('delete')
                imgSpan.classList.remove('add')
            } catch (error) { console.log(error.message) }
        }
    })

    if (objData['photo']) {
        imgElement.setAttribute('src', objData['photo'])
        imgSpan.classList.add('delete')
        imgSpan.classList.remove('add')
    }

    photoDiv.append(imgElement, inputFile, imgSpan)

}


