// Update the footer year to current year
$('#footerYear').text(new Date().getFullYear());

// Change the dropdown menu direction in the navbar on medium and small screens
if (screen.width < 1024) {
    $('.dropdown').removeClass('dropleft');
}

// Enable Submit Button on Sign Up page when the confirm password matches the password
$('#Rpassword').on('keyup', function() {
    passwordVal = $('#password').val();
    RpasswordVal = $('#Rpassword').val();

    if (passwordVal === RpasswordVal) {
        $('.registerBtn').prop('disabled', false);
    } else {
        $('.registerBtn').prop('disabled', true);
    }
})

$(window).scroll(() => {
    if ($(window).scrollTop() > 400) {
        $('.floating-right-bottom-btn').css('display', 'block');
    } else {
        $('.floating-right-bottom-btn').css('display', 'none');
    };
});