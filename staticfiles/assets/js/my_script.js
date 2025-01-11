var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value

function addAndRemoveFromCart(id, action) {


    var item_id_selector = document.getElementsByClassName(`${id}_id_item_count`);
    var item_id = document.getElementsByClassName(`${id}_id_item_id`)[0].value;


    if (action.toString().trim() === 'add') {
        console.log(action, 'add')
        console.log('Add item to cart')
        var url = add_to_cart_url;
        if (item_id_selector.length > 1) {
            for (let i = 0; i < item_id_selector.length; i++) {
                console.log(item_id_selector[i].value)
                item_id_selector[i].value = parseInt(item_id_selector[i].value) + 1;
            }
        } else {
            item_id_selector[0].value = parseInt(item_id_selector[0].value) + 1;
        }

    } else {
        var url = remove_from_cart_url;
        console.log('Remove item from cart')
        if (item_id_selector.length > 1) {
            for (let i = 0; i < item_id_selector.length; i++) {
                let value = parseInt(item_id_selector[i].value)
                if (Number(value) > 0) {
                    item_id_selector[i].value = Number(value) - 1;
                }
            }
        } else {
            if (Number(parseInt(item_id_selector[0].value)) > 0) {
                item_id_selector[0].value = Number(parseInt(item_id_selector[0].value)) - 1;
            }
        }
    }
    if (Number(item_id_selector[0].value) >= 0) {
        console.log("the is Number(item_id_selector[0].value ", Number(item_id_selector[0].value))
        fetch(url, {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin',
            body: JSON.stringify({
                'item_count': item_id_selector[0].value,
                'item_id': item_id,
            })
        }).then(async (res) => {
            var response = await res.json()
            var status_code = await res.status
            console.log('status_code', status_code)
            console.log('response of wait', response);
            if (status_code === 200) {
                changePriceAndCount(response)
                if (Number(item_id_selector[0].value) === 0) {
                    location.reload()
                }
            }
        }).catch((error) => {
            console.log(error);
        })
    }

}

function changePriceAndCount(response) {
    console.log(response)
    var total_item_count_selector = document.getElementsByClassName('total_item_count')
    var total_item_amount_selector = document.getElementsByClassName('total_item_amount')

    for (let i = 0; i < total_item_count_selector.length; i++) {
        console.log('count', i)
        console.log(total_item_count_selector.length)
        total_item_count_selector[i].innerHTML = `${response['total_item_count']}+`
    }
    for (let i = 0; i < total_item_amount_selector.length; i++) {
        console.log('amount', i)
        console.log(total_item_amount_selector.length)
        total_item_amount_selector[i].innerHTML = `$${response['total_item_amount']}`
    }
    if (response['order_item_id']) {
        var order_item_price = document.getElementsByClassName(`${response['order_item_id']}order_item_price`)
        for (let i = 0; i < order_item_price.length; i++) {
            console.log('order_item_price', i)
            console.log(order_item_price.length)
            order_item_price[i].innerHTML = `$${response['order_item_price']}`
        }
    }

}

const addPickUpLocation = (item_id) => {
    fetch(change_pickup_location_url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
            'item_id': item_id,
        })
    }).then(async (res) => {
        await res.json()
        if (res.status === 200) {
            console.log('Location changed')
        }
    }).catch((error) => {
        console.log(error);
    })

}
const addShippingRoutine = (item_id) => {
    fetch(change_shipping_routine_url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
            'item_id': item_id,
        })
    }).then(async res => {
            if (res.status === 200) {
                console.log('Shipping routine changed')
                var response = await res.json()
                console.log(response)
                changePriceAndCount(response)
            }
        }
    ).catch((error) => {
        console.log(error);
    })

}


var shipping_form = document.getElementById('shipping_form');
shipping_form.addEventListener('submit', function submit(event) {
    event.preventDefault();
    submit_form(shipping_form, update_shipping_url)
    Swal.fire({
        "imageUrl": logo_url,
        "imageHeight": 50,
        "imageAlt": 'Gimsap',
        "confirmButtonColor": '#ff3838',
        "text": 'Shipping address was successfully updated..',
    })


})
var profile_form = document.getElementById('profile_form');
profile_form.addEventListener('submit', function submit(event) {
    event.preventDefault();
    submit_form(profile_form, update_customer_url)
    Swal.fire({
        "imageUrl": logo_url,
        "imageHeight": 50,
        "imageAlt": 'Gimsap',
        "confirmButtonColor": '#ff3838',
        "text": 'Profile info was successfully updated..',
    })
})


var subscription_form = document.getElementById('subscription_form');
subscription_form.addEventListener('submit', function (event) {
    event.preventDefault();
    submit_form(subscription_form, subscription_url)
})

function subscribe_email(event) {
    event.preventDefault();
    submit_form(subscription_form, subscription_url)
}

function submit_form(form_element, url) {
    var data = {}
    for (let i = 0; i < form_element.length; i++) {
        console.log(form_element.elements[i].name)
        data[form_element.elements[i].name] = form_element.elements[i].value;
    }
    console.log(data)
    fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: JSON.stringify(data)
    }).then(async (res) => {
        var response = await res.json()
        console.log('response of wait', response);

    }).catch((error) => {
        console.log(error);
    })
}


function add_or_remove_wishlist(id, action) {

    fetch(add_to_wishlist_url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
            'id': id,
            'action': action
        })
    }).then(async (res) => {
        var response = await res.json()
        console.log('response of wait', response);
        var wishlist_item_count = document.getElementsByClassName('wishlist_item_count')

        for (let i = 0; i < wishlist_item_count.length; i++) {
            console.log('count', i)
            console.log(wishlist_item_count.length)
            wishlist_item_count[i].innerHTML = response['wishlist_item_count']
        }

    }).catch((error) => {
        console.log(error);
    })
}


function submit_order_form(orderData) {
    // submitting the form
    var form = document.getElementById('payment-form');
    // Insert the token ID into the form, so it gets submitted to the server
    var hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('type', 'hidden');
    hiddenInput.setAttribute('name', 'payment_id');
    hiddenInput.setAttribute('value', orderData.id);
    form.appendChild(hiddenInput);
    // Insert the Json Response into the form, so it gets submitted to the server
    var hiddenInputPaymentInfo = document.createElement('input');
    hiddenInputPaymentInfo.setAttribute('type', 'hidden');
    hiddenInputPaymentInfo.setAttribute('name', 'payment_info');
    hiddenInputPaymentInfo.setAttribute('value', JSON.stringify(orderData, null, 2));
    form.appendChild(hiddenInputPaymentInfo);

    console.log('The hidden input', hiddenInput)
    // Submit the form
    HTMLFormElement.prototype.submit.call(form);
}