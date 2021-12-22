document.addEventListener('DOMContentLoaded', function () {
    
    document.querySelectorAll('.type-class').forEach((element) => {
        update_schema_type_form(element);
    });
});

// update_schema_type_forms
function update_schema_type_form(element) {
    
    // get schematype object id
    const type_id = element.getAttribute('id').slice(8);
    console.log(type_id);

    // amend "id" and "name" properties for each input element
    const col = element.querySelector('#id_column_name');
    col.id = `id${type_id}_column_name`;
    col.name = `column_name_${type_id}`;

    const type = element.querySelector('#id_data_type');
    type.id = `id${type_id}_data_type`;
    type.name = `data_type_${type_id}`;
    visibility_switch(type);

    const from = element.querySelector('#id_range_from');
    from.id = `id${type_id}_range_from`;
    from.name = `range_from_${type_id}`;
    from.setAttribute('min', 0);     
    
    const to = element.querySelector('#id_range_to');
    to.id = `id${type_id}_range_to`;
    to.name = `range_to_${type_id}`;
    to.setAttribute('min', 0);

    const order = element.querySelector('#id_order_num');
    order.id = `id${type_id}_order_num`;
    order.name = `order_num_${type_id}`;
    order.setAttribute('min', 0);

    // update class 'col-delete' attributes to delete element
    const del_col = element.querySelector('button');
    del_col.setAttribute('class', `col-delete col-del btn btn-outline-danger btn-sm`);
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
        visibility_switch(element);
    };   
});

function visibility_switch(element) {
    // reach range elements of the column through grandparent element 'row'
    const range_els = element.parentElement.parentElement.querySelectorAll('.range');
    range_els.forEach(range=> {
        // if 'integer' or 'text' option is selected, change visibility
        if (element.value === '8' || element.value === '7') {
            range.style.visibility = 'visible';
        } else {
            range.style.visibility = 'hidden';
        }
    });   
}
