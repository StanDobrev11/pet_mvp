const ownersUri = 'api/owners'
const doctorsUri = 'api/doctors'
const userApiUri = 'accounts/api'


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getDomain() {
    return window.DOMAIN
}

function getUserId() {
    return window.USERID
}

function displayElement(parrentClass, targetElement) {
    // will display the named element and hide all others

    const parentContainer = document.querySelector(`.${parrentClass}`)

    Array.from(parentContainer.children)
        .forEach(child => {
            child.classList.contains(`${targetElement}-${parrentClass}`)
                ? child.classList.remove('hidden')
                : child.classList.add('hidden')
        })

}

function parseProperty(prop) {
    // Split the property by underscores, capitalize the first letter of each word, and join them with spaces
    return prop
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}


function parseToKebapCase(prop) {
    return prop.split('_').join(' ')
                
}

function parseToSnakeCase(prop) {
    return prop
        .split('-')
        .map(ch => ch.toLowerCase())
        .join('_')
}

function changeLanguage(lang) {
    const currentUrl = window.location.href;
    const newUrl = new URL(currentUrl);
    newUrl.searchParams.set('lang', lang);
    window.location.href = newUrl;
}


async function patchObjectProperty(obj, objUri, propName, newValue) {
    const domain = window.getDomain()
    const csrftoken = window.getCookie('csrftoken')

    const bodyData = {}
    bodyData[propName] = newValue

    obj.user
        ? id = obj.user
        : id = obj.id

    return await fetch(`${domain}/${objUri}/${id}/`, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrftoken,
            'content-type': 'application/json'
        },
        body: JSON.stringify(bodyData)
    })
}



async function patchObjectPhoto(obj, objUri, propName, newValue) {
    const domain = window.getDomain()
    const csrftoken = window.getCookie('csrftoken')

    const formData = new FormData()
    formData.append(propName, newValue)

    obj.user
        ? id = obj.user
        : id = obj.id

    return await fetch(`${domain}/${objUri}/${id}/`, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: formData
    })
}

async function deleteObjectPhoto(obj, objUri, propName) {
    const domain = window.getDomain();
    const csrftoken = window.getCookie('csrftoken');

    const id = obj.user
        ? obj.user
        : obj.id;

    return await fetch(`${domain}/${objUri}/${id}/`, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ [propName]: null }),
    });
}

function fetchCountryChoices(xLang = null) {
    const domain = window.getDomain();
    const countryChoicesUri = 'api/country-choices'

    const headers = {}
    if (xLang !== null) {
        headers['X-Lang'] = xLang
    }

    return fetch(`${domain}/${countryChoicesUri}`, {
        method: "GET",
        headers: headers
    })
    .then(res => res.json())
    .then(data => {
        if (isEmpty(headers)) {
            window.countryChoices = data;
        }
        return data;
    })
    .catch(e => {
        console.log(e.message);
        throw e; 
    });
}



function fetchObjTranslatedFields(name, objUri) {
    const domain = window.getDomain()

    return fetch(`${domain}/${objUri}/translated-fieldset`)
        .then(res => res.json())
        .then(data => {
            window[`${name}TranslatedFieldsData`] = data
        })
        .catch(e => console.log(e.message))
}


// function fetchOwnerTranslatedFields() {
//     const domain = window.getDomain()
//     const ownersTranslatedFieldsUti = 'api/owners/translated-fieldset'

//     return fetch(`${domain}/${ownersTranslatedFieldsUti}`)
//         .then(res => res.json())
//         .then(data => {
//             window.ownersTranslatedFieldsData = data
//         })
//         .catch(e => console.log(e.message))
// }

function isEmpty(obj) {
    return Object.keys(obj).length === 0 && obj.constructor === Object;
}


function getCountryFullName(country) {

    return window.countryChoices
                .find(pair => pair['value'] === country)['label']

}


async function fetchUserData() {
    const domain = getDomain()
    const userId = getUserId()

    try {
        const resp = await fetch(`${domain}/${userApiUri}/${userId}`)

        if (!resp.ok) {
            const errorData = await resp.json()
            throw new Error(errorData.detail)
        }
        const data = await resp.json()
        window.userData = data
        
    } catch (err) { console.log(err); }
}

async function fetchProfileData(userStatus) {
    const domain = window.getDomain()
    const userId = window.getUserId()
    const setLanguage = getCookie('lang')

    let uri
    if (userStatus === 'owner') {
        uri = ownersUri
    } else if (userStatus === 'doctor') {
        uri = doctorsUri
    }

    try {
        const resp = await fetch(`${domain}/${uri}/${userId}`, {
            headers: {
                'Accept-Language': setLanguage
            }
        })
        const data = await resp.json()

        if (!resp.ok) {
            throw new Error(data.detail)
        }

        window.profileData = data

    } catch (err) {
        console.log(err.message)
    }
}