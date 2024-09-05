// FUNCTIONS

// SEE MORE

document.addEventListener('DOMContentLoaded', function() {
  const seeMoreBtn = document.getElementById('see-more-btn');
  const seeMoreContainer = document.querySelector('.see-more-container');

  if (seeMoreBtn && seeMoreContainer) {
    seeMoreBtn.addEventListener('click', function() {
      if (seeMoreContainer.classList.contains('expanded')) {
        seeMoreContainer.classList.remove('expanded');
        seeMoreBtn.textContent = 'See More';
      } else {
        seeMoreContainer.classList.add('expanded');
        seeMoreBtn.textContent = 'See Less';
      }
    });
  }
});

// GO BACK
let goBackButton = document.getElementById('goBack');
if(goBackButton) {
  goBackButton.addEventListener('click', function () {
  if (document.referrer) {
    window.history.back();
  } else {
    window.location.href = '/fallback-url';
  } 
  })
}
