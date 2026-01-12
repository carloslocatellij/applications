<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# enviar email com python

Para **enviar e-mail com Python**, o método mais comum é utilizar a biblioteca padrão `smtplib`, que permite enviar mensagens via protocolo SMTP. Você pode também utilizar a biblioteca `email` para construir mensagens mais elaboradas, incluindo suporte a HTML e anexos[^1_1][^1_2][^1_4][^1_5][^1_7].

## Exemplo básico de envio de e-mail com Gmail

```python
import smtplib
from email.mime.text import MIMEText

# Dados do e-mail
assunto = "Assunto do Email"
corpo = "Este é o corpo da mensagem"
remetente = "seu_email@gmail.com"
destinatarios = ["destinatario1@gmail.com", "destinatario2@gmail.com"]
senha = "sua_senha_de_app"  # Use uma senha de app do Google, não sua senha normal

def enviar_email(assunto, corpo, remetente, destinatarios, senha):
    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = remetente
    msg['To'] = ', '.join(destinatarios)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
        servidor.login(remetente, senha)
        servidor.sendmail(remetente, destinatarios, msg.as_string())
    print("Mensagem enviada!")

enviar_email(assunto, corpo, remetente, destinatarios, senha)
```

**Atenção:**

- Se você usa Gmail, é necessário gerar uma “senha de app” nas configurações de segurança da sua conta Google, especialmente se você utiliza autenticação em dois fatores. Não utilize sua senha normal do Gmail[^1_2][^1_5].
- Para outros provedores, altere o servidor SMTP e a porta conforme as instruções do serviço de e-mail.


## Envio com Outlook (Windows)

Se você usa o Outlook instalado no Windows, pode automatizar o envio sem SMTP usando a biblioteca `pywin32`:

```python
import win32com.client as win32

outlook = win32.Dispatch('outlook.application')
email = outlook.CreateItem(0)
email.To = 'destinatario@exemplo.com'
email.Subject = 'Assunto do E-mail'
email.HTMLBody = '<p>Corpo do e-mail em HTML</p>'
email.Send()
print("Email enviado")
```

Esse método dispensa configurações de servidor, mas exige que o Outlook esteja instalado e configurado[^1_6].

## Dicas e boas práticas

- Para enviar anexos, utilize a classe `MIMEBase` junto com `MIMEMultipart` do módulo `email`.
- Sempre proteja suas credenciais e nunca compartilhe senhas em código público.
- Para grandes volumes de e-mail, considere serviços especializados ou APIs.

Esses exemplos cobrem os principais cenários para envio de e-mail com Python, tanto para Gmail quanto para Outlook[^1_2][^1_4][^1_5][^1_6].

<div style="text-align: center">⁂</div>

[^1_1]: https://pythonacademy.com.br/blog/como-enviar-email-utilizando-python
[^1_2]: https://mailtrap.io/pt/blog/python-send-email-gmail/
[^1_3]: https://www.youtube.com/watch?v=LUyM7Nm1i9k
[^1_4]: https://hub.asimov.academy/tutorial/como-enviar-emails-com-python-um-guia-para-iniciantes/
[^1_5]: https://www.treinaweb.com.br/blog/enviando-email-com-python-e-smtp
[^1_6]: https://www.hashtagtreinamentos.com/envio-de-e-mail-com-python
[^1_7]: https://mailtrap.io/pt/blog/python-send-email/
[^1_8]: https://www.youtube.com/shorts/YkElv7ElFVA
[^1_9]: https://www.youtube.com/watch?v=N97q96BygUg

---

# Módulo de Envio de E-mail para Web2py com Fila de Gerenciamento

## Visão Geral do Sistema

Para construir um módulo completo de envio de e-mail para uma aplicação Web2py com sistema de fila e gerenciamento, você precisará implementar **quatro componentes principais**: configuração do e-mail, criação da fila no banco de dados, processamento da fila e interface de gerenciamento.

## 1. Configuração do Sistema de E-mail

### Configuração no arquivo `models/db.py`

```python
from gluon.tools import Mail

# Configuração do mailer
mail = Mail()
mail.settings.server = 'smtp.gmail.com:587'  # ou seu servidor SMTP
mail.settings.sender = 'seu_email@gmail.com'
mail.settings.login = 'seu_email@gmail.com:sua_senha_de_app'
mail.settings.tls = True

# Para debug, você pode usar:
# mail.settings.server = 'logging'  # Não envia, apenas registra no console
```

## 2. Modelo de Dados para Fila de E-mail

### Definição da tabela no `models/db.py`

```python
# Tabela para fila de e-mails
db.define_table('email_queue',
    Field('status', default='pending',
          requires=IS_IN_SET(['pending', 'sent', 'failed', 'retry'])),
    Field('recipient_email', 'string', requires=IS_EMAIL()),
    Field('subject', 'string', length=255),
    Field('message', 'text'),
    Field('html_message', 'text'),  # Para e-mails HTML
    Field('record_id', 'integer'),  # ID do registro que gerou o e-mail
    Field('record_table', 'string'), # Nome da tabela do registro
    Field('attempts', 'integer', default=0),
    Field('max_attempts', 'integer', default=3),
    Field('created_on', 'datetime', default=request.now),
    Field('sent_on', 'datetime'),
    Field('error_message', 'text'),
    Field('priority', 'integer', default=1),  # 1=alta, 2=média, 3=baixa
    format='%(subject)s (%(status)s)'
)

# Tabela para templates de e-mail
db.define_table('email_templates',
    Field('name', 'string', unique=True),
    Field('subject', 'string'),
    Field('body_template', 'text'),
    Field('html_template', 'text'),
    Field('description', 'text'),
    format='%(name)s'
)
```

## 3. Módulo de Envio de E-mail

### Criar arquivo `modules/email_manager.py`

```python
# -*- coding: utf-8 -*-

class EmailManager:
    def __init__(self, db, mail):
        self.db = db
        self.mail = mail
    
    def add_to_queue(self, recipient_email, subject, message, 
                     html_message=None, record_id=None, record_table=None,
                     priority=1):
        """
        Adiciona um e-mail à fila
        """
        try:
            email_id = self.db.email_queue.insert(
                recipient_email=recipient_email,
                subject=subject,
                message=message,
                html_message=html_message,
                record_id=record_id,
                record_table=record_table,
                priority=priority,
                status='pending'
            )
            self.db.commit()
            return email_id, True, "E-mail adicionado à fila com sucesso"
        except Exception as e:
            return None, False, str(e)
    
    def generate_email_from_record(self, template_name, record_id, table_name):
        """
        Gera e-mail baseado em um registro do banco de dados
        """
        try:
            # Busca o template
            template = self.db(self.db.email_templates.name == template_name).select().first()
            if not template:
                return None, False, "Template não encontrado"
            
            # Busca o registro
            table = self.db[table_name]
            record = self.db(table.id == record_id).select().first()
            if not record:
                return None, False, "Registro não encontrado"
            
            # Renderiza o template com os dados do registro
            from gluon.template import render
            context = dict(record=record)
            
            subject = render(template.subject, context=context)
            message = render(template.body_template, context=context)
            html_message = None
            if template.html_template:
                html_message = render(template.html_template, context=context)
            
            # Assume que o registro tem um campo email
            recipient_email = record.email if hasattr(record, 'email') else None
            if not recipient_email:
                return None, False, "E-mail do destinatário não encontrado no registro"
            
            return {
                'recipient_email': recipient_email,
                'subject': subject,
                'message': message,
                'html_message': html_message
            }, True, "E-mail gerado com sucesso"
            
        except Exception as e:
            return None, False, str(e)
    
    def send_from_queue(self, limit=10):
        """
        Processa a fila de e-mails
        """
        sent_count = 0
        failed_count = 0
        
        # Busca e-mails pendentes ordenados por prioridade e data
        pending_emails = self.db(
            (self.db.email_queue.status == 'pending') |
            (self.db.email_queue.status == 'retry')
        ).select(
            orderby=[self.db.email_queue.priority, self.db.email_queue.created_on],
            limitby=(0, limit)
        )
        
        for email_record in pending_emails:
            try:
                # Prepara a mensagem
                message = email_record.message
                if email_record.html_message:
                    message = (email_record.message, email_record.html_message)
                
                # Tenta enviar
                success = self.mail.send(
                    to=email_record.recipient_email,
                    subject=email_record.subject,
                    message=message
                )
                
                if success:
                    # Atualiza como enviado
                    email_record.update_record(
                        status='sent',
                        sent_on=self.db.email_queue.sent_on.default
                    )
                    sent_count += 1
                else:
                    # Incrementa tentativas
                    attempts = email_record.attempts + 1
                    if attempts >= email_record.max_attempts:
                        email_record.update_record(
                            status='failed',
                            attempts=attempts,
                            error_message='Número máximo de tentativas excedido'
                        )
                        failed_count += 1
                    else:
                        email_record.update_record(
                            status='retry',
                            attempts=attempts
                        )
                
            except Exception as e:
                # Marca como falha
                attempts = email_record.attempts + 1
                email_record.update_record(
                    status='failed' if attempts >= email_record.max_attempts else 'retry',
                    attempts=attempts,
                    error_message=str(e)
                )
                failed_count += 1
        
        self.db.commit()
        return sent_count, failed_count
    
    def get_queue_status(self):
        """
        Retorna estatísticas da fila
        """
        pending = self.db(self.db.email_queue.status == 'pending').count()
        sent = self.db(self.db.email_queue.status == 'sent').count()
        failed = self.db(self.db.email_queue.status == 'failed').count()
        retry = self.db(self.db.email_queue.status == 'retry').count()
        
        return {
            'pending': pending,
            'sent': sent,
            'failed': failed,
            'retry': retry,
            'total': pending + sent + failed + retry
        }
```

## 4. Controller para Envio de E-mail

### Arquivo `controllers/default.py` (ou outro controller)

```python
# Importa o módulo de e-mail
from email_manager import EmailManager

def enviar_email():
    """
    Página com formulário para gerar e enviar e-mail baseado em registro
    """
    # Assume que você tem o ID do registro na sessão ou como parâmetro
    record_id = request.vars.record_id or session.current_record_id
    
    if not record_id:
        response.flash = "Nenhum registro selecionado"
        redirect(URL('index'))
    
    # Busca templates disponíveis
    templates = db(db.email_templates).select()
    
    form = FORM(
        SELECT([OPTION(t.name, _value=t.name) for t in templates],
               _name='template_name', requires=IS_NOT_EMPTY()),
        INPUT(_type='submit', _value='Enviar E-mail', _class='btn btn-primary')
    )
    
    if form.accepts(request.vars, session):
        email_manager = EmailManager(db, mail)
        
        # Gera o e-mail baseado no registro
        email_data, success, message = email_manager.generate_email_from_record(
            form.vars.template_name, 
            record_id, 
            'sua_tabela'  # Substitua pelo nome real da tabela
        )
        
        if success:
            # Adiciona à fila
            email_id, queue_success, queue_message = email_manager.add_to_queue(
                email_data['recipient_email'],
                email_data['subject'],
                email_data['message'],
                email_data['html_message'],
                record_id,
                'sua_tabela'
            )
            
            if queue_success:
                response.flash = "E-mail adicionado à fila de envio com sucesso!"
            else:
                response.flash = f"Erro ao adicionar à fila: {queue_message}"
        else:
            response.flash = f"Erro ao gerar e-mail: {message}"
    
    return dict(form=form, record_id=record_id)
```

## 5. Interface de Gerenciamento da Fila

### Controller `controllers/admin_email.py`

```python
@auth.requires_membership('admin')  # Apenas administradores
def gerenciar_fila():
    """
    Interface para gerenciar a fila de e-mails
    """
    email_manager = EmailManager(db, mail)
    
    # Estatísticas
    stats = email_manager.get_queue_status()
    
    # Processar ações
    if request.vars.action == 'process_queue':
        sent, failed = email_manager.send_from_queue(limit=20)
        response.flash = f"Processados: {sent} enviados, {failed} falhas"
        redirect(URL('gerenciar_fila'))
    
    elif request.vars.action == 'clear_sent':
        # Remove e-mails enviados há mais de 30 dias
        import datetime
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
        deleted = db((db.email_queue.status == 'sent') & 
                    (db.email_queue.sent_on < cutoff_date)).delete()
        db.commit()
        response.flash = f"{deleted} e-mails antigos removidos"
        redirect(URL('gerenciar_fila'))
    
    # Lista de e-mails na fila
    query = db.email_queue.id > 0
    if request.vars.status:
        query &= db.email_queue.status == request.vars.status
    
    grid = SQLFORM.grid(
        query,
        fields=[db.email_queue.created_on, db.email_queue.recipient_email,
                db.email_queue.subject, db.email_queue.status,
                db.email_queue.attempts],
        orderby=~db.email_queue.created_on,
        paginate=25,
        deletable=auth.has_membership('admin'),
        editable=False,
        create=False,
        csv=False
    )
    
    return dict(stats=stats, grid=grid)

@auth.requires_membership('admin')
def processar_fila_manual():
    """
    Endpoint para processar fila manualmente via AJAX
    """
    email_manager = EmailManager(db, mail)
    sent, failed = email_manager.send_from_queue(limit=10)
    
    return response.json({
        'sent': sent,
        'failed': failed,
        'message': f"Processados: {sent} enviados, {failed} falhas"
    })
```

## 6. Views para Interface

### View `views/default/enviar_email.html`

```html
{{extend 'layout.html'}}

<div class="container">
    <h2>Enviar E-mail</h2>
    
    <div class="row">
        <div class="col-md-8">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Gerar E-mail para Registro #{{=record_id}}</h3>
                </div>
                <div class="panel-body">
                    {{=form}}
                </div>
            </div>
        </div>
    </div>
    </div>

```

### View `views/admin_email/gerenciar_fila.html`

```html
{{extend 'layout.html'}}

<div class="container">
    <h2>Gerenciamento da Fila de E-mails</h2>
    
    <!-- Estatísticas -->
    <div class="row">
        <div class="col-md-12">
            <div class="panel panel-info">
                <div class="panel-heading">
                    <h3 class="panel-title">Estatísticas da Fila</h3>
                </div>
                <div class="panel-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="alert alert-warning">
                                <strong>Pendentes:</strong> {{=stats.pending}}
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="alert alert-success">
                                <strong>Enviados:</strong> {{=stats.sent}}
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="alert alert-danger">
                                <strong>Falhas:</strong> {{=stats.failed}}
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="alert alert-info">
                                <strong>Retry:</strong> {{=stats.retry}}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Ações -->
    <div class="row">
        <div class="col-md-12">
            <div class="btn-group" role="group">
                <a href="{{=URL('gerenciar_fila', vars={'action': 'process_queue'})}}" 
                   class="btn btn-primary">Processar Fila</a>
                <a href="{{=URL('gerenciar_fila', vars={'action': 'clear_sent'})}}" 
                   class="btn btn-warning"
                   onclick="return confirm('Remover e-mails enviados antigos?')">
                   Limpar Enviados</a>
                <button onclick="processQueue()" class="btn btn-info">
                    Processar via AJAX
                </button>
            </div>
        </div>
    </div>
    
    <br>
    
    <!-- Grade de e-mails -->
    <div class="row">
        <div class="col-md-12">
            {{=grid}}
        </div>
    </div>
</div>

<script>
function processQueue() {
    $.ajax({
        url: '{{=URL("processar_fila_manual")}}',
        type: 'POST',
        success: function(data) {
            alert(data.message);
            location.reload();
        },
        error: function() {
            alert('Erro ao processar fila');
        }
    });
}
</script>
```


## 7. Script de Processamento em Background

### Arquivo `private/mail_queue_processor.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import os

# Adiciona o caminho do Web2py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from email_manager import EmailManager

def process_email_queue():
    """
    Processa a fila de e-mails em background
    """
    try:
        email_manager = EmailManager(db, mail)
        sent, failed = email_manager.send_from_queue(limit=50)
        
        if sent > 0 or failed > 0:
            print(f"Processamento completo: {sent} enviados, {failed} falhas")
        
        return sent, failed
        
    except Exception as e:
        print(f"Erro no processamento: {str(e)}")
        return 0, 0

if __name__ == '__main__':
    # Loop principal
    while True:
        try:
            process_email_queue()
            time.sleep(60)  # Processa a cada minuto
        except KeyboardInterrupt:
            print("Processamento interrompido pelo usuário")
            break
        except Exception as e:
            print(f"Erro crítico: {str(e)}")
            time.sleep(300)  # Aguarda 5 minutos em caso de erro
```


## 8. Executar o Processador

Para executar o processador em background:

```bash
# Execute no diretório do Web2py
python web2py.py -S sua_app -M -R applications/sua_app/private/mail_queue_processor.py
```


## 9. Configuração com Scheduler (Alternativa)

### No arquivo `models/scheduler.py`

```python
from gluon.scheduler import Scheduler
from email_manager import EmailManager

def process_email_queue_task():
    """
    Tarefa do scheduler para processar e-mails
    """
    email_manager = EmailManager(db, mail)
    sent, failed = email_manager.send_from_queue(limit=20)
    return f"Enviados: {sent}, Falhas: {failed}"

# Inicializa o scheduler
scheduler = Scheduler(db, tasks=dict(process_emails=process_email_queue_task))

# Agenda a tarefa para executar a cada 5 minutos
scheduler.queue_task('process_emails', repeats=0, period=300)  # 300 segundos = 5 minutos
```


## Recursos Principais Implementados

### Sistema de Fila

- **Adição automática** de e-mails à fila baseada em registros do banco[^2_1]
- **Status de controle** (pendente, enviado, falha, retry)
- **Sistema de prioridades** para diferentes tipos de e-mail
- **Controle de tentativas** com limite máximo configurável


### Geração de E-mail

- **Templates personalizáveis** armazenados no banco de dados[^2_1]
- **Renderização automática** usando dados do registro selecionado
- **Suporte a HTML e texto** simples
- **Validação de dados** antes do envio


### Interface de Gerenciamento

- **Dashboard com estatísticas** da fila de e-mails
- **Processamento manual** via interface web
- **Limpeza automática** de e-mails antigos
- **Visualização detalhada** dos e-mails na fila


### Processamento em Background

- **Script dedicado** para processamento contínuo[^2_1]
- **Integração com Web2py Scheduler** como alternativa
- **Tratamento de erros** robusto
- **Logging** de atividades

Este sistema completo fornece uma solução robusta para envio de e-mails em aplicações Web2py, com controle total sobre a fila de envio e capacidades de gerenciamento administrativo[^2_2][^2_3][^2_4][^2_1].

<div style="text-align: center">⁂</div>

[^2_1]: https://docs.hypernode.com/hypernode-platform/email/how-to-manage-your-email-queue.html

[^2_2]: https://www.web2py.com/books/default/chapter/29/08/emails-and-sms

[^2_3]: https://www.bookstack.cn/read/web2py-manual-6th-en/spilt.1.868a80c3f0930aca.md

[^2_4]: https://www.codingeasypeasy.com/blog/web2py-scheduled-tasks-and-cron-jobs-a-comprehensive-guide-with-examples

[^2_5]: https://stackoverflow.com/questions/30399926/mail-send-feature-in-web2py-for-bounced-email-email-address-that-doesnt-exist/30401904

[^2_6]: https://web2py.com/books/default/chapter/31/08/e-mails-e-sms

[^2_7]: https://stackoverflow.com/questions/20906072/unable-to-send-email-on-main-server-in-web2py

[^2_8]: https://groups.google.com/g/web2py/c/8LN2jGVtOHg

[^2_9]: https://web2py.narkive.com/if0GQq3G/sending-email

[^2_10]: https://www.web2py.com/books/default/chapter/29/13/deployment-recipes?search=response

[^2_11]: https://stackoverflow.com/questions/8668379/asynchronous-background-processes-with-web2py

[^2_12]: https://www.pythonanywhere.com/forums/topic/2129/

[^2_13]: https://stackoverflow.com/questions/52001774/web2py-queued-e-mails-not-send-via-tls-encrypted-smtp-server

[^2_14]: https://groups.google.com/g/web2py/c/2JJir7CRATc

[^2_15]: https://fastapi.tiangolo.com/tutorial/background-tasks/

[^2_16]: https://stackoverflow.com/questions/32084828/web2py-configure-a-scheduler

[^2_17]: https://stackoverflow.com/questions/53261136/web2py-how-i-send-email-automatically-per-day

[^2_18]: https://www.web2py.com/init/default/examples

[^2_19]: https://www.tutorialspoint.com/web2py/web2py_forms_validators.htm

[^2_20]: https://groups.google.com/g/web2py/c/x-F1m4uXXQI

[^2_21]: https://web2py.com/books/default/chapter/32/06/the-database-abstraction-layer

[^2_22]: https://02632110730338943350.googlegroups.com/attach/e12a3e3460030fcc/web2py_manual_789.pdf?part=2\&vt=ANaJVrF87n-GlldoYPpQdVxnolYXOCubq-Wxpt2OdYtcMUYuNN5jO3KSma2k2cF83Zb7Q6hY_TOQO_FhimmKDD0682Seyz4CBF_cNsTEmyEaP29Gqc4Blo4

[^2_23]: https://groups.google.com/g/web2py/c/UxY9-eRmrm8

[^2_24]: https://web2py.com/books/default/chapter/29/06/the-database-abstraction-layer

[^2_25]: https://www.codingeasypeasy.com/blog/dynamic-forms-in-web2py-a-comprehensive-guide-with-examples

[^2_26]: https://www.codingeasypeasy.com/blog/how-to-send-emails-in-web2py-a-comprehensive-guide-with-code-examples

[^2_27]: https://stackoverflow.com/questions/30399926/mail-send-feature-in-web2py-for-bounced-email-email-address-that-doesnt-exist

[^2_28]: https://pypi.org/project/pymailq/

[^2_29]: https://www.codementor.io/@codementorteam/how-to-send-mail-in-python-web2py-rucm500ym

[^2_30]: https://web2py.com/books/default/chapter/29/04/the-core?search=import+module

[^2_31]: https://stackoverflow.com/questions/16351995/web2py-email-authentication

[^2_32]: https://stackoverflow.com/questions/35759073/setting-up-email-notification-with-private-message-on-web2py

[^2_33]: https://groups.google.com/g/web2py/c/n-l0oxc5SwE

[^2_34]: https://groups.google.com/g/web2py/c/IlgdaKX_b2c

[^2_35]: https://www.web2py.com/AlterEgo/default/show/189

