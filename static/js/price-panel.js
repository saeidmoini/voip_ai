const overlay = document.getElementById("popup-overlay");
const popup = document.getElementById("popup");
const closePopupBtn = document.getElementById("close-popup-btn");
const popupExplain = document.getElementById("popupExplain");
const popupDiscription = document.getElementById("popupDiscription");
const openExplain = document.getElementById("open-explain");
const openDiscription = document.getElementById("open-discription");

document.getElementById('increase_btn').addEventListener('click', () => {
    const pre_value = document.getElementById("toggle-sign").textContent;
    let value = document.getElementById('increase_input').value.trim();
    value = pre_value === "-" ? pre_value + value : value;
    

    if (!value || isNaN(value)) {
        Toastify({
            text: "لطفاً درصد تغییر را درست وارد کنید.",
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
  popupExplain.style.display = "none";
  popupDiscription.style.display = "none";
}

// بستن پاپ‌آپ با کلیک روی فضای بیرونی
overlay.addEventListener("click", () => {
  closeAllPopups();
});


// پاپ آپ ها مربوط متن توضیحات و شرح کالا
function showAlert(msg, status) {
  Toastify({
    text: `${msg}`,
    duration: 1000,
    gravity: "top",
    position: "right",
    style: {
        background: status === "success" ? "#4CAF50" : "#f44336",
    },
  }).showToast();
};
// اضافه کردن عملکرد برای باز کردن popup توضیحات
openExplain.addEventListener("click", function() {
  closeAllPopups();
  fetch("/api/get-prd-explain-text")
    .then(response => response.json())
    .then(data => {
      popupExplain.querySelector("textarea").value = data.text || ""; 
      popupExplain.style.display = "block";
      overlay.style.display = "block";
    })
    .catch(error => {
      showAlert("خطا در بارگذاری متن شرح کالا!", "error");
    });
});

// اضافه کردن عملکرد برای باز کردن popup توضیحات
openDiscription.addEventListener("click", function() {
  closeAllPopups();
  fetch("/api/get-description-text")
    .then(response => response.json())
    .then(data => {
      popupDiscription.querySelector("textarea").value = data.text || ""; 
      popupDiscription.style.display = "block";
      overlay.style.display = "block";
    })
    .catch(error => {
      showAlert("خطا در بارگذاری متن توضیحات!", "error");
    });
});

// ارسال تغییرات شرح کالا به سرور
document.querySelector("#popupExplain button").addEventListener("click", function() {
  const text = popupExplain.querySelector("textarea").value;

  fetch("/api/set-prd-explain-text", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: text }),
  })
    .then(response => {
      if (response.ok) {
        showAlert("تغییرات با موفقیت ذخیره شد", "success");
        popupExplain.style.display = "none";
        overlay.style.display = "none";
      } else {
        showAlert("خطا در ذخیره تغییرات!", "error");
      }
    })
    .catch(error => {
      showAlert("خطا در ذخیره تغییرات!", "error");
    });
});

// ارسال تغییرات توضیحات پیش فاکتور به سرور
document.querySelector("#popupDiscription button").addEventListener("click", function() {
  const text = popupDiscription.querySelector("textarea").value;

  fetch("/api/set-description-text", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: text }),
  })
    .then(response => {
      if (response.ok) {
        showAlert("تغییرات با موفقیت ذخیره شد", "success");
        popupDiscription.style.display = "none";
        overlay.style.display = "none";
      } else {
        showAlert("خطا در ذخیره تغییرات!", "error");
      }
    })
    .catch(error => {
      showAlert("خطا در ذخیره تغییرات!", "error");
    });
});

// بستن پاپ‌آپ شرح کالا 
document.getElementById("close-explain").addEventListener("click", function() {
  popupExplain.style.display = "none";
  overlay.style.display = "none";
});

// بستن پاپ‌آپ توضیحات
document.getElementById("close-discription").addEventListener("click", function() {
  popupDiscription.style.display = "none";
  overlay.style.display = "none";
});

// دکمه مثبت و منفی برای درصد تغییر قیمت ها

function toggleSign() {
  const pre_value = document.getElementById("toggle-sign");
  pre_value.textContent = pre_value.textContent === "+" ? "-" : "+";
}