// FUNCTIONS

// SEE MORE
document.addEventListener('DOMContentLoaded', () => {
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

      seeMoreBtns[index].addEventListener('click', () => {
        if (container.classList.contains('expanded')) {
          container.classList.remove('expanded');
          textDescription.innerHTML = truncatedText;
          seeMoreBtns[index].textContent = 'Show More';
        } else {
          container.classList.add('expanded');
          textDescription.innerHTML = fullText;
          seeMoreBtns[index].textContent = 'Show Less';
        }
      });
    }
  });
});

// GO BACK
let goBackButton = document.getElementById('goBack');
if(goBackButton) {
  goBackButton.addEventListener('click', () => {
  if (document.referrer) {
    window.history.back();
  } else {
    window.location.href = '/fallback-url';
  } 
  })
}

// SHOW POSTS OR TEXTS
const showPostsButton = document.getElementById('showPosts');
const postsContainer = document.getElementById('postsContainer');
const showTextsButton = document.getElementById('showTexts');
const textsContainer = document.getElementById('textsContainer');

function ShowOrHideContainers(button, secondButton, showContainer, hideContainer) {
  button.addEventListener('click', () => {
    button.classList.add('border-bottom-1', 'border-dark')
    secondButton.classList.remove('border-bottom-1', 'border-dark')
    showContainer.style.setProperty('display', 'block', 'important');
    hideContainer.style.setProperty('display', 'none', 'important');
  });
}

if (showPostsButton) {
  ShowOrHideContainers(showPostsButton, showTextsButton, postsContainer, textsContainer);
  ShowOrHideContainers(showTextsButton, showPostsButton, textsContainer, postsContainer);
}

// POST UPDATE
const postUpdateButton = document.getElementById('postUpdateButton');
const descriptionContainer = document.getElementById('descriptionContainer');
const formTemplate = document.getElementById('postUpdateForm');
const descriptionViewTemplate = document.getElementById('descriptionViewTemplate');

if (postUpdateButton) {
  postUpdateButton.addEventListener('click', () => {
    const formClone = document.importNode(formTemplate.content, true);
    descriptionContainer.innerHTML = '';
    descriptionContainer.appendChild(formClone);
  
    const cancelPostUpdateButton = descriptionContainer.querySelector('#cancelPostUpdateButton');
  
    cancelPostUpdateButton.addEventListener('click', (event) => {
      event.preventDefault();
  
      const descriptionClone = document.importNode(descriptionViewTemplate.content, true);
      descriptionContainer.innerHTML = '';
      descriptionContainer.appendChild(descriptionClone);
    });
  });
}
