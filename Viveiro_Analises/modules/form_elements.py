from gluon import SQLFORM, DIV, SELECT, OPTION, INPUT, SPAN, SCRIPT, STYLE



      
class IS_LIST_OF_REFERENCES(object):
    """Validador personalizado para lista de referências"""
    
    def __init__(self, tablename, error_message='Item inválido'):
        self.tablename = tablename
        self.error_message = error_message
        
    def __call__(self, value):
        if not value:
            return ([], None)
            
        if isinstance(value, str):
            try:
                # Converte string em lista de IDs
                value = [int(v.strip()) for v in value.split(',') if v.strip()]
            except (ValueError, TypeError):
                return (value, self.error_message)
                
        return (value, None)
        
        
def list_reference_widget(field, value, allow_duplicates=False, **attributes):
    """Widget personalizado que combina lista e select box"""
    if value is None:
        value = []
        
    # Converte value para lista de IDs única
    if isinstance(value, str):
        try:
            # Remove caracteres indesejados e divide por vírgula
            value = value.replace('[', '').replace(']', '').replace("'", '')
            # Converte para conjunto para remover duplicatas
            value = list(set([int(v.strip()) for v in value.split(',') if v.strip()]))
        except (ValueError, TypeError):
            value = []
            
    # Obtem db e tablename
    db = field._db
    tablename = field.requires.tablename
    
    # Em modo readonly, apenas mostra os valores
    if attributes.get('_readonly', False):
        items = []
        for item_id in value:
            try:
                row = db[tablename][item_id]
                if row:
                    items.append(field.represent(row))
            except:
                continue
        return DIV(', '.join(items), _class='readonly-list-reference')
    
    # Cria select box para modo de edição
    select = SELECT(
        OPTION('', _value=''),
        _class='form-control reference-select',
        _name=field.name + '_select',
        **attributes
    )
    
    # Adiciona opções
    query = db[tablename].id > 0
    rows = db(query).select()
    for row in rows:
        select.append(OPTION(
            field.represent(row), 
            _value=row.id
        ))
    
    # Lista de selecionados
    selected_list = DIV(_class='selected-items')
    
    # Campo hidden principal para armazenar valores
    hidden_main = INPUT(
        _type='hidden',
        _name=field.name,
        _value=','.join(str(v) for v in value) if value else '',
        _class='list-reference-values'
    )
    
    # Script atualizado para manter valores únicos
    script = SCRIPT("""
    jQuery(function($) {
        var field = $('#%(field_id)s');
        var select = field.find('.reference-select');
        var selected = field.find('.selected-items');
        var hiddenMain = field.find('.list-reference-values');
        var allowDuplicates = %(allow_duplicates)s;
        
        function getSelectedValues() {
            var values = [];
            selected.find('input[type="hidden"]').not('.list-reference-values').each(function() {
                values.push($(this).val());
            });
            return values;
        }
        
        function updateHiddenMain() {
            // Usa Set para garantir valores únicos
            var values = allowDuplicates ? getSelectedValues() : Array.from(new Set(getSelectedValues()));
            hiddenMain.val(values.join(','));
        }
        
        // Adiciona items iniciais
        var initialValues = hiddenMain.val().split(',').filter(Boolean);
        initialValues.forEach(function(val) {
            var option = select.find('option[value="' + val + '"]');
            if (option.length) {
                selected.append(
                    $('<div class="selected-item">').append(
                        option.text(),
                        $('<input type="hidden">').attr({
                            name: '%(field_name)s',
                            value: val
                        }),
                        $('<span class="remove-item">').text('×')
                    )
                );
            }
        });
        
        select.on('change', function() {
            var val = $(this).val();
            if (!val) return;
            
            if (!allowDuplicates && getSelectedValues().indexOf(val) !== -1) {
                $(this).val('');
                return;
            }
            
            selected.append(
                $('<div class="selected-item">').append(
                    $(this).find('option:selected').text(),
                    $('<input type="hidden">').attr({
                        name: '%(field_name)s',
                        value: val
                    }),
                    $('<span class="remove-item">').text('×')
                )
            );
            $(this).val('');
            updateHiddenMain();
        });
        
        selected.on('click', '.remove-item', function() {
            $(this).parent().remove();
            updateHiddenMain();
        });
    });
    """ % dict(
        field_id=field.name,
        field_name=field.name,
        allow_duplicates='true' if allow_duplicates else 'false'
    ))
    
    # Adiciona itens já selecionados
    for item_id in value:
        try:
            row = db[tablename][item_id]
            if row:
                selected_list.append(
                    DIV(
                        field.represent(row),
                        INPUT(_type='hidden', _name=field.name, _value=item_id),
                        SPAN('×', _class='remove-item'),
                        _class='selected-item'
                    )
                )
        except:
            continue

    return DIV(
        select,
        selected_list,
        hidden_main,
        script,
        _id=field.name,
        _class='list-reference-widget'
    )