$(function () {
    var loginDropdown = $('#login-dropdown');
    var btnShowLoginForm = $('#btn-no-usos');
    var loginForm = $('#login-without-usos');

    loginDropdown.bind('click', function () {
	btnShowLoginForm.show();
	loginForm.hide();
    });

    btnShowLoginForm.bind('click', function (event) {
	event.stopPropagation();
	$(this).hide();
	loginForm.show();
    });
});
