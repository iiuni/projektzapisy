
window.onload = function () {

    function nonZeroSelectedStudents() {
        var options = document.getElementById("id_students").options;
        var counter = 0;

        for (let i = 0; i < options.length; i++) {
            if (options[i].selected) {
                counter++;
            }
        }

        return (counter > 0);
    }

    function showChange(reservedUntil) {
        reservedUntil.classList.add("red-borders");
        var intervalID = setInterval(function () {
            if (reservedUntil.classList.contains("red-borders")) {
                reservedUntil.classList.remove("red-borders");
            }
        }, 1500);
    }

    function changeOfDateField(requiredDate, reservedUntil) {
        
        var reservedUntilLabel = $('label[for="id_reserved_until"]');

        if (requiredDate) {
            var reservedUntilDate = new Date();
            reservedUntilDate.setFullYear(reservedUntilDate.getFullYear() + 2);
            var dd = String(reservedUntilDate.getDate()).padStart(2, '0');
            var mm = String(reservedUntilDate.getMonth() + 1).padStart(2, '0');
            var yyyy = reservedUntilDate.getFullYear();
            reservedUntilDate = yyyy + '-' + mm + '-' + dd;
            
            reservedUntil.value = reservedUntilDate;
            reservedUntil.disabled = false;
            showChange(reservedUntil);

            reservedUntilLabel.addClass('requiredField');
            reservedUntilLabel.append('<span class="asteriskField">*</span>');
            reservedUntil.classList.add('requiredField');
        } else {
            reservedUntil.value = "";
            reservedUntil.disabled = true;
            showChange(reservedUntil);
            
            reservedUntilLabel.removeClass('requiredField');
            var text = reservedUntilLabel.text();
            reservedUntilLabel.text(text.slice(0,text.length-13));            
        }
    }

    var studentsSelect = document.getElementById("id_students");
    var reservedUntil = document.getElementById('id_reserved_until');

    var requiredDate = nonZeroSelectedStudents();

    if(Boolean(reservedUntil.value) != requiredDate) {
        changeOfDateField(requiredDate, reservedUntil);
    }

    studentsSelect.addEventListener('change', function handleChange(event) {
        if (nonZeroSelectedStudents() != requiredDate) {
            requiredDate = !requiredDate;
            changeOfDateField(requiredDate, reservedUntil);
        }
        else if (Boolean(reservedUntil.value) != requiredDate) {

            changeOfDateField(requiredDate, reservedUntil);
        }
    });
};
