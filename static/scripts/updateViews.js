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
        $(domObj).parent().children('span').remove();
        // TODO: Mouse over these for brief explanation
        if(parseInt(data['valid']) === 1) {
            html = '<span class="mx-2 my-auto" title="Dancer registered"><i class="far fa-check-circle" style="color: green;"></i></span>';
        } else {
            html = '<span class="mx-2 my-auto" title="Dancer not registered"><i class="far fa-times-circle" style="color: red;"></i></span>';
        }
        $(domObj).parent().prepend(html)
    });
}