// FUNCTIONS

// GO BACK
let goBackButton = document.getElementById('goBack');
goBackButton.addEventListener('click', function () {
  if (document.referrer) {
    window.history.back();
  } else {
    window.location.href = '/fallback-url';
  } 
})

