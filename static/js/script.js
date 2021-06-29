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

// Show/hide different feeds on profile page
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

// Get the modal form to add new trip
var addTripFormModal = $('#addTripFormModal');
let addTripButton = $('.addTripBtn');
var closeModal = $('.close').first();

$(document).ready(() => {
addTripButton.click(() => {
    addTripFormModal.show(500);
});

closeModal.click(() => {
    addTripFormModal.hide(500);
});

$(document).click((event) => {
    if (!$(event.target).closest('#TripBtn,.modal-content').length) {
        addTripFormModal.hide(500);
    };
});

});

// Enable Submit Button on add new trip form when there is any value in the 
// select elements and input file type limit is less than or equal 15
$('.selectElNewTrip').each((key, value) => {
    $(value).on('change', () => {
        if (($('#trip_category').val() && $('#trip_country').val() && $('#trip_privacy').val()) && ($('#trip_photos')[0].files.length <= 15)) {
            $('.tripAddBtn').prop('disabled', false);
        } else {
            $('.tripAddBtn').prop('disabled', true);
        }
    });
});

// Create a photo preview on new trip form
$('#trip_photos').on('change', () => {
    const uploadedFiles = trip_photos.files
    $(uploadedFiles).each((key, value) => {
        const img_url = URL.createObjectURL(value)
        $(`<img src='${img_url}' alt=''>`).appendTo("#newTripPrev");
    });
});