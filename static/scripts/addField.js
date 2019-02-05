function startAgeIn(name) {
    var select = "<select class='form-control' name='" + name + "StartAge[]'>";
    for(i=0; i < 100; i++) {
        iStr = i.toString();
        select += "<option value='" + iStr + "'>" + iStr + "</option>";
    }
    select += "</select>";
    return select;
}

function endAgeIn(name) {
    var select = "<select class='form-control' name='" + name + "EndAge[]'>";
    for(i=0; i < 100; i++) {
        iStr = i.toString();
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
    return select
}

function nameIn(name) {
    return "<input class='form-control' type='text' name='" + name + "Name[]' />";
}

function removeIn() {
    return "<button type='button' class='btn btn-danger py-2 del'>Remove</button>";
}

var nameFG = "FG";
var nameTR = "TR";
var nameTNN = "TNN";
var nameAR = "AR";
var nameSP = "SP";

$(document).ready(function() {
    $('#addFG').click(function() {
        $('#FG div:last').after('<div class="py-2">Start Age: ' + startAgeIn(nameFG) + '<br>End Age: ' + endAgeIn(nameFG) + '<br>Genders: ' + genderIn(nameFG) + '<br>Type: ' + typeIn(nameFG) + '<br>' + removeIn() + '</div>');
    });

    $('#addTR').click(function() {
        $('#TR div:last').after('<div class="py-2">Level: ' + levelIn(nameTR) + '<br>Start Age: ' + startAgeIn(nameTR) + '<br>End Age: ' + endAgeIn(nameTR) + '<br>Genders: ' + genderIn(nameTR) + '<br>' + removeIn() + '</div>');
    });

    $('#addTNN').click(function() {
        $('#TNN div:last').after('<div class="py-2">Start Age: ' + startAgeIn(nameTNN) + '<br>End Age: ' + endAgeIn(nameTNN) + '<br>' + removeIn() + '</div>');
    });

    $('#addAR').click(function() {
        $('#AR div:last').after('<div class="py-2">Name: ' + nameIn(nameAR) + '<br>Start Age: ' + startAgeIn(nameAR) + '<br>End Age: ' + endAgeIn(nameAR) + '<br>Genders: ' + genderIn(nameAR) + '<br>' + removeIn() + '</div>');
    });

    $('#addSP').click(function() {
        $('#SP div:last').after('<div class="py-2">Name: ' + nameIn(nameSP) + '<br>Level: ' + levelIn(nameSP) + '<br>Start Age: ' + startAgeIn(nameSP) + '<br>End Age: ' + endAgeIn(nameSP) + '<br>Genders: ' + genderIn(nameSP) + '<br>' + removeIn() + '</div>');
    });

    $('div').on('click','.del', function() {
        $(this).closest('div').remove();
    });
});