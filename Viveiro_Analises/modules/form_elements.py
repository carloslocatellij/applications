from gluon import current, SQLFORM, DIV, SELECT, OPTION, INPUT, SPAN, SCRIPT, STYLE


class IS_LIST_OF_REFERENCES:
    """Validador personalizado para lista de referências"""
    
    def __init__(self, db, tablename, fields, error_message='Item inválido'):
        self.db = db
        self.tablename = tablename
        self.fields = fields
        self.error_message = error_message
        
    def __call__(self, value):
        if not value:
            return ([], None)
            
        if isinstance(value, str):
            value = [v.strip() for v in value.split(',') if v.strip()]
            
        errors = []
        validated_ids = []
        
        for item in value:
            if str(item).isdigit():
                # Verifica se o ID existe na tabela
                if self.db(self.db[self.tablename].id == item).count():
                    validated_ids.append(int(item))
                else:
                    errors.append(self.error_message)
                    
        if errors:
            return (value, errors)
        return (validated_ids, None)
    
def list_reference_widget(field, value, **attributes):
    """Widget personalizado que combina lista e select box"""
    
    # Obtém a tabela referenciada
    db = current.db
    tablename = field.type.split(':')[1]
    
    # Cria o select box
    select = SELECT(
        OPTION('', _value=''),
        _class='form-control reference-select',
        _name=field.name + '_select'
    )
    
    # Adiciona as opções do select
    for row in db(db[tablename]).select():
        select.append(OPTION(
            especie_represent(row), 
            _value=row.id
        ))
    
    # Cria a lista de itens selecionados
    selected_list = DIV(_class='selected-items')
    if value:
        if isinstance(value, str):
            value = [v.strip() for v in value.split(',') if v.strip()]
        for item_id in value:
            row = db(db[tablename].id == item_id).select().first()
            if row:
                selected_list.append(
                    DIV(
                        especie_represent(row),
                        INPUT(_type='hidden', _name=field.name, _value=item_id),
                        SPAN('×', _class='remove-item'),
                        _class='selected-item'
                    )
                )
    
    # Script para manipular a interação
    script = SCRIPT("""
    jQuery(function($) {
        var field = $('#%(field_id)s');
        var select = field.find('.reference-select');
        var selected = field.find('.selected-items');
        
        select.on('change', function() {
            var val = $(this).val();
            var text = $(this).find('option:selected').text();
            if (val) {
                selected.append(
                    $('<div class="selected-item">').append(
                        text,
                        $('<input type="hidden">').attr({
                            name: '%(field_name)s',
                            value: val
                        }),
                        $('<span class="remove-item">').text('×')
                    )
                );
                $(this).val('');
            }
        });
        
        selected.on('click', '.remove-item', function() {
            $(this).parent().remove();
        });
    });
    """ % dict(field_id=field.name, field_name=field.name))
    
    # Estilo para os elementos
    style = STYLE("""
    .selected-items { margin-top: 10px; }
    .selected-item {
        display: inline-block;
        margin: 2px;
        padding: 2px 5px;
        background: #f0f0f0;
        border: 1px solid #ccc;
        border-radius: 3px;
    }
    .remove-item {
        margin-left: 5px;
        color: #999;
        cursor: pointer;
    }
    .remove-item:hover { color: #f00; }
    """)
    
    return DIV(select, selected_list, script, style, _id=field.name)