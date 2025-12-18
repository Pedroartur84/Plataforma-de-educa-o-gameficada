from django import template
register = template.Library()

@register.filter
def conquistas_na_sala(titulo, sala):
    """
    Retorna o número de conquistas de um título em uma sala específica.
    
    Uso no template:
    {{ titulo|conquistas_na_sala:sala }}
    """
    try:
        return titulo.participacoes_com_titulo.filter(sala=sala).count()
    except (AttributeError, TypeError):
        # Caso o título não tenha o relacionamento ou ocorra outro erro
        return 0