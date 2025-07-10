const openPopupBtn = document.getElementById("open-popup-btn");
const openPopupEdit = document.getElementsByClassName("open-popup-edit");
const closePopupBtn = document.getElementById("close-popup-btn");
const popup = document.getElementById("popup");
const overlay = document.getElementById("popup-overlay");
const popupForm = document.getElementById("user-form");
const popupExplain = document.getElementById("popupExplain");
const popupDiscription = document.getElementById("popupDiscription");
const openExplain = document.getElementById("open-explain");
const openDiscription = document.getElementById("open-discription");


openPopupBtn.addEventListener("click", function (event) {
  event.preventDefault(); // جلوگیری از رفتار پیش‌فرض فرم
  popup.style.display = "block";
  overlay.style.display = "block";

  popupForm.children[0].value = "";
  popupForm.children[1].value = "";
  popupForm.children[2].value = "";
  popupForm.children[3].value = "";
  popupForm.children[4].value = "";
  popupForm.children[5].value = "";
  popupForm.action = "/add_user";
});

for (let i = 0; i < openPopupEdit.length; i++) {
  const button = openPopupEdit[i];
  const arrayString = button.value.match(/\[.*\]/)[0];
  const jsonString = arrayString.replace(/None/g, "null").replace(/'/g, '"');
  let dataArray;
  try {
    dataArray = JSON.parse(jsonString);
  } catch (error) {
    console.error("Invalid JSON format:", error);
  }
  const [id, phone, name, city, code, coldroom] = dataArray;

  button.addEventListener("click", () => {
    popup.style.display = "block";
    overlay.style.display = "block";
    popupForm.children[0].value = name || "";
    popupForm.children[1].value = phone || "";
    popupForm.children[2].value = city || "";
    popupForm.children[3].value = code || "";
    popupForm.children[4].value = coldroom || "";
    document.getElementById("user-id").value = id || "";
    popupForm.action = "/edit_user";
  });
}

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


// کد مربوط به جدول کاربران و جستجو
$(document).ready(function () {
    $("#userSearch").on("keyup", function () {
      var value = $(this).val().toLowerCase();
      $("#userTable tr").filter(function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
      });
    });
});

function showAlert(msg, status) {
  Toastify({
    text: `${msg}`,
    duration: 2000,
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
