
document.addEventListener('DOMContentLoaded', () => {
    element = document.querySelector('#message');
    setTimeout(() => { fadeOut(element) }, 4000);
    if (element) {
        document.addEventListener('click', event => {
            const elt = event.target;
            if (elt.className === 'btn-close') {
                fadeOut(element); 
            }
        });
    }   
    function fadeOut(element) {
        element.style.animationPlayState = 'running';
        element.addEventListener('animationend', () => {
            element.remove();
        });
    };              
})
