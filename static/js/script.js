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

// Open delete trip confirmation
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

// Ajax to count the trips likes without refresh the page
$(document).ready(() => {
    $('.like').each((key, value) => {
        $(value).click((event) => {
            event.preventDefault();

            let trip_id = $(value).data('trip');

            let req = $.ajax({
                url: `/likes/${trip_id}`,
                type: 'POST',
                data: { trip: trip_id }
            });

            req.done((data) => {
                $(`#like_count_${trip_id}`).text(data.count_likes);
            });

        });
    });
});

// Blocks the pop up asking for form resubmission on refresh
// Code from https://www.webtrickshome.com/forum/how-to-stop-form-resubmission-on-page-refresh
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
};

// Ajax to delete photos without refresh the page
$(document).ready(() => {
    $('.deletePhotoBtn').each((key, value) => {
        $(value).click((event) => {
            event.preventDefault();

            let trip_id = $(value).data('trip');
            let filename = $(value).data('flname');
            let imgId = $(value).data('img');

            let req = $.ajax({
                url: `/delete_img/${trip_id}/${filename}`,
                type: 'POST',
                data: { trip: trip_id, filename: filename, imgId: imgId }
            });

            req.done((data) => {
                $(`#${imgId}`).remove();
            });

            let countPrevImg = $('.imgPrevWrapper').children().length - 1;
            if (countPrevImg > 15) {
                $('#trip_photos').hide(500);
            } else if (countPrevImg == 0) {
                $(`<h3 class="text-center">No photos to show</h3>`).appendTo('#editTripPrev');
            } else {
                $('#trip_photos').show(500);
            };

        });
    });

    let countPrevImg = $('.imgPrevWrapper').children().length;
    if (countPrevImg > 15) {
        $('#trip_photos').hide(500);
    } else {
        $('#trip_photos').show(500);
    };

    $('#trip_photos').on('change', () => {
        countInputFiles = $('#trip_photos')[0].files.length;
        totalInputFiles = countInputFiles + countPrevImg;
        if (totalInputFiles > 15) {
            $('.updateTripBtn').prop('disabled', true);
            $('.previewImages').hide(500)
            $('.previewPicture').remove()
            $('#trip_photos').addClass('alertValidation');
        } else if (totalInputFiles = 0) {
            $('.updateTripBtn').prop('disabled', false);
            $('.previewImages').hide(500)
            $('.previewPicture').remove()
            $('#trip_photos').removeClass('alertValidation');
        } else {
            $('.updateTripBtn').prop('disabled', false);
            $('.previewImages').show(500)
            $('#trip_photos').removeClass('alertValidation');
        };

    });

});

// Open delete photo confirmation
$('.delEditImg').each((key, value) => {
    let button_id = $(value).attr('id');
    let button_el = $(`#${button_id}`);

    $(button_el).click(() => {
        let closeBtn = $('.closeDeleteConfirm');
        let delete_btn_id = $(button_el).attr('id');
        let delete_btn = $(`#${delete_btn_id}`);
        let modal_id = `deletePhotoModal_${delete_btn_id}`;
        let modal_el = $(`#${modal_id}`);

        modal(delete_btn, modal_el, closeBtn);
    });
});

// Apply active style to pagination button
$('.pageLink').each((key, value) => {
    let pageText = $(value).text();
    let pageData = $(value).data('page');

    if (pageData == pageText) {
        $(value).addClass('active');
    };
});

// Google maps api from google maps api documentation
let map;
let service;
let infowindow;

function initMap() {
    infowindow = new google.maps.InfoWindow();
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 5,
    });
    const request = {
        query: $('#placeName').text(),
        fields: ["name", "geometry"],
    };
    service = new google.maps.places.PlacesService(map);
    service.findPlaceFromQuery(request, (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK && results) {
            for (let i = 0; i < results.length; i++) {
                createMarker(results[i]);
            }
            map.setCenter(results[0].geometry.location);
        }
    });
}

function createMarker(place) {
    if (!place.geometry || !place.geometry.location) return;
    const marker = new google.maps.Marker({
        map,
        position: place.geometry.location,
    });
    google.maps.event.addListener(marker, "click", () => {
        infowindow.setContent(place.name || "");
        infowindow.open(map);
    });
}

// Open photo modal
$('.tripPhoto').each((key, value) => {
    let button_id = $(value).attr('id');
    let button_el = $(`#${button_id}`);

    $(button_el).click(() => {
        let closeBtn = $('.closetripPhotoModal');
        let photo_btn_id = $(button_el).attr('id');
        let photo_btn = $(`#${photo_btn_id}`);
        let modal_id = `tripPhotoModal_${photo_btn_id}`;
        let modal_el = $(`#${modal_id}`);

        modal(photo_btn, modal_el, closeBtn);
    });
});

// Ajax to follow request
$(document).ready(() => {
    $('#followBtn').click((event) => {
        event.preventDefault();

        let user_id = $('#followBtn').data('id');
        let button = $('#followBtn');
        let buttonHtml = $('#followBtn').html();

        let req = $.ajax({
            url: `/notification/${user_id}`,
            type: 'POST',
            data: { user_id: user_id }
        });

        req.done((data) => {
            if (buttonHtml == 'Follow <i class="fas fa-user-plus" aria-hidden="true"></i>') {
                button.removeClass('btn-outline-primary');
                button.addClass('btn-outline-warning');
                $(button).html('Remove follow request');
            } else {
                button.removeClass('btn-outline-warning');
                button.addClass('btn-outline-primary');
                $(button).html('Follow <i class="fas fa-user-plus"></i>');
            };
        });

    });
});

// Ajax to delete photos without refresh the page
$(document).ready(() => {
    $('.accept_btn').each((key, value) => {
        $(value).click((event) => {
            event.preventDefault();

            let button = $(value);
            let user_id = $(value).data('id');
            let ntf_id;

            $('.notification').each((key, value) => {
                $(value).click(() => {
                    ntf_id = $(value).attr('id');
                });
            });

            let req = $.ajax({
                url: `/follow_request/${user_id}`,
                type: 'POST',
                data: { user: user_id }
            });

            req.done((data) => {
                $(`#${ntf_id}`).remove();
            });

        });
    });
});