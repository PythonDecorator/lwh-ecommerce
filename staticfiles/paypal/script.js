function initPayPalButton() {
    paypal.Buttons({
        style: {
            shape: 'pill',
            color: 'gold',
            layout: 'vertical',
            label: 'buynow',

        },
        createOrder: function (data, actions) {
            return actions.order.create({
                purchase_units: [{
                    "amount": {
                        "currency_code": "USD",
                        "value": "{{ order.get_total }}"
                    }
                }]
            });
        },
        onApprove: function (data, actions) {
            return actions.order.capture().then(function (orderData) {

                // Full available details
                console.log('Capture result', orderData, JSON.stringify(orderData, null, 2));

                // Show a success message within this page, e.g.
                const element = document.getElementById('paypal-button-container');
                element.innerHTML = '';
                element.innerHTML = '<h3>Payment Processing do not Refresh the page</h3>';

                // submitting the form
                var form = document.getElementById('payment-form');
                // Insert the token ID into the form so it gets submitted to the server
                var hiddenInput = document.createElement('input');
                hiddenInput.setAttribute('type', 'hidden');
                hiddenInput.setAttribute('name', 'payment_id');
                hiddenInput.setAttribute('value', orderData.id);
                form.appendChild(hiddenInput);

                console.log('The hidden input', hiddenInput)
                // Submit the form
                HTMLFormElement.prototype.submit.call(form);

            });
        },
        onError: function (err) {
            console.log(err);
        }
    }).render('#paypal-button-container');
    console.log('done!');
}

initPayPalButton();



  <script src="https://www.paypal.com/sdk/js?client-id=sb&enable-funding=venmo&currency=USD" data-sdk-integration-source="button-factory"></script>