window.onload = function () {
    if (document.querySelector('.promo-code')) {
        document.querySelector('.promo-code-btn').addEventListener('click', function() {
            document.querySelector('.promo-code').classList.toggle('code-hidden');
        })
    }
};
