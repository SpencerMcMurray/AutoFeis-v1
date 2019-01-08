function startAgeIn(name) {
    var select = "<select name='" + name + "StartAge[]'>";
    for(i=0; i < 100; i++) {
        iStr = i.toString();
        select += "<option value='" + iStr + "'>" + iStr + "</option>";
    }
    select += "</select>";
    return select;
}

function endAgeIn(name) {
    var select = "<select name='" + name + "EndAge[]'>";
    for(i=0; i < 100; i++) {
        iStr = i.toString();
        select += "<option value='" + iStr + "'>" + iStr + "</option>";
    }
    select += "</select>";
    return select;
}

function genderIn(name) {
    var select = "<select name='" + name + "Gender[]'>";
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
    var select = "<select name='" + name + "Level[]'>";
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
    var select = "<select name='" + name + "Type[]'>";
    select += "<option value='8'>8-Hand</option>";
    select += "<option value='6'>6-Hand</option>";
    select += "<option value='4'>4-Hand</option>";
    select += "<option value='3'>3-Hand</option>";
    select += "<option value='2'>2-Hand</option>";
    return select
}

function nameIn(name) {
    return "<input type='text' name='" + name + "Name[]' />";
}

function removeIn() {
    return "<button class='del'>-</button>";
}

var nameFG = "FG";
var nameTR = "TR";
var nameTNN = "TNN";
var nameAR = "AR";
var nameSP = "SP";

$(document).ready(function() {
    $('#addFG').click(function() {
        console.log('hi');
        $('#FG tr:last').after('<tr><td>' + startAgeIn(nameFG) + '</td><td>' + endAgeIn(nameFG) + '</td><td>' + genderIn(nameFG) + '</td><td>' + typeIn(nameFG) + '</td><td>' + removeIn() + '</td></tr>');
    });

    $('#addTR').click(function() {
        $('#TR tr:last').after('<tr><td>' + levelIn(nameTR) + '</td><td>' + startAgeIn(nameTR) + '</td><td>' + endAgeIn(nameTR) + '</td><td>' + genderIn(nameTR) + '</td><td>' + removeIn() + '</td></tr>');
    });

    $('#addTNN').click(function() {
        $('#TNN tr:last').after('<tr><td>' + startAgeIn(nameTNN) + '</td><td>' + endAgeIn(nameTNN) + '</td><td>' + removeIn() + '</td></tr>');
    });

    $('#addAR').click(function() {
        $('#AR tr:last').after('<tr><td>' + nameIn(nameAR) + '</td><td>' + startAgeIn(nameAR) + '</td><td>' + endAgeIn(nameAR) + '</td><td>' + genderIn(nameAR) + '</td><td>' + removeIn() + '</td></tr>');
    });

    $('#addSP').click(function() {
        $('#SP tr:last').after('<tr><td>' + nameIn(nameSP) + '</td><td>' + levelIn(nameSP) + '</td><td>' + startAgeIn(nameSP) + '</td><td>' + endAgeIn(nameSP) + '</td><td>' + genderIn(nameSP) + '</td><td>' + removeIn() + '</td></tr>');
    });

    $('table').on('click','.del', function() {
        $(this).closest('tr').remove();
    });
});