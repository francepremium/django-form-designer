// Our class will live in the yourlabs global namespace.
if (window.yourlabs == undefined) window.yourlabs = {};

if (window.yourlabs.FormUpdate != undefined) console.log('form_update.js already loaded');

// Make jquery behave according to standards, which are compatible
// with django, else it would use PHP's implementration
$.ajaxSettings.traditional = true;

window.yourlabs.FormUpdate = function(options) {
    this.form = [];
    this.modal = $('#field-configuration');
    this.modalForm = this.modal.find('.form');
    this.options = options;

    var formUpdate = this;

    this.init = function() {
        $('.nav-tabs li').each(function() {
            $(this).data('tab', {
                verbose_name: $(this).find('.name').html(),
                pk: $(this).data('pk'),
            });
        });
        
        $('.nav-tabs li:first a').click();
    };

    this.bind = function() {
        $(document).keyup(function(e) {
            if (e.which == 27) { // esc
                $('.modal .close').click();
            }
        });

        $('.modal').keypress(function(e) {
            if (e.which == 13) // enter
                $(this).find('.save').click();
        });

        $('.modal .cancel').click(function() {
            $(this).parents('.modal').find('.close').click();
        });

        // {{{ widgets
        $('.field .add').click(function(e) {
            var url = formUpdate.options.widgetCreateUrl;
            url += '?';
            url += $.param({
                widget_class: $(this).parents('.field').data('widget-class'),
                tab_id: $('.nav-tabs .active').data('tab').pk,
            });
            
            $('#field-configuration').data('action', url);

            $.ajax(url, {
                type: 'get',
                async: false,
                dataType: 'html',
                success: function(data, textStatus, jqXHR) {
                    $('#field-configuration form').html(data);
                    $('#field-configuration').modal('show');
                },
            });
        });

        $('#field-configuration .save').click(function() {
            $.ajax($('#field-configuration').data('action'), {
                type: 'post',
                data: $('#field-configuration form').serialize(),
                success: function(data, textStatus, jqXHR) {
                    if (jqXHR.status == 201) {
                        $('#field-configuration').modal('hide');
                    } else {
                        $('#field-configuration form').html(data);
                    }
                },
            });
        });
        // }}}

        // {{{ tabs
        $('.new-tab').click(function() {
            $('#new-tab').modal('show');
            $('#new-tab input[type=text]:first').focus();
        });

        $('#new-tab .save').click(function() {
            var verboseName = $('#new-tab input[name=verbose_name]').val();

            if (! $.trim(verboseName).length) {
                $('#new-tab .control-group').addClass('error');

                $('<span>', {
                    'class': 'help-inline',
                    html: gettext('Please type the tab title'),
                }).insertAfter('#new-tab input[name=verbose_name]');
                
                return;
            }

            $.ajax(formUpdate.options.tabCreateUrl, {
                async: false,
                type: 'post',
                data: {
                    verbose_name: verboseName,
                    form_pk: $('#form-pk').val(),
                },
                dataType: 'json',
                success: function(data, textStatus, jqXHR) {
                    var id = data.tab.pk;

                    $('<div>', {
                        id: 'tab-' + id,
                        'class': 'tab-pane',
                        html: $('<table>', {
                            'class': 'fieldset',
                        }),
                    }).insertAfter('.tab-content div:last');
        
                    var tab = $('<li>', {
                        html: $('<a>', {
                            href: '#tab-' + id,
                            'data-toggle': 'tab',
                            html: [
                                '<span class="handle ui-icon ui-icon-arrow-2-e-w"></span>',
                                '<span contenteditable="true" class="name">',
                                data.tab.verbose_name,
                                '</span>',
                                '<span class="ui-icon ui-icon-circle-close remove"></span>',
                            ].join(''),
                        })
                    });
                    tab.data('tab', data.tab);
                    tab.insertBefore($('li.new-tab'));

                    $('#new-tab').modal('hide');
                    $('#new-tab input[type=text]').val('');
                    $('#new-tab .help-inline').remove();
                    $('#new-tab .error').removeClass('error');

                    $('.nav-tabs li:not(.new-tab):last a').click();
                },
            });
        });

        $('.nav-tabs .remove').live('click', function() {
            var data = $(this).parents('li').data('tab');
            $('#delete-tab .tab-name').html(data.verbose_name);
            $('#delete-tab').data('tab-pk', data.pk);
            $('#delete-tab').modal('show');
        });

        $('#delete-tab .save').bind('click', function() {
            var data = $('a[href=#tab-'+$('#delete-tab').data('tab-pk')+']').parents('li'
                ).data('tab');

            $.ajax(formUpdate.options.tabDeleteUrl, {
                async: false,
                type: 'post',
                data: data,
                success: function() {
                    $('div#tab-' + data.pk).remove();
                    $('a[href=#tab-' + data.pk + ']').remove();
                    $('#delete-tab').modal('hide');
                },
            });
        });

        $('.nav-tabs .name').live('focusout', function() {
            var data = $(this).parents('li').data('tab');
            $.post(formUpdate.options.tabUpdateUrl, {
                pk: data.pk,
                name: $(this).html(),
            });
        });

        $('.nav-tabs').sortable({
            axis: 'x',
            handle: '.handle',
            items: 'li:not(.new-tab)',
            stop: function(e, ui) {
                var pks=[];
                $('.nav-tabs li:not(.new-tab)').each(function() {
                    pks.push($(this).data('tab').pk);
                });
                $.post(formUpdate.options.formUpdateUrl, {tabs: pks});
            },
        });

        // }}}
    };

    this.currentTabContent = function() {
        return $('.tab-pane.active');
    };

    this.fieldFormUrl = function(widget_class) {
    }

    this.createFieldHtml = function(configuration) {
        $('<tr>', {
            'class': 'field',
            html: [
                $('<td>'),
            ].join(''),
        });
    };

    this.showFieldConfiguration = function(field) {
        var data = typeof(field) == 'string' ? {} : field.data('configuration');
        
        this.modalForm.data('field', field);

        $.ajax(this.fieldUrl(widget_class), {
            async: false,
            data: data,
            type: 'post',
            dataType: 'html',
            success: function(data, jqXHR, textStatus) {
                formUpdate.modalForm.html(data);
            },
        });
    };

    this.sendForm = function() {
        $.ajax(this.fieldUrl(this.modalForm.data('widget_class')), {
            async: false,
            data: formUpdate.modalForm.serialize(),
            type: 'post',
            dataType: 'json',
            success: function(data, jqXHR, textStatus) {
                if (data.is_valid) {
                    var html = this.createFieldHtml(data.field);
                    var table = formUpdate.currentTabContent().find('table');

                    if (typeof(formUpdate.modalForm.data('field')) == 'string') {
                        table.append(html);
                    } else {
                        var current = table.find('tr#field-' + data.field.pk)
                        current.html(html.html());
                    }
                } else {
                    formUpdate.modalForm.html(data);
                }
            },
        });
    }
}
