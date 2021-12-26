
// Remove schema selected for deletion
document.addEventListener('click', event => {
    const element = event.target;
    if (element.className === 'btn btn-outline-danger btn-sm py-0 my-0') {
        const schema = element.parentElement.parentElement;
        const schema_name = schema.querySelector('td:nth-child(2)').innerText;
        condition = confirm(`WARNING: You are going to delete schema ${schema_name}\nand all related datasets.\n\nPress 'OK' to continue.`);
        if (condition) {
            const schema_id = schema.getAttribute('id').slice(6);
            //  send get request to server      
            fetch(`/delete_schema/${schema_id}`, { method: 'DELETE' })
            .then(response => {
                if (response.status === 204) {
                    console.log("success");
                    // Remove schema row in window view
                    schema.remove();
                } else {
                    response.json()
                    .then(result => {
                    console.log(result);
                    });
                }
            })
            .catch(error => console.log(error));
        };
    };    
});

