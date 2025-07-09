document.getElementById('increase_btn').addEventListener('click', () => {
    const value = document.getElementById('increase_input').value.trim();
    if (!value || isNaN(value)) {
        Toastify({
            text: "لطفاً درصد افزایش معتبر وارد کنید.",
            duration: 2000,
            gravity: "top",
            position: "right",
            style: {
                background: "#f44336"
            },
        }).showToast();
        return;
    }

    fetch(`/api/increase-prices?increase_value=${encodeURIComponent(value)}`, {
        method: 'POST',
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.status == 200) {
            Toastify({
            text: "prices increased successful",
            duration: 2000,
            gravity: "top",
            position: "right",
            style: {
                background: "#4CAF50"
            },
            }).showToast();

            setTimeout(() => {
                window.location.reload();
            }, 2000);

            return;
        }
    })
    .catch(err => {
        Toastify({
            text: err.message,
            duration: 4000,
            gravity: "top",
            position: "right",
            style: {
                background: "#f44336"
            },
        }).showToast();
        console.error(err);
    });
});
