document.addEventListener('DOMContentLoaded', function () {

    document.querySelector('#id_data_type').value = "";
    addColomn();
    document.querySelector('#add-colomn').onclick = function() {
        addColomn();
        };
  
    // document.querySelectorAll('.col-delete').forEach(link => {
    //     link.onclick = function() {
    //         deleteColomn(this.dataset.col);
    //     }
    // });
});

let counter = 0;

// ================================================================
// Add new blank colomn to colomn container
function addColomn() {
    
    // get colomn form
    const newcol = document.querySelector('#blank-colomn-form').innerHTML;

    // wrap colomn form into div with mx-2
    const element = document.createElement('div');
    element.className = 'mx-2';
    element.innerHTML = newcol;

    // amend "id" and "name" properties for each input element
    counter++;
   
    const col = element.querySelector('#id_colomn_name');
    col.id = `id${counter}_colomn_name`;
    col.name = `colomn_name_${counter}`;

    const type = element.querySelector('#id_data_type');
    type.id = `id${counter}_data_type`;
    type.name = `data_type_${counter}`;

    const from = element.querySelector('#id_range_from');
    from.id = `id${counter}_range_from`;
    from.name = `range_from_${counter}`;
    from.parentElement.style.visibility = 'hidden';    

    const to = element.querySelector('#id_range_to');
    to.id = `id${counter}_range_to`;
    to.name = `range_to_${counter}`;
    to.parentElement.style.visibility = 'hidden';

    const order = element.querySelector('#id_order_num');
    order.id = `id${counter}_order_num`;
    order.name = `order_num_${counter}`;

    // add class 'col-delete' attributes to delete element
    const del_col = element.querySelector('p');
    del_col.setAttribute('class', `col-delete text-danger`);

    // place new element to DOM
    document.querySelector('#col-container').append(element);
}

// Remove colomn selected for deletion
document.addEventListener('click', event => {
    const element = event.target;
    if (element.className === 'col-delete text-danger') {
        element.parentElement.parentElement.remove();
    }    
});

// Visiolise range colomns when 'integer' or 'text' type is selected
document.addEventListener('change', event => {
    const element = event.target;
    if (element.className === 'form-select mb-3') {
        // reach range elements of relevant colomn through grandparent element 'row'
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
