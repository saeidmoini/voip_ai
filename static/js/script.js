const openPopupBtn = document.getElementById('open-popup-btn');
const closePopupBtn = document.getElementById('close-popup-btn');
const popup = document.getElementById('popup');
const overlay = document.getElementById('popup-overlay');
const userForm = document.getElementById('user-form');

// باز کردن پاپ‌آپ
openPopupBtn.addEventListener('click', () => {
    popup.style.display = 'block';
    overlay.style.display = 'block';
});

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
