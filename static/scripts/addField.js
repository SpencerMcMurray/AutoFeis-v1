function startAgeIn(name, id_counter) {
    var select = "<select id='" + id_counter + "' class='form-control' name='" + name + "StartAge[]'>";
    for(var i=0; i < 100; i++) {
        var iStr = i.toString();
        select += "<option value='" + iStr + "'>" + iStr + "</option>";
    }
    select += "</select>";
    return select;
}

function endAgeIn(name, id_counter) {
    var select = "<select id='" + id_counter + "' class='form-control' name='" + name + "EndAge[]'>";
    for(var i=0; i < 100; i++) {
        var iStr = i.toString();
        select += "<option value='" + iStr + "'>" + iStr + "</option>";
    }
    select += "</select>";
    return select;
}

function genderIn(name, id_counter) {
    var select = "<select id='" + id_counter + "' class='form-control' name='" + name + "Gender[]'>";
    select += "<option value='all'>All</option>";
    if(name === "FG") {
        select += "<option value='mixed'>Mixed Only</option>";
    }
    select += "<option value='female'>Female Only</option>";
    select += "<option value='male'>Male Only</option>";
    select += "</select>";
    return select;
}

function levelIn(name, id_counter) {
    var select = "<select id='" + id_counter + "' class='form-control' name='" + name + "Level[]'>";
    select += "<option value='All'>All Levels</option>";
    select += "<option value='Championship'>All Championship Levels</option>";
    select += "<option value='Open Championship'>Open Championship</option>";
    select += "<option value='Preliminary Championship'>Preliminary Championship</option>";
    select += "<option value='Grades'>Grades Levels</option>";
    select += "<option value='Non-Dancer'>Non-Dancer</option>";
    select += "</select>";
    return select;
}

function typeIn(name, id_counter) {
    var select = "<select id='" + id_counter + "' class='form-control' name='" + name + "Type[]'>";
    select += "<option value='8'>8-Hand</option>";
    select += "<option value='6'>6-Hand</option>";
    select += "<option value='4'>4-Hand</option>";
    select += "<option value='3'>3-Hand</option>";
    select += "<option value='2'>2-Hand</option>";
    select += "</select>";
    return select
}

function nameIn(name, id_counter) {
    return "<input id='" + id_counter + "' class='form-control' placeholder='Enter Name' type='text' name='" + name + "Name[]' />";
}

function removeIn() {
    return "<div class='pt-3 form-group d-flex justify-content-center'><button type='button' class='btn btn-danger mt-2 del'>Remove</button></div>";
}

function removeBtn() {
    return "<button type='button' class='btn btn-danger mt-2 del'>Remove</button>";
}

var nameFG = "FG";
var nameTR = "TR";
var nameTNN = "TNN";
var nameAR = "AR";
var nameSP = "SP";
var classes = "d-flex sub-box mx-auto feis-box rounded bd-highlight p-2 align-items-center";

$(document).ready(function() {
    // Dynamic tabulation logic
    $('#delCol').click( function () {
        if ($('tbody tr:last').children('td').length > 3) {
            $('.delBtn').prev().remove();
        }
    });
    $('#addCol').click( function () {
        var delBtn = $('.delBtn');
        var clone = delBtn.prev().clone();
        delBtn.before(clone);
    });
    $('#addRow').click( function () {
        var body = $('tbody');
        var numRows = body.children('tr').length;
        if (numRows === 0) {
            body.append(
                '<tr>' +
                '<td><div class="form-group mb-0">' +
                '<input name="entries[' + numRows + '][]" class="form-control" type="text" placeholder="Dancer">' +
                '</div></td>' +
                '<td><div class="form-group mb-0">' +
                '<input name="entries[' + numRows + '][]" class="form-control" type="text" placeholder="Mark">' +
                '</div></td>' +
                '<td class="delBtn"><button type="button" class="btn btn-danger del">Delete</button></td>' +
                '</tr>'
            );
        } else {
            var newRow = body.children('tr:last').clone();
            newRow.find(':text').val('');
            body.append(newRow);
        }
        // Update name arrays
        body.children('tr').each( function (idx) {
            $(this).children('td').children('div').children('input').attr('name', 'entries[' + idx + '][]')
        });
    });
    // Dynamic preparation for tabulation logic
    $('#judgeContainer').on('click', '.addSheet', function () {
        var judgeId = $(this).closest('.judge').children('.judgeId').text();
        $(this).closest('.judge').children('table').children('tbody').append(
            '<tr><td>No</td>' +
            '<td><form method="POST" action="/welcome/tabulate/judges/marks">' +
            '<input type="hidden" name="judgeId" value="' + judgeId + '">' +
            '<button type="submit" class="btn btn-info mt-2">Enter</button>' +
            '</form></td>' +
            '<td>' + removeBtn() +
            '</td></tr>'
        );
    });
    $('#addJudge').click(function () {
        $('#table tbody').append(
            '<tr>' +
            '<td class="form-group text-left">' +
            '<input required name="Judge[]" type="text" class="form-control" placeholder="Enter Name">' +
            '</td>' +
            '<td>' + removeBtn() +
            '</td></tr>'
        );
    });
    // Dynamic competition logic
    var id_counter = 0;
    $('#addFG').click(function() {
        $('#FG .feis-box:last').after(
            '<div class="' + classes + '"><div class="form-group col-md-12 justify-content-center align-items-center">' +
            '<label class="pt-3" for="' + id_counter + '">Start Age: </label>' + startAgeIn(nameFG, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">End Age: </label>' + endAgeIn(nameFG, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">Genders: </label>' + genderIn(nameFG, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">Type: </label>' + typeIn(nameFG, id_counter) +
            removeIn() + '</div></div>'
        );
        ++id_counter;
    });

    $('#addTR').click(function() {
        $('#TR .feis-box:last').after(
            '<div class="' + classes + '"><div class="form-group col-md-12 justify-content-center align-items-center">' +
            '<label class="pt-3" for="' + id_counter + '">Level: </label>' + levelIn(nameTR, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">Start Age: </label>' + startAgeIn(nameTR, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">End Age: </label>' + endAgeIn(nameTR, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">Genders: </label>' + genderIn(nameTR, id_counter) +
            removeIn() + '</div></div>'
        );
        ++id_counter;
    });

    $('#addTNN').click(function() {
        $('#TNN .feis-box:last').after(
            '<div class="' + classes + '"><div class="form-group col-md-12 justify-content-center align-items-center">' +
            '<label class="pt-3" for="' + id_counter + '">Start Age: </label>' + startAgeIn(nameTNN, id_counter) +
            '<label class="pt-3" for="' + id_counter+1 + '">End Age: </label>' + endAgeIn(nameTNN, id_counter) +
            removeIn() + '</div></div>'
        );
        ++id_counter;
    });

    $('#addAR').click(function() {
        $('#AR .feis-box:last').after(
            '<div class="' + classes + '"><div class="form-group col-md-12 justify-content-center align-items-center">' +
            '<label class="pt-3" for="' + id_counter + '">Name: </label>' + nameIn(nameAR, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">Start Age: </label>' + startAgeIn(nameAR, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">End Age: </label>' + endAgeIn(nameAR, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">Genders: </label>' + genderIn(nameAR, id_counter) +
            removeIn() + '</div></div>'
        );
        ++id_counter;
    });

    $('#addSP').click(function() {
        $('#SP .feis-box:last').after(
            '<div class="' + classes + '"><div class="form-group col-md-12 justify-content-center align-items-center">' +
            '<label class="pt-3" for="' + id_counter + '">Name: </label>' + nameIn(nameSP, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">Level: </label>' + levelIn(nameSP, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">Start Age: </label>' + startAgeIn(nameSP, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">End Age: </label>' + endAgeIn(nameSP, id_counter) +
            '<label class="pt-3" for="' + ++id_counter + '">Genders: </label>' + genderIn(nameSP, id_counter) +
            removeIn() + '</div></div>'
        );
        ++id_counter;
    });

    $('tbody').on('click', '.del', function() {
        $(this).closest('tr').remove();
    });

    $('div').on('click','.del', function() {
        $(this).closest('.feis-box').remove();
    });
});