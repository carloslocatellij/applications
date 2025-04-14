from gluon import SQLFORM, DIV, SELECT, OPTION, INPUT, SPAN, SCRIPT, STYLE

def especie_represent(row):
    """Função para representar espécies"""
    if not row:
        return ''
    
    if isinstance(row, (int, str)):
        esp_repr = db(db.Especies.id == int(row)).select().first()
    else:
        esp_repr = row
        
    if not esp_repr:
        return ''
    
    if esp_repr.Especie:
        if len(esp_repr.Especie.split(' ')) > 1:
            nome_cientifico = f"{str(esp_repr.Especie[0])}. {str(esp_repr.Especie.split(' ')[1])}"
        else:
            nome_cientifico = f"{str(esp_repr.Especie[0])}. {str(esp_repr.Especie)}"
            
    else:
        nome_cientifico = ''
        
    nome = esp_repr.Nome.replace('-', ' ')
    return f"{nome} - {nome_cientifico}"  

      
class IS_LIST_OF_REFERENCES(object):
        """Validador personalizado para lista de referências"""
        
        def __init__(self, tablename, error_message='Item inválido'):
            self.tablename = tablename
            self.error_message = error_message
            
        def __call__(self, value):
            if not value:
                return ([], None)
                
            if isinstance(value, str):
                value = [v.strip() for v in value.split(',') if v.strip()]
                
            # O campo list:reference já faz a validação básica
            return (value, None)
        
        
def list_reference_widget(field, value, **attributes):
    """Widget personalizado que combina lista e select box"""
    if value is None:
        value = []
        
    # Pega o db do próprio field
    db = field._db
    
    # Obtém a tabela referenciada
    tablename = 'Especies'
    
    # Cria o select box
    select = SELECT(
        OPTION('', _value=''),
        _class='form-control reference-select',
        _name=field.name + '_select',
        **attributes
    )
    
    # Adiciona as opções do select
    query = db[tablename].id > 0
    rows = db(query).select()
    for row in rows:
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
            row = db[tablename][item_id]
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

    return DIV(select, selected_list, script, _id=field.name, _class='list-reference-widget')