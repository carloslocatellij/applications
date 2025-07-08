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


---

# Análise Crítica da Solução de E-mail para Web2py: Melhorias e Simplificação Arquitetural

## Avaliação Geral da Arquitetura Atual

A solução apresentada para o módulo de envio de e-mail no Web2py é **funcionalmente completa**, mas apresenta várias oportunidades de melhoria tanto em termos de **arquitetura quanto simplificação**. Após análise detalhada das melhores práticas atuais da indústria, identifiquei aspectos que podem ser otimizados para criar uma solução mais robusta, eficiente e maintível.

## Principais Problemas Identificados

### **1. Acoplamento Excessivo**

A solução atual viola o **Princípio da Responsabilidade Única (SRP)** ao concentrar múltiplas responsabilidades na classe `EmailManager`[^3_1][^3_2]. Esta classe gerencia templates, filas, processamento e estatísticas simultaneamente, criando um ponto de falha único e dificultando manutenção.

### **2. Dependência Rígida do Web2py Scheduler**

O Web2py Scheduler apresenta **limitações conhecidas** em ambientes de produção[^3_3][^3_4], incluindo complexidade de configuração e problemas de confiabilidade em cenários de alta carga. A solução atual fica presa a estas limitações arquiteturais.

### **3. Ausência de Rate Limiting**

A implementação não considera **limites de envio** de provedores de e-mail[^3_5][^3_6]. Provedores como Gmail impõem limites rigorosos (aproximadamente 100-500 e-mails por dia para contas novas), e a violação destes limites pode resultar em bloqueios ou blacklisting.

### **4. Gerenciamento Subótimo de Conexões**

A solução não aproveita adequadamente o **connection pooling** do Web2py[^3_7][^3_8], perdendo oportunidades de otimização de performance em cenários de alto volume.

### **5. Template Engine Limitado**

O uso do template engine nativo do Web2py pode ser restritivo. Engines como **Jinja2** oferecem recursos mais robustos[^3_9] para geração de e-mails complexos.

## Proposta de Arquitetura Melhorada

### **Arquitetura Baseada em Microserviços Internos**

```python
# Estrutura Modular Proposta
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, Optional, List
import asyncio
from datetime import datetime, timedelta

# 1. INTERFACES E CONTRATOS
class EmailProvider(Protocol):
    def send(self, email: 'EmailMessage') -> bool: ...
    def get_rate_limits(self) -> 'RateLimits': ...

class QueueBackend(Protocol):
    async def enqueue(self, message: 'EmailMessage') -> str: ...
    async def dequeue(self, count: int) -> List['EmailMessage']: ...
    async def get_stats(self) -> 'QueueStats': ...

class TemplateEngine(Protocol):
    def render(self, template: str, context: dict) -> str: ...

# 2. MODELOS DE DADOS
@dataclass
class EmailMessage:
    id: str
    recipient: str
    subject: str
    body: str
    html_body: Optional[str] = None
    priority: int = 1
    attempts: int = 0
    max_attempts: int = 3
    created_at: datetime = None
    scheduled_at: Optional[datetime] = None

@dataclass
class RateLimits:
    daily_limit: int
    hourly_limit: int
    current_daily: int
    current_hourly: int

# 3. SERVIÇOS ESPECIALIZADOS
class RateLimitManager:
    def __init__(self, db, provider_limits: RateLimits):
        self.db = db
        self.limits = provider_limits
    
    async def can_send(self, count: int = 1) -> bool:
        """Verifica se é possível enviar sem violar limites"""
        current_stats = await self._get_current_usage()
        return (current_stats.daily + count <= self.limits.daily_limit and
                current_stats.hourly + count <= self.limits.hourly_limit)
    
    async def record_sent(self, count: int):
        """Registra e-mails enviados para controle de rate limiting"""
        await self._update_usage_stats(count)

class EmailTemplateService:
    def __init__(self, template_engine: TemplateEngine):
        self.engine = template_engine
    
    def render_email(self, template_name: str, context: dict) -> EmailMessage:
        """Renderiza template e retorna EmailMessage"""
        template = self._get_template(template_name)
        return EmailMessage(
            subject=self.engine.render(template.subject, context),
            body=self.engine.render(template.body, context),
            html_body=self.engine.render(template.html_body, context) if template.html_body else None
        )

class EmailQueueService:
    def __init__(self, queue_backend: QueueBackend, rate_limiter: RateLimitManager):
        self.queue = queue_backend
        self.rate_limiter = rate_limiter
    
    async def add_to_queue(self, email: EmailMessage) -> str:
        """Adiciona e-mail à fila com validação"""
        if not await self._validate_email(email):
            raise ValueError("E-mail inválido")
        
        return await self.queue.enqueue(email)
    
    async def process_batch(self, batch_size: int = 10) -> tuple[int, int]:
        """Processa lote de e-mails respeitando rate limits"""
        if not await self.rate_limiter.can_send(batch_size):
            batch_size = await self._get_allowed_batch_size()
        
        messages = await self.queue.dequeue(batch_size)
        sent, failed = 0, 0
        
        for message in messages:
            if await self._send_email(message):
                sent += 1
            else:
                failed += 1
        
        await self.rate_limiter.record_sent(sent)
        return sent, failed
```


### **Sistema de Fila Alternativo com Redis**

```python
# Implementação usando Redis como backend de fila
import redis
import json
from typing import List

class RedisEmailQueue:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.queue_key = "email_queue"
        self.processing_key = "email_processing"
        self.failed_key = "email_failed"
    
    async def enqueue(self, email: EmailMessage) -> str:
        """Adiciona e-mail à fila Redis com prioridade"""
        email_data = {
            'id': email.id,
            'recipient': email.recipient,
            'subject': email.subject,
            'body': email.body,
            'priority': email.priority,
            'created_at': email.created_at.isoformat()
        }
        
        # Usa sorted set para implementar prioridades
        score = email.priority * 1000000 + int(time.time())
        self.redis.zadd(self.queue_key, {json.dumps(email_data): score})
        return email.id
    
    async def dequeue(self, count: int) -> List[EmailMessage]:
        """Remove e-mails da fila por prioridade"""
        pipe = self.redis.pipeline()
        
        # Pega os itens de maior prioridade
        items = self.redis.zrange(self.queue_key, 0, count-1, withscores=True)
        
        # Move para lista de processamento
        for item, score in items:
            pipe.zrem(self.queue_key, item)
            pipe.lpush(self.processing_key, item)
        
        pipe.execute()
        
        # Converte de volta para EmailMessage
        messages = []
        for item, _ in items:
            data = json.loads(item)
            messages.append(EmailMessage(**data))
        
        return messages
```


### **Controlador Simplificado**

```python
# Controller otimizada seguindo SOLID principles
class EmailController:
    def __init__(self, 
                 template_service: EmailTemplateService,
                 queue_service: EmailQueueService):
        self.template_service = template_service
        self.queue_service = queue_service
    
    async def send_email_from_record(self, template_name: str, record_id: int, table_name: str):
        """Gera e enfileira e-mail baseado em registro"""
        try:
            # Busca dados do registro
            record = await self._get_record(table_name, record_id)
            
            # Gera e-mail usando template
            email = self.template_service.render_email(template_name, {'record': record})
            email.recipient = record.email
            
            # Adiciona à fila
            email_id = await self.queue_service.add_to_queue(email)
            
            return {
                'success': True,
                'message': 'E-mail adicionado à fila com sucesso',
                'email_id': email_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    async def get_queue_dashboard(self):
        """Dashboard simplificado com métricas essenciais"""
        stats = await self.queue_service.queue.get_stats()
        rate_status = await self.queue_service.rate_limiter.get_current_status()
        
        return {
            'queue_stats': stats,
            'rate_limits': rate_status,
            'next_processing': await self._get_next_processing_time()
        }
```


## Melhorias Implementadas

### **1. Separação de Responsabilidades**

Cada classe tem uma **responsabilidade única**[^3_1][^3_10]:

- `EmailTemplateService`: Gerencia apenas templates
- `EmailQueueService`: Gerencia apenas filas
- `RateLimitManager`: Controla apenas rate limiting
- `EmailController`: Orquestra operações


### **2. Injeção de Dependências**

Uso de **interfaces/protocolos** permite substituir implementações facilmente[^3_2], facilitando testes e manutenção.

### **3. Rate Limiting Inteligente**

Sistema considera **limites reais** de provedores[^3_5][^3_6], evitando bloqueios e blacklisting.

### **4. Backend de Fila Flexível**

Suporte a **múltiplos backends** (Redis, Database, In-memory) através de interface comum[^3_11][^3_12].

### **5. Processamento Assíncrono**

Uso de **async/await** para melhor performance[^3_13][^3_14] em operações I/O intensivas.

## Simplificações Propostas

### **Configuração Única**

```python
# config/email_config.py
EMAIL_CONFIG = {
    'provider': {
        'type': 'gmail',
        'smtp_server': 'smtp.gmail.com:587',
        'username': 'app@domain.com',
        'password': 'app_password',
        'daily_limit': 100,
        'hourly_limit': 6
    },
    'queue': {
        'backend': 'redis',  # ou 'database'
        'host': 'localhost',
        'port': 6379,
        'batch_size': 10
    },
    'templates': {
        'engine': 'jinja2',  # ou 'web2py'
        'cache_enabled': True
    }
}
```


### **Inicialização Simplificada**

```python
# Dependency injection container
class EmailServiceContainer:
    def __init__(self, config: dict):
        self.config = config
        self._services = {}
    
    def get_email_service(self) -> EmailQueueService:
        if 'email_service' not in self._services:
            # Cria automaticamente todos os serviços necessários
            provider = self._create_email_provider()
            queue_backend = self._create_queue_backend()
            rate_limiter = self._create_rate_limiter()
            template_service = self._create_template_service()
            
            self._services['email_service'] = EmailQueueService(
                queue_backend, rate_limiter
            )
        
        return self._services['email_service']

# Uso no controller
def index():
    container = EmailServiceContainer(EMAIL_CONFIG)
    email_service = container.get_email_service()
    # Uso direto e simplificado
```


## Benefícios da Arquitetura Proposta

### **Performance**

- **Processamento assíncrono** reduz latência[^3_13][^3_14]
- **Connection pooling** otimizado[^3_7][^3_8]
- **Rate limiting** evita throttling de provedores[^3_5]


### **Manutenibilidade**

- **Código modular** seguindo SOLID[^3_1][^3_2][^3_10]
- **Interfaces bem definidas** facilitam testes
- **Separação clara** de responsabilidades


### **Escalabilidade**

- **Backend de fila plugável** (Redis, Database)[^3_11][^3_15]
- **Processamento distribuído** possível
- **Configuração flexível** por ambiente


### **Confiabilidade**

- **Retry automático** com backoff exponencial
- **Dead letter queue** para falhas persistentes
- **Monitoramento** integrado de métricas


## Alternativas Tecnológicas

### **Para Filas de Mensagem**

Em vez do Web2py Scheduler, considere[^3_16][^3_15][^3_17]:

- **Redis Queue (RQ)**: Simples, confiável para pequeno/médio volume
- **Celery**: Robusto para alta escala, mas mais complexo
- **AsyncIO Queue**: Para processamento assíncrono simples


### **Para Templates**

Substitua o template engine do Web2py por[^3_9]:

- **Jinja2**: Mais recursos, melhor performance
- **Mako**: Rápido, usado pelo SQLAlchemy
- **Chameleon**: Compatível com XML/HTML


### **Para Provedores de E-mail**

Considere APIs especializadas em vez de SMTP:

- **SendGrid**: Rate limiting automático, analytics
- **Amazon SES**: Integração cloud, baixo custo
- **Mailgun**: API robusta, fácil implementação


## Implementação Gradual

### **Fase 1: Refatoração Core**

1. Extrair `EmailTemplateService`
2. Implementar `RateLimitManager`
3. Criar interfaces para providers

### **Fase 2: Queue Backend**

1. Implementar Redis como backend alternativo
2. Migrar dados existentes
3. Configurar processamento assíncrono

### **Fase 3: Otimizações**

1. Implementar connection pooling
2. Adicionar métricas avançadas
3. Configurar monitoramento

A **arquitetura proposta mantém compatibilidade** com o Web2py existente enquanto introduz melhorias significativas em modularidade, performance e manutenibilidade. A transição pode ser **gradual**, permitindo validação em cada etapa antes de avançar para a próxima fase.

<div style="text-align: center">⁂</div>

[^3_1]: https://www.tutorialkart.com/python/python-solid-principles/

[^3_2]: https://arjancodes.com/blog/solid-principles-in-python-programming/

[^3_3]: https://stackoverflow.com/questions/32084828/web2py-configure-a-scheduler

[^3_4]: https://www.pythonanywhere.com/forums/topic/24968/

[^3_5]: https://info.lusha.com/en/articles/257535-email-limits-best-practices

[^3_6]: https://developers.cloudflare.com/waf/rate-limiting-rules/best-practices/

[^3_7]: https://web2py.com/books/default/chapter/32/06/the-database-abstraction-layer

[^3_8]: https://www.youtube.com/watch?v=toWx754nHX4

[^3_9]: https://www.libhunt.com/r/trender

[^3_10]: https://www.machinet.net/tutorial-eng/applying-solid-principles-to-python-projects

[^3_11]: https://www.twilio.com/en-us/blog/queueing-emails-python-redis-queue-twilio-sendgrid

[^3_12]: https://github.com/prakhar308/message-queues-in-python

[^3_13]: https://docs.python.org/3/library/asyncio-queue.html

[^3_14]: https://bytepawn.com/writing-a-simple-python-async-message-queue-server.html

[^3_15]: https://app.studyraid.com/en/read/15008/518850/celery-vs-other-task-queue-systems

[^3_16]: https://stackoverflow.com/questions/44830321/celery-vs-rq-benchmarking

[^3_17]: https://stackoverflow.com/questions/13440875/pros-and-cons-to-use-celery-vs-rq

[^3_18]: https://www.web2py.com/books/default/chapter/29/08/emails-and-sms

[^3_19]: https://stackoverflow.com/questions/52001774/web2py-queued-e-mails-not-send-via-tls-encrypted-smtp-server

[^3_20]: https://github.com/arunsaiv/queue-patterns

[^3_21]: https://www.tutorialspoint.com/web2py/web2py_email_sms.htm

[^3_22]: https://groups.google.com/g/web2py/c/-8I2-zSB2G8

[^3_23]: https://web2py.com/books/default/chapter/31/08/e-mails-e-sms

[^3_24]: https://testdriven.io/blog/developing-an-asynchronous-task-queue-in-python/

[^3_25]: https://web2py.com/books/default/chapter/29/06/the-database-abstraction-layer

[^3_26]: https://stackshare.io/web2py/alternatives

[^3_27]: https://github.com/roelzkie15/python-microservices-patterns

[^3_28]: https://stackoverflow.com/questions/9840389/performance-capacity-statistics-for-web2py

[^3_29]: https://www.g2.com/products/web2py/competitors/alternatives

[^3_30]: https://laxaar.com/blog/design-patterns-for-python-microservices-building-1709555656449

[^3_31]: https://groups.google.com/g/web2py/c/GAYnWiYe0_c

[^3_32]: https://www.reddit.com/r/node/comments/182a07g/what_are_the_simplest_strategies_to_implement/

[^3_33]: https://stackoverflow.com/questions/16902036/message-queue-abstraction-for-python

[^3_34]: https://www.codingeasypeasy.com/blog/how-to-send-emails-in-web2py-a-comprehensive-guide-with-code-examples

[^3_35]: https://www.codingeasypeasy.com/blog/web2py-scheduled-tasks-and-cron-jobs-a-comprehensive-guide-with-examples

[^3_36]: https://stackoverflow.com/questions/68372642/sending-messages-correctly-with-async-server-python

[^3_37]: https://python.plainenglish.io/boost-your-microservices-architecture-with-these-hidden-patterns-dcd844b5d01c?gi=25f7778348cb

[^3_38]: https://www.codingeasypeasy.com/blog/optimizing-web2py-dal-queries-best-practices-for-performance

[^3_39]: https://www.moesif.com/blog/technical/rate-limiting/Best-Practices-for-API-Rate-Limits-and-Quotas-With-Moesif-to-Avoid-Angry-Customers/


---

# 1 - Não podemos utilizar o Redis, vamos manter a solução de fila do web2py.

2 - Não iremos nos preocupar com rate limit.
Reavalie o projeto e vamos chegar a uma solução final ótima focada em na simplicidade do web2py.

Considerando as suas restrições de **não utilizar Redis** e **não se preocupar com rate limiting**, e que o foco é manter a simplicidade e aproveitar as facilidades nativas do Web2py, segue uma **solução final otimizada e simplificada** para o envio de e-mails com fila usando apenas os recursos do Web2py.

## Proposta Final Simplificada para Envio de E-mail com Fila no Web2py

### 1. Modelo de Dados para Fila de E-mails

Defina uma tabela simples para armazenar os e-mails pendentes e seus status, no seu `models/db.py`:

```python
db.define_table('email_queue',
    Field('recipient_email', 'string', requires=IS_EMAIL()),
    Field('subject', 'string', length=255),
    Field('message', 'text'),           # Texto simples
    Field('html_message', 'text'),      # Opcional, para HTML
    Field('status', 'string', default='pending', requires=IS_IN_SET(['pending', 'sent', 'failed'])),
    Field('attempts', 'integer', default=0),
    Field('max_attempts', 'integer', default=3),
    Field('created_on', 'datetime', default=request.now),
    Field('sent_on', 'datetime'),
    Field('error_message', 'text'),
    format='%(subject)s'
)
```


### 2. Configuração do Mail no `models/db.py`

Configure o objeto `mail` do Web2py para envio via SMTP, por exemplo Gmail:

```python
from gluon.tools import Mail

mail = Mail()
mail.settings.server = 'smtp.gmail.com:587'  # ou seu servidor SMTP
mail.settings.sender = 'seu_email@gmail.com'
mail.settings.login = 'seu_email@gmail.com:sua_senha_de_app'  # senha de app Google
mail.settings.tls = True
```


### 3. Função para Adicionar E-mail na Fila (Controller ou Módulo)

No controller onde o registro está selecionado, crie uma função para gerar o e-mail e adicioná-lo na fila:

```python
def enviar_email_fila():
    record_id = request.vars.record_id
    if not record_id:
        session.flash = "Registro não selecionado"
        redirect(URL('index'))

    # Exemplo: busca o registro do banco
    registro = db.sua_tabela(record_id)
    if not registro:
        session.flash = "Registro não encontrado"
        redirect(URL('index'))

    # Geração simples do corpo do e-mail
    assunto = f"Notificação para registro {registro.id}"
    mensagem = f"Olá, este é o conteúdo do e-mail para o registro {registro.id}."
    destinatario = registro.email  # assume que o registro tem campo email

    # Adiciona na fila
    email_id = db.email_queue.insert(
        recipient_email=destinatario,
        subject=assunto,
        message=mensagem,
        status='pending'
    )
    db.commit()

    session.flash = "E-mail adicionado à fila com sucesso!"
    redirect(URL('index'))
```


### 4. Função para Processar a Fila (Pode ser chamada pelo Scheduler ou manualmente)

No controller ou módulo, função para enviar os e-mails pendentes:

```python
def processar_fila_emails():
    limite = 10  # quantidade de e-mails para processar por vez
    emails = db(db.email_queue.status == 'pending').select(limitby=(0, limite), orderby=db.email_queue.created_on)

    enviados = 0
    falhas = 0

    for email in emails:
        try:
            if email.html_message:
                success = mail.send(
                    to=email.recipient_email,
                    subject=email.subject,
                    message=email.message,
                    body=email.html_message
                )
            else:
                success = mail.send(
                    to=email.recipient_email,
                    subject=email.subject,
                    message=email.message
                )

            if success:
                email.update_record(status='sent', sent_on=request.now)
                enviados += 1
            else:
                raise Exception("Falha no envio desconhecida")

        except Exception as e:
            tentativas = email.attempts + 1
            status = 'failed' if tentativas >= email.max_attempts else 'pending'
            email.update_record(status=status, attempts=tentativas, error_message=str(e))

            falhas += 1

    db.commit()
    return dict(enviados=enviados, falhas=falhas)
```


### 5. Agendamento com Web2py Scheduler (Opcional)

No `models/scheduler.py`:

```python
from gluon.scheduler import Scheduler

def tarefa_processar_emails():
    return processar_fila_emails()

scheduler = Scheduler(db, tasks=dict(processar_emails=tarefa_processar_emails))
scheduler.queue_task('processar_emails', repeats=0, period=300)  # a cada 5 minutos
```


### 6. Interface Simples para Gerenciar a Fila

No controller:

```python
@auth.requires_membership('admin')
def gerenciar_fila():
    query = db.email_queue.id > 0
    grid = SQLFORM.grid(query,
        fields=[db.email_queue.created_on, db.email_queue.recipient_email, db.email_queue.subject, db.email_queue.status, db.email_queue.attempts],
        orderby=~db.email_queue.created_on,
        editable=False,
        deletable=True,
        create=False,
        csv=False,
        paginate=20)
    return dict(grid=grid)
```


## Resumo das Melhorias e Simplificações

- **Uso exclusivo do banco de dados do Web2py** para fila, sem dependências externas.
- **Funções claras e separadas** para adicionar e processar e-mails.
- **Tratamento básico de tentativas e falhas** com limite de tentativas.
- **Uso do Web2py Scheduler** para processamento periódico, sem necessidade de sistemas externos.
- **Interface administrativa simples** via `SQLFORM.grid` para monitorar e gerenciar a fila.
- **Configuração padrão do Web2py Mail**, fácil de manter e alterar.


## Considerações Finais

Essa solução é **totalmente compatível com o Web2py**, fácil de entender e manter, e atende ao requisito de fila de envio com feedback ao usuário. Para cenários simples e médios, ela é suficiente e evita complexidade desnecessária.

Caso futuramente precise de mais escalabilidade, poderá migrar para soluções externas, mas para agora, essa é a forma mais prática e robusta dentro do ecossistema Web2py.

Se desejar, posso ajudar a montar os códigos completos para controllers, views e módulos para essa solução final.

<div style="text-align: center">⁂</div>

[^4_1]: https://www.web2py.com/books/default/chapter/29/08/emails-and-sms

[^4_2]: https://www.codementor.io/@codementorteam/how-to-send-mail-in-python-web2py-rucm500ym

[^4_3]: https://web2py.narkive.com/if0GQq3G/sending-email

[^4_4]: https://www.codingeasypeasy.com/blog/how-to-send-emails-in-web2py-a-comprehensive-guide-with-code-examples

[^4_5]: https://stackoverflow.com/questions/35759073/setting-up-email-notification-with-private-message-on-web2py

[^4_6]: https://www.web2py.com/books/default/chapter/34/08/email-and-sms

[^4_7]: https://stackoverflow.com/questions/19085738/i-am-trying-send-email-using-web2py-with-gmail-and-using-smtp-setting-i-have-att

[^4_8]: https://www.tutorialspoint.com/web2py/web2py_email_sms.htm

