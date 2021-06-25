// Update the footer year to current year
$('#footerYear').text(new Date().getFullYear());

// Change the dropdown menu direction in the navbar on medium and small screens
if (screen.width < 1024) {
    $('.dropdown').removeClass('dropleft');
};

// Enable Submit Button on Sign Up page when the confirm password matches the password
$('#Rpassword').on('keyup', function () {
    passwordVal = $('#password').val();
    RpasswordVal = $('#Rpassword').val();

    if (passwordVal === RpasswordVal) {
        $('.registerBtn').prop('disabled', false);
    } else {
        $('.registerBtn').prop('disabled', true);
    }
});

$('.profileNavItem').each((key, value) => {
    $(value).click(() => {
        if ($(value).text() == "Trips") {
            $('.profileFeed').addClass('d-none');
            $('.tripsprofileFeed').removeClass('d-none');
        } else if ($(value).text() == "Followers") {
            $('.profileFeed').addClass('d-none');
            $('.followersFeed').removeClass('d-none');
        } else if ($(value).text() == "Following") {
            $('.profileFeed').addClass('d-none');
            $('.followingFeed').removeClass('d-none');
        } else if ($(value).text() == "Statistics") {
            $('.profileFeed').addClass('d-none');
            $('.statisticsFeed').removeClass('d-none');
        }
    })
});

// Get the modal
var addTripFormModal = $('#addTripFormModal');
let addTripButton = $('.addTripBtn');

// Get the <span> element that closes the modal
var closeModal = $('.close').first();

$(document).ready(() => {
// When the user clicks on the button, open the modal
addTripButton.click(() => {
    addTripFormModal.show(500);
});

// When the user clicks on <span> (x), close the modal
closeModal.click(() => {
    addTripFormModal.hide(500);
});

// When the user clicks anywhere outside of the modal, close it
$(document).click((event) => {
    if (!$(event.target).closest('#TripBtn,.modal-content').length) {
        addTripFormModal.hide(500);
    };
});

});
