// Our class will live in the yourlabs global namespace.
if (window.yourlabs == undefined) window.yourlabs = {};

if (window.yourlabs.FormUpdate != undefined) console.log('form_update.js already loaded');

window.yourlabs.FormUpdate = function(options) {
    this.form = [];
    this.modal = $('#field-configuration');
    this.modalForm = this.modal.find('.form');
    this.options = options;

    var formUpdate = this;

    this.init = function() {
        console.log('init');
        $('.nav-tabs li').each(function() {
            $(this).data('tab', {
                verbose_name: $(this).find('.name').html(),
                pk: $(this).data('pk'),
            });
        });
    };

    this.bind = function() {
        $('#new-tab').keypress(function(e) {
            if (e.which == 13) // enter
                $('#new-tab .save').click();
        });

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
    };

    this.currentTabContent = function() {
        return $('.tab-pane.active');
    };

    this.fieldFormUrl = function(path) {
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

        $.ajax(this.fieldUrl(path), {
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
        $.ajax(this.fieldUrl(this.modalForm.data('path')), {
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
