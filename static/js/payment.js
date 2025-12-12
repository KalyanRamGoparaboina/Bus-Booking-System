// payment.js

document.addEventListener('DOMContentLoaded', function() {
    const paymentMethods = document.getElementsByName('payment_method');
    const cardDetails = document.getElementById('card-details');
    const upiDetails = document.getElementById('upi-details');
    const netBankingDetails = document.getElementById('net-banking-details');
    const walletDetails = document.getElementById('wallet-details');

    function showPaymentDetails() {
        cardDetails.style.display = 'none';
        upiDetails.style.display = 'none';
        netBankingDetails.style.display = 'none';
        walletDetails.style.display = 'none';

        const selectedMethod = document.querySelector('input[name="payment_method"]:checked').value;

        if (selectedMethod === 'card') {
            cardDetails.style.display = 'block';
        } else if (selectedMethod === 'upi') {
            upiDetails.style.display = 'block';
        } else if (selectedMethod === 'net_banking') {
            netBankingDetails.style.display = 'block';
        } else if (selectedMethod === 'wallet') {
            walletDetails.style.display = 'block';
        }
    }

    paymentMethods.forEach(method => {
        method.addEventListener('change', showPaymentDetails);
    });

    // Initialize the payment details display
    showPaymentDetails();
});
