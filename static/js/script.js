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

// Open modal
function modal(openButton, modal, closeBtn) {

    openButton.click(() => {
        modal.show(500);
    });

    closeBtn.click(() => {
        modal.hide(500);
    });
};

// Get the modal form to add new trip
let addTripFormModal = $('#addTripFormModal');
let addTripButton = $('.addTripBtn');
let tripBtn = $('#TripBtn');
let closeAddTripBtn = $('#addTripClose')

modal(addTripButton, addTripFormModal, closeAddTripBtn);

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

    let numberPics = Object.keys(uploadedFiles)

    if (numberPics.length > 15) {
        $('.previewImages').hide(500)
        $("#trip_photos").addClass('alertValidation')
        $('.previewPicture').remove()
    } else if (numberPics.length == 0) {
        $('.previewImages').hide(500)
        $("#trip_photos").removeClass('alertValidation')
        $('.previewPicture').remove()
    } else {
        $('.previewImages').show(500)
        $("#trip_photos").removeClass('alertValidation')
        $('.previewPicture').remove()
        $(uploadedFiles).each((key, value) => {
            let img_url = URL.createObjectURL(value)
            $(`<div>
                 <img class="previewPicture img-centered" src="${img_url}" alt="">
               </div>`).appendTo("#newTripPrev");
        });
    };
});

// Open delete confirmation
$('.deletePost').each((key, value) => {
    let button_id = $(value).attr('id');
    let button_el = $(`#${button_id}`);

    $(button_el).click(() => {
        let closeBtn = $('.closeDeleteConfirm');
        let delete_btn_id = $(button_el).attr('id');
        let delete_btn = $(`#${delete_btn_id}`);
        let id = delete_btn_id.slice(-1);
        let modal_id = `deleteTripModal_${id}`;
        let modal_el = $(`#${modal_id}`);

        modal(delete_btn, modal_el, closeBtn);
    });
});
