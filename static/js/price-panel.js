const overlay = document.getElementById("popup-overlay");
const popup = document.getElementById("popup");
const closePopupBtn = document.getElementById("close-popup-btn");

document.getElementById('increase_btn').addEventListener('click', () => {
    const value = document.getElementById('increase_input').value.trim();
    if (!value || isNaN(value)) {
        Toastify({
            text: "لطفاً درصد تغییر را وارد کنید.",
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
            text: "قیمت ها با موفقیت تغییر یافتند",
            duration: 1000,
            gravity: "top",
            position: "right",
            style: {
                background: "#4CAF50"
            },
            }).showToast();

            setTimeout(() => {
                window.location.reload();
            }, 1000);

            return;
        }
    })
    .catch(err => {
        Toastify({
            text: 'تغییر قیمت ها با خطا مواجه شد !',
            duration: 1000,
            gravity: "top",
            position: "right",
            style: {
                background: "#f44336"
            },
        }).showToast();
        console.error(err);
    });
});


document.getElementById('chn-price-btn').addEventListener('click', () => {
    overlay.style.display = "block"
    popup.style.display = "block"
});


// بستن پاپ‌آپ
closePopupBtn.addEventListener("click", () => {
  popup.style.display = "none";
  overlay.style.display = "none";
});

function closeAllPopups() {
  popup.style.display = "none";
  overlay.style.display = "none";
}

// بستن پاپ‌آپ با کلیک روی فضای بیرونی
overlay.addEventListener("click", () => {
  closeAllPopups();
});