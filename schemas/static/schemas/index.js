
// Remove schema selected for deletion
document.addEventListener('click', event => {
    const element = event.target;
    if (element.className === 'del-link text-danger ms-3') {
        const schema = element.parentElement.parentElement;
        const schema_id = schema.getAttribute('id').slice(6);
        //  send get request to server      
        fetch(`/delete_schema/${schema_id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(result => {
            console.log(result);
            // Remove schema row in window view
            schema.remove();
        })
        .catch(error => console.log(error));
    };    
});

