const openPopupBtn = document.getElementById('open-popup-btn');
const openPopupEdit = document.getElementsByClassName('open-popup-edit');
const closePopupBtn = document.getElementById('close-popup-btn');
const popup = document.getElementById('popup');
const overlay = document.getElementById('popup-overlay');
const popupForm = document.getElementById('user-form');


openPopupBtn.addEventListener("click", function (event) {
    event.preventDefault(); // جلوگیری از رفتار پیش‌فرض فرم
    popup.style.display = 'block';
    overlay.style.display = 'block';

    popupForm.children[0].value = ""
    popupForm.children[1].value = ""
    popupForm.children[2].value = ""
    popupForm.children[3].value = ""
    popupForm.children[4].value = ''
    popupForm.action = "/add_user"
});

for (let i = 0; i < openPopupEdit.length; i++) {
    const button = openPopupEdit[i];
    const arrayString = button.value.match(/\[.*\]/)[0];
    const jsonString = arrayString.replace(/'/g, '"');
    const dataArray = JSON.parse(jsonString);
    const [id, phone, name, code, coldroom] = dataArray;

    button.addEventListener('click', () => {
        popup.style.display = 'block';
        overlay.style.display = 'block';
        popupForm.children[0].value = name
        popupForm.children[1].value = phone
        popupForm.children[2].value = code
        popupForm.children[3].value = coldroom
        popupForm.children[4].value = id
        popupForm.action = "/edit_user"
    });
}

// بستن پاپ‌آپ
closePopupBtn.addEventListener('click', () => {
    popup.style.display = 'none';
    overlay.style.display = 'none';
});

// بستن پاپ‌آپ با کلیک روی فضای بیرونی
overlay.addEventListener('click', () => {
    popup.style.display = 'none';
    overlay.style.display = 'none';

});


