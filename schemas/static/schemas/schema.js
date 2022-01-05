
document.addEventListener('DOMContentLoaded', function () {

    // clean type field after reload on relevant page   
    document.querySelector('#id_data_type').value = "";
    // add first column on relevant page
    addColumn();
    // add further columns upon pless 'Add column' button 
    document.querySelector('#add-column').onclick = function() {
        addColumn();
    };
});

let counter = 0;

// Add new blank column to column container
function addColumn() {
    
    // get column form
    const newcol = document.querySelector('#blank-column-form').innerHTML;

    // wrap column form into div with mx-2
    const element = document.createElement('div');
    element.className = 'mx-3';
    element.innerHTML = newcol;

    // amend "id" and "name" properties for each input element
    counter++;
   
    const col = element.querySelector('#id_column_name');
    col.id = `id${counter}_column_name`;
    col.name = `column_name_${counter}`;

    const type = element.querySelector('#id_data_type');
    type.id = `id${counter}_data_type`;
    type.name = `data_type_${counter}`;

    const from = element.querySelector('#id_range_from');
    from.id = `id${counter}_range_from`;
    from.name = `range_from_${counter}`;
    from.parentElement.style.visibility = 'hidden';
    from.setAttribute('min', 0);    

    const to = element.querySelector('#id_range_to');
    to.id = `id${counter}_range_to`;
    to.name = `range_to_${counter}`;
    to.parentElement.style.visibility = 'hidden';
    to.setAttribute('min', 0);

    const order = element.querySelector('#id_order_num');
    order.id = `id${counter}_order_num`;
    order.name = `order_num_${counter}`;
    order.setAttribute('min', 0);

    // add class 'col-delete' attributes to delete element
    const del_col = element.querySelector('button');
    del_col.setAttribute('class', `col-delete col-del btn btn-outline-danger btn-sm`);

    // place new element to DOM
    document.querySelector('#col-container').append(element);
}

// Remove column selected for deletion
document.addEventListener('click', event => {
    const element = event.target;
    if (element.className === 'col-delete col-del btn btn-outline-danger btn-sm') {
        element.parentElement.parentElement.remove();
    }    
});

// Visiolise range columns when 'integer' or 'text' type is selected
document.addEventListener('change', event => {
    const element = event.target;
    if (element.className === 'form-select mb-3') {
        // reach range elements of relevant column through grandparent element 'row'
        const range_els = element.parentElement.parentElement.querySelectorAll('.range');
        range_els.forEach(range=> {
            // if 'integer' or 'text' option is selected, change visibility
            if (element.value === '8' || element.value === '7') {
                range.style.visibility = 'visible';
            } else {
                range.style.visibility = 'hidden';
            }
        });
    };   
});
