document.addEventListener("DOMContentLoaded", function () {
    console.log('it is loaded')
    const vaccineSelects = document.querySelectorAll('select[id$="-vaccine"]');
    console.log(vaccineSelects)

    vaccineSelects.forEach((vaccineSelect) => {
        console.log('vaccineSelect')
        const formPrefix = vaccineSelect.id.replace("-vaccine", "");
        const dateInput = document.getElementById(`${formPrefix}-date_of_vaccination`);
        const validUntilInput = document.getElementById(`${formPrefix}-valid_until`);
        const validFromInput = document.getElementById(`${formPrefix}-valid_from`);
        const validFromWrapper = document.getElementById(`field-${formPrefix}-valid_from`);
        const customInputWrapper = document.getElementById(`custom-${formPrefix}-wrapper`);

        function updateOnVaccineChange() {
            console.log('update on change')
            const selectedOption = vaccineSelect.options[vaccineSelect.selectedIndex];
            const value = selectedOption.value;
            const isCustom = value === "custom";
            const interval = parseInt(selectedOption.getAttribute("data-interval"));

            if (isCustom) {
                if (customInputWrapper) customInputWrapper.style.display = "block";
                if (validUntilInput) validUntilInput.value = "";
                if (validFromInput) validFromInput.value = "";
                if (validFromWrapper) validFromWrapper.style.display = "none";
            } else {
                if (customInputWrapper) customInputWrapper.style.display = "none";

                if (interval && dateInput && dateInput.value) {
                    const d = new Date(dateInput.value);
                    d.setDate(d.getDate() + interval - 1);
                    if (validUntilInput) validUntilInput.value = d.toISOString().split("T")[0];
                }

                const vaccineCoreName = selectedOption.getAttribute("data-core-name") || "";
                if (/rabies/i.test(vaccineCoreName) && dateInput && dateInput.value) {
                    const rabiesDate = new Date(dateInput.value);
                    rabiesDate.setDate(rabiesDate.getDate() + 21);
                    if (validFromInput) validFromInput.value = rabiesDate.toISOString().split("T")[0];
                    if (validFromWrapper) validFromWrapper.style.display = "block";
                } else {
                    if (validFromInput) validFromInput.value = "";
                    if (validFromWrapper) validFromWrapper.style.display = "none";
                }
            }
        }

        function updateValidUntilFromDate() {
            console.log('valid until')
            const selectedOption = vaccineSelect.options[vaccineSelect.selectedIndex];
            const interval = parseInt(selectedOption.getAttribute("data-interval"));
            if (!selectedOption || selectedOption.value === "custom") return;

            if (interval && dateInput && dateInput.value) {
                const d = new Date(dateInput.value);
                d.setDate(d.getDate() + interval - 1);
                if (validUntilInput) validUntilInput.value = d.toISOString().split("T")[0];
            }

            const vaccineName = selectedOption.textContent.toLowerCase();
            if (vaccineName.includes("rabies") && dateInput && dateInput.value) {
                const rabiesDate = new Date(dateInput.value);
                rabiesDate.setDate(rabiesDate.getDate() + 21);
                if (validFromInput) validFromInput.value = rabiesDate.toISOString().split("T")[0];
                if (validFromWrapper) validFromWrapper.style.display = "block";
            } else {
                if (validFromInput) validFromInput.value = "";
                if (validFromWrapper) validFromWrapper.style.display = "none";
            }
        }

        vaccineSelect.addEventListener("change", updateOnVaccineChange);
        if (dateInput) dateInput.addEventListener("change", updateValidUntilFromDate);
    });
});
