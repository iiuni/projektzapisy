$(document).ready(function () {
  let previousInput;
  let selectedStudentIds = $("#id_students option")
    .map(function () {
      return $(this).val();
    })
    .get();
  $("#id_selected_students").val(selectedStudentIds.join(","));
  $("#id_students").find("option:selected").prop("selected", false);

  function debounce(func, delay) {
    let timer;
    return function () {
      const context = this;
      const args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () {
        func.apply(context, args);
      }, delay);
    };
  }

  function handleInput() {
    const inputValue = $("#id_user_input").val().trim();

    if (inputValue === previousInput || inputValue === "") {
      return;
    }
    previousInput = inputValue;

    $.ajax({
      url: ajaxUrl,
      type: "GET",
      data: {
        input_value: inputValue,
        csrfmiddlewaretoken: csrfToken,
      },
      success: function (data) {
        const students = data.filtered_students;
        const allStudentsElement = $("#id_all_students");
        const pickedStudentIds = $("#id_students option")
          .map(function () {
            return $(this).val();
          })
          .get();

        allStudentsElement.empty();
        students.forEach(function (student) {
          if (!pickedStudentIds.includes(student.id.toString())) {
            allStudentsElement.append(
              `<option value='${student.id}'>${student.name} (${student.matricula})</option>`
            );
          }
        });
      },
      error: function (xhr, status, error) {
        console.error("Something went wrong :(");
      },
    });
  }

  function updateSelectedStudents() {
    const all_students = $("#id_all_students");
    const picked_students = $("#id_students");

    picked_students.find("option:selected").each(function () {
      all_students.append($(this).clone().prop("selected", false));
      const student_id = $(this).val();
      const index = selectedStudentIds.indexOf(student_id);
      selectedStudentIds.splice(index, 1);
      $(this).remove();
    });

    all_students.find("option:selected").each(function () {
      picked_students.append($(this).clone().prop("selected", false));
      selectedStudentIds.push($(this).val());
      $(this).remove();
    });
    $("#id_selected_students").val(selectedStudentIds.join(","));
    console.log("Selected Student IDs:", selectedStudentIds);
    console.log("Hidden input value:", $("#id_selected_students").val());
  }

  const debouncedInputHandler = debounce(handleInput, 200);
  $("#id_user_input").on("input", debouncedInputHandler);
  $("#id_all_students, #id_students").on("change", updateSelectedStudents);
});
