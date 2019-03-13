/**
 * Used in enterMarks, used to validate if a competitor is registered for this competition
 */
function applyValidation(domObj, comp, url) {
    var data = {};
    data['num'] = parseFloat($(domObj).val());
    data['comp'] = comp;
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify(data),
        dataType: 'json'
    }).done(function (data) {
        var html;
        console.log($(domObj).parent().html());
        $(domObj).parent().children('i').remove();
        // TODO: Mouse over these for brief explanation
        if(parseInt(data['valid']) === 1) {
            html = '<i class="far fa-check-circle mx-2 my-auto" style="color: green;"></i>';
        } else {
            html = '<i class="far fa-times-circle mx-2 my-auto" style="color: red;"></i>';
        }
        $(domObj).parent().prepend(html)
    });
}