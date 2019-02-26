function startAgeIn(name) {
    var select = "<select class='form-control' name='" + name + "StartAge[]'>";
    for(var i=0; i < 100; i++) {
        var iStr = i.toString();
        select += "<option value='" + iStr + "'>" + iStr + "</option>";
    }
    select += "</select>";
    return select;
}

function endAgeIn(name) {
    var select = "<select class='form-control' name='" + name + "EndAge[]'>";
    for(var i=0; i < 100; i++) {
        var iStr = i.toString();
        select += "<option value='" + iStr + "'>" + iStr + "</option>";
    }
    select += "</select>";
    return select;
}

function genderIn(name) {
    var select = "<select class='form-control' name='" + name + "Gender[]'>";
    select += "<option value='all'>All</option>";
    if(name === "FG") {
        select += "<option value='mixed'>Mixed Only</option>";
    }
    select += "<option value='female'>Female Only</option>";
    select += "<option value='male'>Male Only</option>";
    select += "</select>";
    return select;
}

function levelIn(name) {
    var select = "<select class='form-control' name='" + name + "Level[]'>";
    select += "<option value='All'>All Levels</option>";
    select += "<option value='Championship'>All Championship Levels</option>";
    select += "<option value='Open Championship'>Open Championship</option>";
    select += "<option value='Preliminary Championship'>Preliminary Championship</option>";
    select += "<option value='Grades'>Grades Levels</option>";
    select += "<option value='Non-Dancer'>Non-Dancer</option>";
    select += "</select>";
    return select;
}

function typeIn(name) {
    var select = "<select class='form-control' name='" + name + "Type[]'>";
    select += "<option value='8'>8-Hand</option>";
    select += "<option value='6'>6-Hand</option>";
    select += "<option value='4'>4-Hand</option>";
    select += "<option value='3'>3-Hand</option>";
    select += "<option value='2'>2-Hand</option>";
    select += "</select>";
    return select
}

function nameIn(name) {
    return "<input class='form-control' placeholder='Enter Name' type='text' name='" + name + "Name[]' />";
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
    var id_counter = 0;
    $('#judgeContainer').on('click', '.addSheet', function () {
        $(this).closest('.judge').children('table').children('tbody').append(
            '<tr><td>No</td>' +
            '<td><form method="POST" action="/welcome/tabulate/judges/marks">' +
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
    $('#addFG').click(function() {
        $('#FG .feis-box:last').after(
            '<div class="' + classes + '"><div class="form-group col-md-12 justify-content-center align-items-center">' +
            '<label class="pt-3" for="' + id_counter + '">Start Age: </label>' + startAgeIn(nameFG) +
            '<label class="pt-3" for="' + ++id_counter + '">End Age: </label>' + endAgeIn(nameFG) +
            '<label class="pt-3" for="' + ++id_counter + '">Genders: </label>' + genderIn(nameFG) +
            '<label class="pt-3" for="' + ++id_counter + '">Type: </label>' + typeIn(nameFG) +
            removeIn() + '</div></div>'
        );
    });

    $('#addTR').click(function() {
        $('#TR .feis-box:last').after(
            '<div class="' + classes + '"><div class="form-group col-md-12 justify-content-center align-items-center">' +
            '<label class="pt-3" for="' + id_counter + '">Level: </label>' + levelIn(nameTR) +
            '<label class="pt-3" for="' + ++id_counter + '">Start Age: </label>' + startAgeIn(nameTR) +
            '<label class="pt-3" for="' + ++id_counter + '">End Age: </label>' + endAgeIn(nameTR) +
            '<label class="pt-3" for="' + ++id_counter + '">Genders: </label>' + genderIn(nameTR) +
            removeIn() + '</div></div>'
        );
    });

    $('#addTNN').click(function() {
        $('#TNN .feis-box:last').after(
            '<div class="' + classes + '"><div class="form-group col-md-12 justify-content-center align-items-center">' +
            '<label class="pt-3" for="' + id_counter + '">Start Age: </label>' + startAgeIn(nameTNN) +
            '<label class="pt-3" for="' + id_counter+1 + '">End Age: </label>' + endAgeIn(nameTNN) +
            removeIn() + '</div></div>'
        );
    });

    $('#addAR').click(function() {
        $('#AR .feis-box:last').after(
            '<div class="' + classes + '"><div class="form-group col-md-12 justify-content-center align-items-center">' +
            '<label class="pt-3" for="' + id_counter + '">Name: </label>' + nameIn(nameAR) +
            '<label class="pt-3" for="' + ++id_counter + '">Start Age: </label>' + startAgeIn(nameAR) +
            '<label class="pt-3" for="' + ++id_counter + '">End Age: </label>' + endAgeIn(nameAR) +
            '<label class="pt-3" for="' + ++id_counter + '">Genders: </label>' + genderIn(nameAR) +
            removeIn() + '</div></div>'
        );
    });

    $('#addSP').click(function() {
        $('#SP tbody').append(
            '<tr><td>' + nameIn(nameSP) +
            '</td><td>' + levelIn(nameSP) +
            '</td><td>' + startAgeIn(nameSP) +
            '</td><td>' + endAgeIn(nameSP) +
            '</td><td>' + genderIn(nameSP) +
            '</td><td>' + removeIn() +
            '</td></tr>'
        );
    });

    $('tbody').on('click', '.del', function() {
        $(this).closest('tr').remove();
    });

    $('div').on('click','.del', function() {
        $(this).closest('.feis-box').remove();
    });
});