// FUNCTIONS

// SEE MORE

document.addEventListener('DOMContentLoaded', function() {
  const seeMoreBtns = document.querySelectorAll('.see-more-btn');
  const seeMoreContainers = document.querySelectorAll('.see-more-container');
  const charLimit = 225;

  seeMoreContainers.forEach((container, index) => {
    const textDescription = container.querySelector('.text-description');
    const fullText = textDescription.innerHTML.trim();
    const truncatedText = fullText.slice(0, charLimit);

    const hasLineBreaks = fullText.includes('<br>');
    const isLongText = fullText.length > charLimit;

    if (isLongText || hasLineBreaks) {
      seeMoreBtns[index].classList.remove('d-none');

      seeMoreBtns[index].addEventListener('click', function() {
        if (container.classList.contains('expanded')) {
          container.classList.remove('expanded');
          textDescription.innerHTML = truncatedText + '...';
          this.textContent = 'Show More';
        } else {
          container.classList.add('expanded');
          textDescription.innerHTML = fullText;
          this.textContent = 'Show Less';
        }
      });
    }
  });
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
