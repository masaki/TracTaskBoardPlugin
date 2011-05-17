// -*- coding: utf-8 -*-

$(function() {
    $('.taskboard_lane').equalHeights();

    $('.taskboard_tickets').sortable({
        dropOnEmpty: true,
        connectWith: ['.taskboard_tickets'],
        placeholder: 'ticket_placeholder',
        forcePlaceholderSize: true
    }).disableSelection();

    $('.taskboard_tickets').bind('sortover', function(event, ui) {
        // resize lane
        var max = 0;
        $('.taskboard_tickets').each(function() {
            var size = $(this).children('li').size();
            if (size > max) max = size;
        });

        var height = max * ($('li.taskboard_ticket').first().height() + 10);
        $('.taskboard_lane').height(height + 50);
        $('.taskboard_tickets').height(height);
    });

    $('.taskboard_tickets').bind('sortreceive', function(event, ui) {
        elem = $(event.target);
        $.post(elem.find('a.taskboard_api').attr('href'), {
            id: /taskboard_ticket_(\d+)/.exec(ui.item.attr("id"))[1],
            status: elem.prev().text()
        });
    });

    $('li.taskboard_ticket h3').click(function(ev) {
        $(ev.target).parent().find('table').toggle();
    });
});