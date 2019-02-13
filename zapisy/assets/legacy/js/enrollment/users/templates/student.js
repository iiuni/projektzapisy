var student = "" +
"<li>" +
"    <a href='${link}' class='student-profile-link'>${name}</a>" +
"    <input type='hidden' name='student-user-id' value='${id}' />" +
"    <input type='hidden' name='student-email' value='${email}' />" +
"    <input type='hidden' name='student-album' value='${album}' />" +
"    <input type='hidden' name='student-recorded' value='${recorded}' />" +
"</li>";

$.template( "student", student );
