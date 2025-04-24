document.addEventListener('DOMContentLoaded', async () => {

    await fetchUserData();
    if (window.userData.is_owner) {
        await fetchProfileData('owner');
        fetchCountryChoices();
        fetchObjTranslatedFields('owners', ownersUri);
    } else if (window.userData.is_doctor) {
        await fetchProfileData('doctor');
        
    }
    

    document.getElementById('profile').addEventListener('click', function (e) {
        e.preventDefault()
        profileClick()
    });
});

// Function to create user account fields
function createUserFields() {
    const userData = window.userData

    const userDiv = document.createElement('div')
    userDiv.setAttribute('id', 'user')

    const label = document.createElement('label')
    label.setAttribute('for', 'email')
    label.textContent = gettext('Email')

    const input = document.createElement('input')
    input.setAttribute('type', 'email')
    input.setAttribute('readonly', '')
    input.setAttribute('name', 'email')
    input.value = userData['email']

    userDiv.append(label, input)

    return userDiv
}


function profileClick() {
    const profileData = window.profileData
    const profilePropsList = [
        'first_name',
        'last_name',
        'phone_number',
        'street',
        'street_number',
        'district',
        'city',
        'country',
        'postal_code',
    ]

    const profileContainer = document.querySelector('.profile-container')
    profileContainer.innerHTML = ''

    const titleElement = document.createElement('h2')


    const divElement = document.createElement('div')
    divElement.setAttribute('id', 'form')

    const formElement = document.createElement('form')

    const imgDiv = document.createElement('div')
    imgDiv.setAttribute('id', 'image')
    imgDiv.classList.add('card')
    const profilePhotoDiv = document.createElement('div')
    profilePhotoDiv.classList.add('profile-photo')
    const imgElement = document.createElement('img')
    imgElement.setAttribute('src', '../../static/imgs/profile.png')
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
            const response = await deleteObjectPhoto(profileData, ownersUri, 'photo')

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
            imgElement.setAttribute('src', '../../static/imgs/profile.png')
            profileData['photo'] = null
        }

    })

    inputFile.addEventListener('change', async () => {
        const file = inputFile.files[0]
        if (file) {
            try {
                const response = await patchObjectPhoto(profileData, ownersUri, 'photo', file)

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
                profileData['photo'] = result.photo; // Assuming the server returns the photo URL
                imgSpan.classList.add('delete')
                imgSpan.classList.remove('add')
            } catch (error) { console.log(error.message) }
        }
    })

    profilePhotoDiv.append(imgElement, inputFile, imgSpan)
    imgDiv.append(profilePhotoDiv)


    const personalDiv = document.createElement('div')
    personalDiv.setAttribute('id', 'personal')
    personalDiv.classList.add('card')

    if (profileData) {
        // display fetched profile data
        displayElement('container', 'profile')
        titleElement.textContent = gettext('Profile')
        const translation = window.ownersTranslatedFieldsData

        if (profileData['photo']) {
            imgElement.setAttribute('src', profileData['photo'])
            imgSpan.classList.add('delete')
            imgSpan.classList.remove('add')
        }

        Object.keys(profileData)
            .forEach(prop => {
                const value = profileData[prop]

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
                                    profileData,
                                    ownersUri,
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
                                profileData[prop] = newValue
                            } catch (err) { console.log(err.message) }

                        } else {
                            input.setAttribute('readonly', '')
                            span.classList.add('readonly')
                            select.setAttribute('disabled', '')
                            label.textContent = label.textContent.replace(' *', '')
                            profileData[prop] = newValue
                        }
                    }
                })


                if (profilePropsList.includes(prop)) {
                    personalDiv.append(formWrapDiv)
                }
            })

        formElement.append(imgDiv, personalDiv)
        divElement.appendChild(formElement)
        profileContainer.append(titleElement, divElement)

    } else {
        // generate and post form data for new profile
        displayElement('container', 'profile')
        titleElement.textContent = gettext('Create New Profile')
        profilePropsList.forEach(prop => {

            const formWrapDiv = document.createElement('div')
            formWrapDiv.className = 'form-wrap'

            const propAsTag = parseProperty(prop)
            const propAsId = parseToKebapCase(prop)
            const label = document.createElement('label')
            label.setAttribute('for', propAsId)
            label.textContent = `${propAsTag}: `
            let select = document.createElement('select')

            if (prop === 'country') {
                select = createCountryDropdown(select)
                select.value = 'BG'
                formWrapDiv.append(label, select)
            } else {

                const input = document.createElement('input')
                input.setAttribute('type', 'text')
                input.setAttribute('id', propAsId)
                input.setAttribute('name', propAsTag)

                formWrapDiv.append(...[label, input])
            }

            if (profilePropsList.includes(prop)) {
                personalDiv.append(formWrapDiv)
            }

        })
        const buttonsDiv = document.createElement('div')
        buttonsDiv.classList.add('buttons')

        const submitBtn = document.createElement('button')
        submitBtn.setAttribute('type', 'submit')
        submitBtn.classList.add('btn')
        submitBtn.textContent = gettext('Submit')

        buttonsDiv.appendChild(submitBtn)

        formElement.append(imgDiv, personalDiv, buttonsDiv)
        divElement.appendChild(formElement)
        profileContainer.append(titleElement, divElement)

        submitBtn.addEventListener('click', (e) => {
            e.preventDefault()
            const formData = gatherFormData(formElement)
            postNewProfile(formData)
        })
    }
}

function createCountryDropdown(select, selectedValue) {
    select.setAttribute('name', 'country');
    const countryChoices = window.countryChoices

    countryChoices.forEach(choice => {
        const option = document.createElement('option');
        option.setAttribute('value', choice.value);
        option.textContent = choice.label;
        if (choice.value === selectedValue) {
            option.setAttribute('selected', 'selected');
        }
        select.appendChild(option);
    });

    return select;
}

function gatherFormData(form) {
    const formData = {};

    form.querySelectorAll('input').forEach(input => {
        const prop = parseToSnakeCase(input.name)
        const value = input.value
        if (value !== '') {
            formData[prop] = value;
        }
    
    });

    const country = form.querySelector('select').value
    formData['country'] = country

    return formData;
}

async function postNewProfile(data) {
    const domain = window.getDomain()
    const csrftoken = getCookie('csrftoken')
    const userId = getUserId()

    data['user'] = userId

    try {
        const response = await fetch(`${domain}/${ownersUri}/`, {
            method: 'POST',
            headers: {
                'content-type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(data)
        })

        if (!response.ok) {
            const errorData = await response.json()

            for (const key in errorData) {
                if (errorData.hasOwnProperty(key)) {
                    const errorMessages = `${gettext("Plese correct")} -> ${errorData[key]}`
                    alert(errorMessages)
                }
            }
        }
        alert(gettext("Profile created"))
        location.reload()


    } catch (error) { console.log(error.message); }
}