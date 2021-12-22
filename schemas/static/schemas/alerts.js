
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('#message')) {
        element = document.querySelector('#message');
        setTimeout(() => { fadeOut(element) }, 4000);
        
        document.addEventListener('click', event => {
            const elt = event.target;
            if (elt.className === 'btn-close') {
                fadeOut(element); 
            }
        });
        
        function fadeOut(element) {
            element.style.animationPlayState = 'running';
            element.addEventListener('animationend', () => {
                element.remove();
            });
        };              
    }
})
