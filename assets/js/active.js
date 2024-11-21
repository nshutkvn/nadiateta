
//  --------------------------PAUSE-PLAY COUBS----------------------------------
const videos = document.querySelectorAll('video');

for (const video of videos) {
  video.addEventListener('click', function () {
    console.log('clicked');
    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  });
}
//-------------------------------- PAUSE-PLAY COUBS- -----------------------------


// ----------------------------- POST SLIDING -----------------------------------

let currentSlideIndex = 0;
const slides = document.querySelectorAll('.slide');
const indicators = document.querySelectorAll('.indicator');
const prevBtn = document.querySelector('.slide-nav.prev');
const nextBtn = document.querySelector('.slide-nav.next');

function showSlide(index) {
  if (index >= slides.length) {
    currentSlideIndex = 0;
  } else if (index < 0) {
    currentSlideIndex = slides.length - 1;
  }

  slides.forEach((slide, i) => {
    slide.classList.remove('active');
  });

  slides[currentSlideIndex].classList.add('active');

  indicators.forEach(indicator => indicator.classList.remove('active'));
  indicators[currentSlideIndex].classList.add('active');
}

function changeSlide(n) {
  currentSlideIndex += n;
  showSlide(currentSlideIndex);
}

// Swipe handling (for desktop)
// ... (similar to the previous code)

indicators.forEach((indicator, index) => {
  indicator.addEventListener('click', () => {
    showSlide(index);
  });
});

prevBtn.addEventListener('click', () => {
  changeSlide(-1);
});

nextBtn.addEventListener('click', () => {
  changeSlide(1);
});

// Initial display
showSlide(currentSlideIndex);

// ----------------------------- POST SLIDIND END -------------------

// ***********************************like*******************************//
//love btn
let love_icons = document.querySelectorAll(".like");
love_icons.forEach(function(icon){
  icon.addEventListener("click",function(){
      let not_loved = icon.children[0];
      let loved = icon.children[1];
      icon.classList.toggle("love");
      not_loved.classList.toggle("hide_img");
      loved.classList.toggle("display");
  })
});

// ***********************************like*******************************//
// ***********************************save*******************************//
//save btn
let save_icon = document.querySelectorAll(".save");
save_icon.forEach(function(save){
  save.addEventListener("click",function(){
    let not_save = save.children[1];
    let saved = save.children[0];
    not_save.classList.toggle("hide");
    saved.classList.toggle("hide");

})
})
// ***********************************save*******************************//
// ***********************************theme******************************//
const themeDots = document.querySelectorAll('.theme-dots .dot');
const body = document.body;

themeDots.forEach(dot => {
    dot.addEventListener('click', () => {
        const theme = dot.dataset.theme;

        // Remove all existing theme classes from the body
        body.classList.remove('default-theme', 'purple-theme', 'dark-theme'); 

        // Add the selected theme class
        body.classList.add(theme);

        localStorage.setItem('theme', theme);
    });
});

// Load saved theme (corrected to use classList)
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    body.classList.remove('default-theme', 'purple-theme', 'dark-theme');
    body.classList.add(savedTheme);
}

// ***********************************theme*******************************//
