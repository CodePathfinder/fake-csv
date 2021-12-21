
document.addEventListener('DOMContentLoaded', function () {

    // call status_check
    status_check();
});

let timerId = 0;

// check pending task data status every 3 seconds
function status_check() {
    timerId = setInterval(() => {
        getPendingDataStatus()
    }, 3000);
};

// request status of pending data
function getPendingDataStatus() {
    let counter = 0
    // console.log(`TIMER_ID: ${timerId}`)
    
    // loop for all link elements waiting for href attribute 
    document.querySelectorAll('.pending-url').forEach(element => {
        const href = element.getAttribute('href');
        if (href === '') {
            counter++
            // get monitor_task_key as link element id
            const id = element.getAttribute('id');
            // send get request to server
            fetch(`/status_check/${id}`)
            .then(response => response.json())
            .then(result => {
                // console.log(result);
                
                if (result['url']) {
                    // change elements properties
                    console.log(`csv file is saved under url: ${result['url']}`)
                    element.setAttribute('href', result['url']);
                    element.setAttribute('class', 'visible');
                    const bttn = element.parentElement.previousElementSibling.querySelector('button');
                    bttn.setAttribute('class', 'btn btn-success btn-sm');
                    bttn.innerText = 'Ready';
                }
            });
        }; 
    });
    if (counter === 0) {
        // change setInterval function
        clearInterval(timerId);
        // console.log('STOP SETINTERVAL');
    }
}
