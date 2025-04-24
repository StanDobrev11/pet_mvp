async function fetchDoctorData(doctorId) {
    const domain = window.getDomain()
    const doctorUri = 'api/doctors'

    try {
        const resp = await fetch(`${domain}/${doctorUri}/${doctorId}`)

        if (!resp.ok) {
            const errorData = await resp.json()
            throw new Error(errorData)
        }

        return resp

    } catch (err) {
        console.log(err.message)
    }
}