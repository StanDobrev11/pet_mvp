const domain = window.getDomain()
const csrftoken = window.getCookie('csrftoken')

document.querySelectorAll('.code-input').forEach((input, index, inputs) => {
    input.addEventListener('input', function () {
        if (this.value.length === 1 && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }
    });

});

document.getElementById('access-code-form').addEventListener('submit', function (e) {
    e.preventDefault();  // Prevent the form from submitting


    const inputs = document.querySelectorAll('.code-input');
    let accessCode = '';
    let isValid = true;  // Flag to check if the form is valid

    inputs.forEach(input => {
        const value = input.value.trim();
        if (value === '' || isNaN(value)) {
            input.classList.add('invalid'); // Add a class for invalid inputs
            isValid = false;  // Mark form as invalid
        } else {
            input.classList.remove('invalid'); // Remove invalid class if it's valid
            accessCode += value;
        }
    });

    if (!isValid) {
        alert('Please fill all cells with valid numbers.');
        return;  // Prevent form submission if validation fails
    }

    return fetch(`${DOMAIN}/api/access-codes/verify/`, {
        method: "POST",
        headers: {
            'content-type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'code': accessCode
        })
    })
        .then(res => {
            // If response is ok, parse it as JSON
            if (res.ok) {
                return res.json();
            } else {
                // If not ok, we still parse the response body to get error details
                return res.json().then(errorData => {
                    throw new Error(errorData.error); // Throw an error with the message
                });
            }
        })
        .then(data => {
            const passportId = data.pk
            sessionStorage.setItem('passportId', passportId);
            window.location.href='../dashboard/'
            
            // return fetch(`${DOMAIN}/api/passports/${passportId}/`)
            //     .then(res => {
            //         if (res.ok) {
            //             return res.json()
            //         } else {
            //             return res.json().then(errorData => {
            //                 throw new Error(errorData.error);
            //             })
            //         }
            //     })
            //     .then(data => {
            //         const passportData = data
            //         window.location.href='../doctor-dashboard/'
            //     })
        })
        .catch(e => console.log(e))

});