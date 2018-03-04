var employee = "" +
"<li>" +
"    <a href='${link}' class='employee-profile-link'>${name}</a>" +
"    <input type='hidden' name='employee-id' value='${id}' />" +
"    <input type='hidden' name='employee-email' value='${email}' />" +
"    <input type='hidden' name='employee-short_old' value='${short_old}' />" +
"    <input type='hidden' name='employee-short_new' value='${short_new}' />" +
"    <input type='hidden' name='employee-teacher' value='${teacher}' />" +
"</li>";

$.template( "employee", employee );
